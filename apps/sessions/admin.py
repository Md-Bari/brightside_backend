from django.contrib import admin

from .models import ChatSession


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "email", "status", "created_at", "updated_at", "ended_at")
    list_filter = ("status",)
    search_fields = ("session_id", "user__email")
