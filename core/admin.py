from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import SnapUser, Message, FriendRequest,Chat


@admin.register(SnapUser)
class SnapUserAdmin(UserAdmin):
    pass


admin.site.register(Message)
admin.site.register(FriendRequest)
admin.site.register(Chat)