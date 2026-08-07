from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Chat, Message
from django.db.models import Q
from channels.db import database_sync_to_async
import json
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .utils import get_or_create_chat


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.group_name = f"chat_{self.chat_id}"

        allowed = await self._is_chat_member(user.id, self.chat_id)
        if not allowed:
            await self.close()
            return
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    @database_sync_to_async
    def _is_chat_member(self, user_id, chat_id):
        return (
            Chat.objects.filter(id=chat_id)
            .filter(Q(user1_id=user_id) | Q(user2_id=user_id))
            .exists()
        )

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        user = self.scope["user"]
        payload = json.loads(text_data)
        text = payload.get("message")
        saved = await self._save_message(self.chat_id, user.id, text)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "message": saved["text"],
                "sender_id": saved["sender_id"],
                "sender_username": saved["sender_username"],
                "created_at": saved["created_at"],
            },
        )

    @database_sync_to_async
    def _save_message(self, chat_id, sender_id, text_message):
        sender = get_object_or_404(get_user_model(), pk=sender_id)
        chat = Chat.objects.get(pk=chat_id)
        receiver = chat.user2

        if sender.id == chat.user2.id:
            receiver = chat.user1

        message = Message.objects.create(
            chat_id=chat.id, sender=sender, receiver=receiver, text=text_message
        )

        now = timezone.now()
        chat.save()
        chat.last_message = now
        chat.save(update_fields=["last_message"])
        return {
            "text": message.text,
            "sender_id": sender_id,
            "sender_username": sender.get_username(),
            "created_at": now.isoformat(),
        }

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "sender_id": event["sender_id"],
                    "sender_username": event["sender_username"],
                    "created_at": event["created_at"],
                }
            )
        )
