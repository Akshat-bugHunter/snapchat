from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class SnapUser(AbstractUser):
    avatar = models.ImageField(upload_to="avatar", default="snaps/default.jpg")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)


# Create your models here.
class FriendRequest(models.Model):

    class StatusChoice(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"

    from_user = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE, related_name="sent_requests"
    )
    to_user = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE, related_name="received_requests"
    )

    status = models.CharField(
        max_length=10, choices=StatusChoice.choices, default=StatusChoice.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("from_user", "to_user")

    def __str__(self):
        return f"{self.from_user} -> {self.to_user}: {self.status}"


class Chat(models.Model):

    class Mode(models.TextChoices):
        KEEP = "keep", "Keep"
        ON_CLOSE = "on_close", "ON_CLOSE"
        AFTER_24HR = "after_24_hr", "AFTER_24_HR"

    user1 = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE, related_name="user1_chats"
    )
    user2 = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE, related_name="user2_chats"
    )
    mode = models.CharField(max_length=16, choices=Mode.choices, default=Mode.ON_CLOSE)
    last_message = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    streak = models.PositiveIntegerField(default=0, editable=False)
    streak_updated_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"Chat: {self.user1} <-> {self.user2}"


class Message(models.Model):
    chat = models.ForeignKey(to=Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE, related_name="recieved_messages"
    )
    is_system = models.BooleanField(default=False)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="snaps", null=True, blank=True)

    def __str__(self):
        return f"Message {self.sender} -> {self.receiver}"
