from django.urls import path
from .views import register_view, login_view, home, search_view, send_invite,chat_details_view

urlpatterns = [
    path("register/", register_view, name="register-user"),
    path("login/", login_view, name="login-user"),
    path("", home, name="home"),
    path("search/", search_view, name="search-users"),
    path("send-invite/<int:id>", send_invite, name="send-invite"),
    path("chat-details/<int:id>", chat_details_view, name="chat-details"),
]
