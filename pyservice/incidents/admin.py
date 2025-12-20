"""
Incident Admin Configuration
PyService Mini-ITSM Platform
"""

from django.contrib import admin
from .models import Incident


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['number', 'title', 'priority', 'state', 'caller', 'assigned_to', 'due_date', 'sla_breached']
    list_filter = ['state', 'priority', 'impact', 'urgency', 'sla_breached']
    search_fields = ['number', 'title', 'description']
    ordering = ['priority', '-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['number', 'priority', 'due_date', 'sla_breached', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Incident Details', {
            'fields': ('number', 'title', 'description')
        }),
        ('People', {
            'fields': ('caller', 'assigned_to')
        }),
        ('Classification', {
            'fields': ('impact', 'urgency', 'priority')
        }),
        ('Status', {
            'fields': ('state', 'due_date', 'sla_breached')
        }),
        ('Resolution', {
            'fields': ('resolution_notes', 'resolved_at'),
            'classes': ['collapse']
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    actions = ['assign_to_me', 'mark_resolved']
    
    def assign_to_me(self, request, queryset):
        queryset.update(assigned_to=request.user, state='in_progress')
    assign_to_me.short_description = "Assign selected incidents to me"
    
    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(state='resolved', resolved_at=timezone.now())
    mark_resolved.short_description = "Mark selected incidents as Resolved"
