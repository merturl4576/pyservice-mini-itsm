"""
Core App - Activity Logs
PyService Mini-ITSM Platform
Audit trail for all model changes
"""

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ActivityLog(models.Model):
    """Audit trail for model changes."""
    
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('assign', 'Assigned'),
        ('claim', 'Claimed'),
        ('resolve', 'Resolved'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('escalate', 'Escalated'),
        ('comment', 'Commented'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activity_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    object_repr = models.CharField(max_length=200)  # String representation
    details = models.TextField(blank=True)  # JSON or text details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
    
    def __str__(self):
        return f"{self.user} {self.get_action_display()} {self.object_repr}"
    
    @classmethod
    def log(cls, user, action, obj, details='', ip_address=None):
        """Create an activity log entry."""
        content_type = ContentType.objects.get_for_model(obj)
        return cls.objects.create(
            user=user,
            action=action,
            content_type=content_type,
            object_id=obj.pk,
            object_repr=str(obj)[:200],
            details=details,
            ip_address=ip_address
        )
    
    @classmethod
    def get_for_object(cls, obj, limit=20):
        """Get activity logs for a specific object."""
        content_type = ContentType.objects.get_for_model(obj)
        return cls.objects.filter(
            content_type=content_type,
            object_id=obj.pk
        )[:limit]
