"""
Notification Tasks
PyService Mini-ITSM Platform

Celery tasks for notification handling:
- Email notifications (async)
- Bulk notifications
- Cleanup tasks
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.core.mail import send_mail, send_mass_mail
from django.conf import settings
from datetime import timedelta

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, rate_limit='30/m')
def send_email_notification(self, user_id, subject, message, html_message=None):
    """
    Send a single email notification asynchronously.
    
    Args:
        user_id: ID of the user to send email to
        subject: Email subject
        message: Plain text message
        html_message: Optional HTML message
    """
    from cmdb.models import User
    
    try:
        user = User.objects.get(pk=user_id)
        
        if not user.email:
            logger.warning(f"User {user.username} has no email address")
            return {'status': 'no_email', 'user': user.username}
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Email sent to {user.email}: {subject}")
        return {'status': 'sent', 'email': user.email}
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {'status': 'user_not_found'}
    except Exception as exc:
        logger.error(f"Failed to send email: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=2)
def send_bulk_notifications(self, user_ids, notification_type, title, message, link=''):
    """
    Send notifications to multiple users at once.
    
    Args:
        user_ids: List of user IDs
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        link: Optional link
    """
    from cmdb.models import User
    from notifications.models import Notification
    
    try:
        users = User.objects.filter(pk__in=user_ids)
        
        notifications_created = []
        for user in users:
            notification = Notification.create_notification(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                link=link
            )
            notifications_created.append(notification.pk)
        
        logger.info(f"Created {len(notifications_created)} bulk notifications")
        return {'created': len(notifications_created), 'ids': notifications_created}
        
    except Exception as exc:
        logger.error(f"Failed to create bulk notifications: {exc}")
        raise self.retry(exc=exc, countdown=30)


@shared_task(bind=True, max_retries=2)
def send_bulk_emails(self, messages_data):
    """
    Send multiple emails efficiently using send_mass_mail.
    
    Args:
        messages_data: List of tuples (subject, message, from_email, recipient_list)
    """
    try:
        messages = [
            (msg['subject'], msg['message'], settings.DEFAULT_FROM_EMAIL, msg['recipients'])
            for msg in messages_data
        ]
        
        sent_count = send_mass_mail(messages, fail_silently=False)
        
        logger.info(f"Sent {sent_count} bulk emails")
        return {'sent': sent_count}
        
    except Exception as exc:
        logger.error(f"Failed to send bulk emails: {exc}")
        raise self.retry(exc=exc, countdown=120)


@shared_task
def cleanup_old_notifications():
    """
    Clean up old read notifications.
    Runs daily at midnight via Celery Beat.
    
    - Deletes read notifications older than 30 days
    - Deletes unread notifications older than 90 days
    """
    from notifications.models import Notification
    
    try:
        now = timezone.now()
        
        # Delete old read notifications (30 days)
        read_cutoff = now - timedelta(days=30)
        read_deleted, _ = Notification.objects.filter(
            is_read=True,
            created_at__lt=read_cutoff
        ).delete()
        
        # Delete old unread notifications (90 days)
        unread_cutoff = now - timedelta(days=90)
        unread_deleted, _ = Notification.objects.filter(
            is_read=False,
            created_at__lt=unread_cutoff
        ).delete()
        
        logger.info(f"Notification cleanup: {read_deleted} read, {unread_deleted} unread deleted")
        return {
            'read_deleted': read_deleted,
            'unread_deleted': unread_deleted
        }
        
    except Exception as exc:
        logger.error(f"Notification cleanup failed: {exc}")
        raise


@shared_task
def send_daily_digest(user_id):
    """
    Send daily digest email to a user summarizing their notifications.
    """
    from cmdb.models import User
    from notifications.models import Notification
    
    try:
        user = User.objects.get(pk=user_id)
        
        if not user.email:
            return {'status': 'no_email'}
        
        # Get unread notifications from the last 24 hours
        yesterday = timezone.now() - timedelta(days=1)
        notifications = Notification.objects.filter(
            user=user,
            is_read=False,
            created_at__gte=yesterday
        ).order_by('-created_at')[:10]
        
        if not notifications.exists():
            return {'status': 'no_notifications'}
        
        # Build email content
        notification_list = "\n".join([
            f"• [{n.get_notification_type_display()}] {n.title}"
            for n in notifications
        ])
        
        subject = f"Your Daily PyService Digest - {notifications.count()} unread notifications"
        message = f"""
Hello {user.get_full_name() or user.username},

Here's your daily summary of unread notifications:

{notification_list}

{'... and more' if notifications.count() >= 10 else ''}

Log in to PyService to view all notifications and take action.

---
PyService Mini-ITSM Platform
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Daily digest sent to {user.email}")
        return {'status': 'sent', 'notification_count': notifications.count()}
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for daily digest")
        return {'status': 'user_not_found'}
    except Exception as exc:
        logger.error(f"Failed to send daily digest: {exc}")
        raise


@shared_task
def notify_request_status_change(request_id, old_state, new_state):
    """
    Send notification when a service request status changes.
    """
    from service_requests.models import ServiceRequest
    from notifications.models import Notification
    
    try:
        request = ServiceRequest.objects.select_related('requester', 'assigned_to').get(pk=request_id)
        
        # Determine notification type based on new state
        type_mapping = {
            'awaiting_approval': 'request_submitted',
            'approved': 'request_approved',
            'rejected': 'request_rejected',
            'completed': 'request_completed',
        }
        
        notification_type = type_mapping.get(new_state, 'general')
        
        # Notify the requester
        if request.requester:
            Notification.create_notification(
                user=request.requester,
                notification_type=notification_type,
                title=f'Request {request.number} Status Update',
                message=f'Your request "{request.title}" status changed from '
                        f'{old_state} to {new_state}.',
                link=f'/service-requests/{request.pk}/'
            )
            
            # Send email for important status changes
            if new_state in ['approved', 'rejected', 'completed']:
                send_email_notification.delay(
                    user_id=request.requester.pk,
                    subject=f'[PyService] Request {request.number} - {new_state.title()}',
                    message=f'Your service request "{request.title}" has been {new_state}.'
                )
        
        logger.info(f"Notified status change for request {request.number}: {old_state} -> {new_state}")
        return {'status': 'notified', 'request': request.number}
        
    except ServiceRequest.DoesNotExist:
        logger.error(f"Service request {request_id} not found")
        return {'status': 'not_found'}
    except Exception as exc:
        logger.error(f"Failed to notify request status change: {exc}")
        raise


@shared_task
def broadcast_announcement(title, message, role=None):
    """
    Broadcast an announcement to all users or users with a specific role.
    
    Args:
        title: Announcement title
        message: Announcement message
        role: Optional role filter (e.g., 'it_support', 'manager')
    """
    from cmdb.models import User
    from notifications.models import Notification
    
    try:
        users = User.objects.filter(is_active=True)
        
        if role:
            users = users.filter(role=role)
        
        created_count = 0
        for user in users:
            Notification.create_notification(
                user=user,
                notification_type='general',
                title=title,
                message=message
            )
            created_count += 1
        
        logger.info(f"Broadcast sent to {created_count} users")
        return {'status': 'sent', 'recipients': created_count}
        
    except Exception as exc:
        logger.error(f"Failed to broadcast announcement: {exc}")
        raise
