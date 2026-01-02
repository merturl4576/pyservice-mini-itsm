"""
Notification Signals
PyService Mini-ITSM Platform
Automatic notification creation on model changes
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from incidents.models import Incident
from service_requests.models import ServiceRequest
from .models import Notification


def send_notification_email(user, subject, message):
    """Send email notification (console backend for development)."""
    if user.email:
        try:
            send_mail(
                subject=f"[PyService] {subject}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass  # Silently fail in development


@receiver(post_save, sender=Incident)
def incident_notification(sender, instance, created, **kwargs):
    """Create notifications when incidents are modified."""
    
    if created:
        # Notify IT staff about new incidents (if assigned)
        if instance.assigned_to:
            Notification.create_notification(
                user=instance.assigned_to,
                notification_type='incident_assigned',
                title=f"New Incident Assigned: {instance.number}",
                message=f"You have been assigned to incident '{instance.title}' with priority {instance.get_priority_display()}.",
                link=f"/incidents/{instance.pk}/"
            )
            send_notification_email(
                instance.assigned_to,
                f"Incident Assigned: {instance.number}",
                f"You have been assigned to incident '{instance.title}'.\n\nPriority: {instance.get_priority_display()}\nDescription: {instance.description[:200]}"
            )
    else:
        # Check for state changes
        if hasattr(instance, '_original_state') and instance._original_state != instance.state:
            # Notify caller when incident is resolved
            if instance.state == 'resolved' and instance.caller:
                Notification.create_notification(
                    user=instance.caller,
                    notification_type='incident_resolved',
                    title=f"Incident Resolved: {instance.number}",
                    message=f"Your incident '{instance.title}' has been resolved.",
                    link=f"/incidents/{instance.pk}/"
                )
                send_notification_email(
                    instance.caller,
                    f"Incident Resolved: {instance.number}",
                    f"Your incident '{instance.title}' has been resolved.\n\nResolution Notes: {instance.resolution_notes or 'N/A'}"
                )
        
        # Check for assignment changes
        if hasattr(instance, '_original_assigned_to') and instance._original_assigned_to != instance.assigned_to:
            if instance.assigned_to:
                Notification.create_notification(
                    user=instance.assigned_to,
                    notification_type='incident_assigned',
                    title=f"Incident Assigned: {instance.number}",
                    message=f"You have been assigned to incident '{instance.title}'.",
                    link=f"/incidents/{instance.pk}/"
                )
                send_notification_email(
                    instance.assigned_to,
                    f"Incident Assigned: {instance.number}",
                    f"You have been assigned to incident '{instance.title}'.\n\nPriority: {instance.get_priority_display()}"
                )


@receiver(pre_save, sender=Incident)
def store_original_incident_values(sender, instance, **kwargs):
    """Store original values for comparison in post_save."""
    if instance.pk:
        try:
            original = Incident.objects.get(pk=instance.pk)
            instance._original_state = original.state
            instance._original_assigned_to = original.assigned_to
        except Incident.DoesNotExist:
            pass


@receiver(post_save, sender=ServiceRequest)
def service_request_notification(sender, instance, created, **kwargs):
    """Create notifications for service request changes."""
    
    if not created:
        # Check for state changes
        if hasattr(instance, '_original_state') and instance._original_state != instance.state:
            # Notify requester when request is approved
            if instance.state == 'approved' and instance.requester:
                Notification.create_notification(
                    user=instance.requester,
                    notification_type='request_approved',
                    title=f"Request Approved: {instance.number}",
                    message=f"Your service request '{instance.title}' has been approved.",
                    link=f"/requests/{instance.pk}/"
                )
                send_notification_email(
                    instance.requester,
                    f"Request Approved: {instance.number}",
                    f"Your service request '{instance.title}' has been approved and is now being processed."
                )
            
            # Notify requester when request is rejected
            elif instance.state == 'rejected' and instance.requester:
                Notification.create_notification(
                    user=instance.requester,
                    notification_type='request_rejected',
                    title=f"Request Rejected: {instance.number}",
                    message=f"Your service request '{instance.title}' has been rejected.",
                    link=f"/requests/{instance.pk}/"
                )
                send_notification_email(
                    instance.requester,
                    f"Request Rejected: {instance.number}",
                    f"Your service request '{instance.title}' has been rejected.\n\nNotes: {instance.notes or 'No additional information provided.'}"
                )
            
            # Notify requester when request is completed
            elif instance.state == 'completed' and instance.requester:
                Notification.create_notification(
                    user=instance.requester,
                    notification_type='request_completed',
                    title=f"Request Completed: {instance.number}",
                    message=f"Your service request '{instance.title}' has been completed.",
                    link=f"/requests/{instance.pk}/"
                )
                send_notification_email(
                    instance.requester,
                    f"Request Completed: {instance.number}",
                    f"Your service request '{instance.title}' has been completed."
                )


@receiver(pre_save, sender=ServiceRequest)
def store_original_request_values(sender, instance, **kwargs):
    """Store original values for comparison in post_save."""
    if instance.pk:
        try:
            original = ServiceRequest.objects.get(pk=instance.pk)
            instance._original_state = original.state
        except ServiceRequest.DoesNotExist:
            pass
