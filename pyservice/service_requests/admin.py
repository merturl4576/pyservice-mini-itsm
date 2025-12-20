"""
Service Request Admin Configuration
PyService Mini-ITSM Platform
"""

from django.contrib import admin
from .models import ServiceRequest


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['number', 'title', 'request_type', 'state', 'requester', 'assigned_to', 'created_at']
    list_filter = ['state', 'request_type']
    search_fields = ['number', 'title', 'description']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['number', 'created_at', 'updated_at', 'approved_at', 'rejected_at', 'completed_at']
    
    fieldsets = (
        ('Request Details', {
            'fields': ('number', 'title', 'description', 'request_type')
        }),
        ('People', {
            'fields': ('requester', 'approver', 'assigned_to')
        }),
        ('Status', {
            'fields': ('state',)
        }),
        ('Approval', {
            'fields': ('approval_notes', 'approved_at', 'rejected_at'),
            'classes': ['collapse']
        }),
        ('Fulfillment', {
            'fields': ('fulfillment_notes', 'completed_at'),
            'classes': ['collapse']
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        from django.utils import timezone
        queryset.filter(state='awaiting_approval').update(
            state='approved',
            approver=request.user,
            approved_at=timezone.now()
        )
    approve_requests.short_description = "Approve selected requests"
    
    def reject_requests(self, request, queryset):
        from django.utils import timezone
        queryset.filter(state='awaiting_approval').update(
            state='rejected',
            approver=request.user,
            rejected_at=timezone.now()
        )
    reject_requests.short_description = "Reject selected requests"
