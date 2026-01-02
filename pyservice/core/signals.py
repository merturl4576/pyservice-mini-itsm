"""
Core Signals - Automatic Activity Logging
PyService Mini-ITSM Platform
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from incidents.models import Incident
from service_requests.models import ServiceRequest
from cmdb.models import Asset
from .models import ActivityLog


def get_client_ip(request):
    """Get client IP from request."""
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    return None


@receiver(post_save, sender=Incident)
def log_incident_changes(sender, instance, created, **kwargs):
    """Log incident creation and updates."""
    if created:
        ActivityLog.log(
            user=instance.caller,
            action='create',
            obj=instance,
            details=f"Created incident: {instance.title}"
        )
    else:
        # Check for state changes
        if hasattr(instance, '_original_state'):
            if instance._original_state != instance.state:
                if instance.state == 'resolved':
                    ActivityLog.log(
                        user=instance.assigned_to,
                        action='resolve',
                        obj=instance,
                        details=f"Resolved incident: {instance.resolution_notes or ''}"
                    )
                elif instance.state == 'escalated':
                    ActivityLog.log(
                        user=instance.assigned_to,
                        action='escalate',
                        obj=instance,
                        details="Escalated to next level"
                    )
        
        # Check for assignment changes
        if hasattr(instance, '_original_assigned_to'):
            if instance._original_assigned_to != instance.assigned_to and instance.assigned_to:
                if instance._original_assigned_to is None:
                    ActivityLog.log(
                        user=instance.assigned_to,
                        action='claim',
                        obj=instance,
                        details=f"Claimed by {instance.assigned_to}"
                    )
                else:
                    ActivityLog.log(
                        user=instance.assigned_to,
                        action='assign',
                        obj=instance,
                        details=f"Assigned to {instance.assigned_to}"
                    )


@receiver(post_save, sender=ServiceRequest)
def log_request_changes(sender, instance, created, **kwargs):
    """Log service request changes."""
    if created:
        ActivityLog.log(
            user=instance.requester,
            action='create',
            obj=instance,
            details=f"Created request: {instance.title}"
        )
    else:
        if hasattr(instance, '_original_state'):
            if instance._original_state != instance.state:
                if instance.state == 'approved':
                    ActivityLog.log(
                        user=instance.approved_by if hasattr(instance, 'approved_by') else None,
                        action='approve',
                        obj=instance,
                        details="Request approved"
                    )
                elif instance.state == 'rejected':
                    ActivityLog.log(
                        user=instance.approved_by if hasattr(instance, 'approved_by') else None,
                        action='reject',
                        obj=instance,
                        details="Request rejected"
                    )
                elif instance.state == 'completed':
                    ActivityLog.log(
                        user=instance.assigned_to,
                        action='resolve',
                        obj=instance,
                        details="Request completed"
                    )


@receiver(post_save, sender=Asset)
def log_asset_changes(sender, instance, created, **kwargs):
    """Log asset changes."""
    if created:
        ActivityLog.log(
            user=instance.created_by,
            action='create',
            obj=instance,
            details=f"Created asset: {instance.name}"
        )
    else:
        # Log assignment changes
        if instance.assigned_to:
            ActivityLog.log(
                user=instance.assigned_to,
                action='assign',
                obj=instance,
                details=f"Assigned to {instance.assigned_to}"
            )
