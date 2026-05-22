from django.contrib import admin
from chat.models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("id", "chat_listing", "buyer", "seller", "created_at")
    search_fields = (
        "chat_listing__title",
        "buyer__username",
        "buyer__email",
        "seller__username",
        "seller__email",
    )
    ordering = ("-created_at",)
    list_filter = ("created_at", "updated_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "sender", "is_read", "created_at")
    search_fields = ("room__listing__title", "sender__username", "text")
    ordering = ("-created_at",)
    list_filter = ("is_read", "created_at", "updated_at")
