"""
Notifications App
PyService Mini-ITSM Platform
Provides in-app notifications and email notification functionality
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    """In-app notification model."""
    
    NOTIFICATION_TYPES = [
        ('incident_assigned', 'Incident Assigned'),
        ('incident_resolved', 'Incident Resolved'),
        ('incident_escalated', 'Incident Escalated'),
        ('sla_warning', 'SLA Warning'),
        ('sla_breached', 'SLA Breached'),
        ('request_submitted', 'Request Submitted'),
        ('request_approved', 'Request Approved'),
        ('request_rejected', 'Request Rejected'),
        ('request_completed', 'Request Completed'),
        ('asset_assigned', 'Asset Assigned'),
        ('general', 'General'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, default='general')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
    
    @classmethod
    def create_notification(cls, user, notification_type, title, message, link=''):
        """Create a notification for a user."""
        return cls.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link
        )
    
    @classmethod
    def get_unread_count(cls, user):
        """Get count of unread notifications for a user."""
        return cls.objects.filter(user=user, is_read=False).count()
    
    @classmethod
    def get_recent_notifications(cls, user, limit=10):
        """Get recent notifications for a user."""
        return cls.objects.filter(user=user)[:limit]
