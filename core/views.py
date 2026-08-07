from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout, get_user_model
import json
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from typing import List
from django.utils import timezone
from .models import Message, FriendRequest, SnapUser, Chat
from . import forms
import base64
from .utils import are_friends, get_friends, get_or_create_chat, update_streak
from django.db import IntegrityError

# Create your views here.


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = forms.RegisterForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("home")

    return render(request, "accounts/register.html", {"form": form})


# @require_http_methods(["GET", "POST"])
# def login_view(request):
#     if request.user.is_authenticated:
#         return redirect("home")


#     form = forms.LoginForm(request, data=request.POST or None)
#     if request.method == "POST" and form.is_valid():
#         login(request, form.get_user())
#         return redirect("home")
#     return render(request, "accounts/login.html", {"form": form})
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = forms.LoginForm(request, data=request.POST or None)

    if request.method == "POST":

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")

    return render(request, "accounts/login.html", {"form": form})


@login_required
def home(request):
    friends = get_friends(request.user)
    locationform = forms.LocationForm()

    chat_list = []

    for friend in friends:
        chat = get_or_create_chat(request.user, friend)

        message = chat.messages.order_by("-created_at").first()

        if message is None:
            last_message = "Say Hi"
        elif message.image:
            last_message = "New Snap"
        else:
            last_message = message.text

        chat_list.append((friend, chat, last_message))

    chat_list.sort(key=lambda row: row[1].last_message, reverse=True)

    return render(
        request,
        "pages/chat.html",
        {
            "chats": chat_list,
            "locationform": locationform,
        },
    )


@login_required
def chat_details_view(request, id):
    chat = get_object_or_404(Chat, pk=id)
    messages = chat.messages.all().order_by("created_at")
    update_streak(chat)

    friend = chat.user1
    if chat.user1 == request.user:
        friend = chat.user2

    if chat.mode == chat.Mode.ON_CLOSE:
        Message.objects.filter(chat=chat, receiver=request.user, sender=friend).delete()

    elif chat.mode == chat.Mode.AFTER_24HR:
        now = timezone.now()
        grace_period = now() - timezone.timedelta(days=1)
        messages = messages.filter(created_at__gte=grace_period)

    return render(
        request,
        "pages/chat-details.html",
        {
            "friend": friend,
            "messages": messages,
            "chat_id": id,
            "chat": chat,
        },
    )


@login_required
def search_view(request):
    unique_friends = []
    sent = []
    received = []
    User = get_user_model()
    query = request.GET.get("q", "")
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)

    queryset = FriendRequest.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user)
    )
    friends = queryset.filter(status=FriendRequest.StatusChoice.ACCEPTED)
    pending_request = queryset.filter(status=FriendRequest.StatusChoice.PENDING)

    for friend in friends:
        if request.user == friend.from_user:
            unique_friends.append(friend.to_user.id)
        else:
            unique_friends.append(friend.from_user.id)

    for req in pending_request:
        if request.user == req.from_user:
            sent.append(req.to_user.id)
        else:
            received.append(req.from_user.id)

    return render(
        request,
        "pages/search.html",
        {"users": users, "friends": unique_friends, "sent": sent, "received": received},
    )


@require_http_methods(["POST"])
@login_required
def send_invite(request, id):
    if id == request.user.id:
        return redirect("search-users")
    to_user = get_object_or_404(get_user_model(), id=id)

    try:
        FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    except IntegrityError:
        return redirect("search-users")
    return redirect("search-users")


@require_http_methods(["POST"])
def send_message(request, id):
    friend = get_object_or_404(get_user_model(), pk=id)

    if not are_friends(request.user, friend):
        return redirect("home")

    message = request.POST.get("message")
    snap = request.FILES.get("image")
    if message or snap:
        chat = get_or_create_chat(request.user, friend)

        Message.objects.create(
            chat=chat, sender=request.user, receiver=friend, text=message, image=snap
        )
        update_streak(chat)
    return redirect("chat-details", id=chat.id)


@login_required
@require_http_methods(["GET"])
def friend_request_list_view(request):
    friend_requests = FriendRequest.objects.filter(
        status=FriendRequest.StatusChoice.PENDING, to_user=request.user
    )
    return render(
        request, "pages/friend-request.html", {"friend_requests": friend_requests}
    )


@login_required
@require_http_methods(["POST"])
def accept_friend_request(request, id):
    req = get_object_or_404(FriendRequest, pk=id)
    if req.to_user == request.user and req.status == FriendRequest.StatusChoice.PENDING:
        req.status = FriendRequest.StatusChoice.ACCEPTED
        req.save()
    return redirect("friend-requests")


@login_required
def map_view(request):

    friends = SnapUser.objects.exclude(id=request.user.id)

    friend_data = []

    for friend in friends:

        friend_data.append(
            {
                "username": friend.username,
                "latitude": friend.latitude,
                "longitude": friend.longitude,
                "avatar": friend.avatar.url,
            }
        )

    return render(request, "pages/map.html", {"friends": friend_data})


@login_required
@require_http_methods(["POST"])
def update_location(request):
    data = json.loads(request.body)

    request.user.latitude = data["latitude"]
    request.user.longitude = data["longitude"]
    request.user.save()

    return JsonResponse({"success": True})


def profile_view(request):
    return render(request, "accounts/profile.html")


@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def camera_view(request):
    friends = get_friends(request.user)
    selected_friend_id = request.GET.get("friend")

    try:
        selected_friend_id = int(selected_friend_id) if selected_friend_id else None
    except (TypeError, ValueError):
        selected_friend_id = None

    return render(
        request,
        "pages/camera.html",
        {"friends": friends, "selected_friend_id": selected_friend_id},
    )


@login_required
@require_http_methods(["POST"])
def send_snap_view(request):
    image_data = request.POST.get("image_data")
    friend_ids = request.POST.getlist("friend_ids")

    if not image_data or not friend_ids:
        return redirect("camera")

    image_text = image_data.split(",")[1]
    image_bytes = base64.b64decode(image_text)

    for friend_id in friend_ids:
        friend = get_object_or_404(get_user_model(), pk=friend_id)
        if not are_friends(request.user, friend):

            continue

        chat = get_or_create_chat(request.user, friend)
        Message.objects.create(
            chat=chat,
            sender=request.user,
            receiver=friend,
            image=ContentFile(image_bytes, name="snap.jpg"),
        )
        chat.last_message = timezone.now()
        chat.save()
        update_streak(chat=chat)
        last_chat = chat
        if last_chat and len(friend_ids) == 1:
            return redirect("chat-details", id=last_chat.id)
    return redirect("home")
