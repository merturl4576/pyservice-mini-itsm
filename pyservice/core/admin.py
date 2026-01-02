from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'object_repr', 'created_at']
    list_filter = ['action', 'content_type', 'created_at']
    search_fields = ['object_repr', 'details', 'user__username']
    readonly_fields = ['user', 'action', 'content_type', 'object_id', 'object_repr', 'details', 'ip_address', 'created_at']
    ordering = ['-created_at']
