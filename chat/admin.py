from django.contrib import admin
from .models import Chat, ChatMembership, Message


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", "is_group", "name", "created_at")
    search_fields = ("name", "id")


@admin.register(ChatMembership)
class ChatMembershipAdmin(admin.ModelAdmin):
    list_display = ("chat", "user", "joined_at")
    list_filter = ("chat", "user")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "sender", "created_at")
    search_fields = ("content",)
    list_filter = ("chat", "sender")
