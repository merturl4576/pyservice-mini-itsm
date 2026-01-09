"""
Remote Support Admin
PyService Mini-ITSM Platform
"""

from django.contrib import admin
from .models import RemoteSupportSession, SessionMessage


class SessionMessageInline(admin.TabularInline):
    model = SessionMessage
    extra = 0
    readonly_fields = ['sender', 'message', 'created_at']


@admin.register(RemoteSupportSession)
class RemoteSupportSessionAdmin(admin.ModelAdmin):
    list_display = ['session_code', 'subject', 'requester', 'technician', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['session_code', 'subject', 'requester__username', 'technician__username']
    readonly_fields = ['session_code', 'created_at', 'accepted_at', 'completed_at']
    inlines = [SessionMessageInline]


@admin.register(SessionMessage)
class SessionMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'sender', 'message', 'created_at']
    list_filter = ['created_at']
