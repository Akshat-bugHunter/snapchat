from django.urls import path
from .views import register_view, login_view, home, search_view, send_invite,chat_details_view,send_message, friend_request_list_view, accept_friend_request

urlpatterns = [
    path("register/", register_view, name="register-user"),
    path("login/", login_view, name="login-user"),
    path("", home, name="home"),
    path("search/", search_view, name="search-users"),
    path("send-invite/<int:id>", send_invite, name="send-invite"),
    path("chat-details/<int:id>", chat_details_view, name="chat-details"),
    path("send-message/<int:id>", send_message, name="send-message"),
    path("friend-requests/", friend_request_list_view, name="friend-requests"),
    path("accept-friend-request/<int:id>", accept_friend_request, name="accept-friend"),
]
