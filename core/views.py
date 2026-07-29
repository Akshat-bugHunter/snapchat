from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout, get_user_model

from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Message, FriendRequest
from . import forms

from django.db import IntegrityError


# Create your views here.


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = forms.RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("home")
    return render(request, "accounts/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = forms.LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("home")
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


def home(request):
    return render(request, "pages/chat.html")


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
def send_invite(request,id):
    if id==request.user.id:
        return redirect("search-users")
    to_user=get_object_or_404(get_user_model(),id=id)

    try:
        FriendRequest.objects.create(from_user=request.user,to_user=to_user)
    except IntegrityError:
        return redirect("search-users")
    return redirect("search-users")