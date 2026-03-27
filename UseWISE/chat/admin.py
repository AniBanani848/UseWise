from django.contrib import admin

from .models import ChatMessage, Friendship


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ("id", "from_user", "to_user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("from_user__email", "to_user__email")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "friendship", "sender", "created_at")
    list_filter = ("created_at",)
    search_fields = ("sender__email", "body")

