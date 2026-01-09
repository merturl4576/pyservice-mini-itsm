"""
Incident Tasks
PyService Mini-ITSM Platform

Celery tasks for incident management:
- SLA breach checking
- Warning emails
- Escalation automation
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3)
def check_sla_breaches(self):
    """
    Check for SLA breaches on open incidents.
    Runs every 5 minutes via Celery Beat.
    
    - Marks incidents as SLA breached if past due date
    - Sends notifications to assigned users and managers
    """
    from incidents.models import Incident
    from notifications.models import Notification
    
    try:
        now = timezone.now()
        
        # Find open incidents that have breached SLA
        breached_incidents = Incident.objects.filter(
            state__in=['new', 'in_progress', 'escalated'],
            sla_breached=False,
            due_date__lt=now
        )
        
        breached_count = 0
        
        for incident in breached_incidents:
            # Mark as SLA breached
            incident.sla_breached = True
            incident.save(update_fields=['sla_breached'])
            
            # Create notification for assigned user
            if incident.assigned_to:
                Notification.create_notification(
                    user=incident.assigned_to,
                    notification_type='sla_breached',
                    title=f'SLA Breached: {incident.number}',
                    message=f'Incident "{incident.title}" has breached its SLA deadline.',
                    link=f'/incidents/{incident.pk}/'
                )
            
            # Queue email notification
            send_sla_breach_email.delay(incident.pk)
            
            breached_count += 1
            logger.info(f"SLA breach marked for incident {incident.number}")
        
        logger.info(f"SLA breach check completed. Found {breached_count} new breaches.")
        return {'breached_count': breached_count}
        
    except Exception as exc:
        logger.error(f"SLA breach check failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_sla_warning_emails(self):
    """
    Send warning emails for incidents approaching SLA deadline.
    Alerts are sent when:
    - 1 hour remaining for P1 (Critical)
    - 4 hours remaining for P2 (High)
    - 12 hours remaining for P3/P4
    """
    from incidents.models import Incident
    from notifications.models import Notification
    
    try:
        now = timezone.now()
        
        # Define warning thresholds by priority
        thresholds = {
            1: timedelta(hours=1),   # P1: 1 hour warning
            2: timedelta(hours=4),   # P2: 4 hours warning
            3: timedelta(hours=12),  # P3: 12 hours warning
            4: timedelta(hours=12),  # P4: 12 hours warning
        }
        
        warnings_sent = 0
        
        for priority, threshold in thresholds.items():
            warning_time = now + threshold
            
            # Find incidents approaching deadline
            at_risk_incidents = Incident.objects.filter(
                state__in=['new', 'in_progress'],
                sla_breached=False,
                priority=priority,
                due_date__lte=warning_time,
                due_date__gt=now
            ).exclude(
                # Don't warn again if already warned (check if notification exists)
                assigned_to__notifications__notification_type='sla_warning',
                assigned_to__notifications__created_at__gte=now - timedelta(hours=1)
            )
            
            for incident in at_risk_incidents:
                if incident.assigned_to:
                    # Create in-app notification
                    Notification.create_notification(
                        user=incident.assigned_to,
                        notification_type='sla_warning',
                        title=f'SLA Warning: {incident.number}',
                        message=f'Incident "{incident.title}" is approaching SLA deadline. '
                                f'Time remaining: {incident.get_sla_status()}',
                        link=f'/incidents/{incident.pk}/'
                    )
                    
                    # Queue email
                    send_sla_warning_email.delay(incident.pk)
                    warnings_sent += 1
        
        logger.info(f"SLA warning check completed. Sent {warnings_sent} warnings.")
        return {'warnings_sent': warnings_sent}
        
    except Exception as exc:
        logger.error(f"SLA warning check failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3, rate_limit='10/m')
def send_sla_breach_email(self, incident_id):
    """Send email notification for SLA breach."""
    from incidents.models import Incident
    
    try:
        incident = Incident.objects.select_related('assigned_to', 'caller').get(pk=incident_id)
        
        recipients = []
        if incident.assigned_to and incident.assigned_to.email:
            recipients.append(incident.assigned_to.email)
        if incident.caller and incident.caller.email:
            recipients.append(incident.caller.email)
        
        if recipients:
            subject = f'[URGENT] SLA Breached: {incident.number}'
            message = f"""
URGENT: SLA BREACH NOTIFICATION

Incident: {incident.number}
Title: {incident.title}
Priority: P{incident.priority}
Due Date: {incident.due_date.strftime('%Y-%m-%d %H:%M')}
Status: {incident.get_state_display()}

This incident has exceeded its SLA deadline and requires immediate attention.

Please take action immediately.

---
PyService Mini-ITSM Platform
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            
            logger.info(f"SLA breach email sent for incident {incident.number}")
            return {'status': 'sent', 'recipients': recipients}
        
        return {'status': 'no_recipients'}
        
    except Incident.DoesNotExist:
        logger.warning(f"Incident {incident_id} not found for email")
        return {'status': 'not_found'}
    except Exception as exc:
        logger.error(f"Failed to send SLA breach email: {exc}")
        raise self.retry(exc=exc, countdown=120)


@shared_task(bind=True, max_retries=3, rate_limit='10/m')
def send_sla_warning_email(self, incident_id):
    """Send email notification for SLA warning."""
    from incidents.models import Incident
    
    try:
        incident = Incident.objects.select_related('assigned_to').get(pk=incident_id)
        
        if incident.assigned_to and incident.assigned_to.email:
            subject = f'[WARNING] SLA Deadline Approaching: {incident.number}'
            message = f"""
SLA WARNING NOTIFICATION

Incident: {incident.number}
Title: {incident.title}
Priority: P{incident.priority}
Due Date: {incident.due_date.strftime('%Y-%m-%d %H:%M')}
Time Remaining: {incident.get_sla_status()}

This incident is approaching its SLA deadline. Please prioritize resolution.

---
PyService Mini-ITSM Platform
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[incident.assigned_to.email],
                fail_silently=False,
            )
            
            logger.info(f"SLA warning email sent for incident {incident.number}")
            return {'status': 'sent'}
        
        return {'status': 'no_email'}
        
    except Incident.DoesNotExist:
        logger.warning(f"Incident {incident_id} not found for email")
        return {'status': 'not_found'}
    except Exception as exc:
        logger.error(f"Failed to send SLA warning email: {exc}")
        raise self.retry(exc=exc, countdown=120)


@shared_task(bind=True)
def auto_escalate_stale_incidents(self):
    """
    Auto-escalate incidents that have been stale for too long.
    - P1: Escalate after 2 hours with no activity
    - P2: Escalate after 8 hours with no activity
    """
    from incidents.models import Incident
    from core.models import ActivityLog
    
    try:
        now = timezone.now()
        escalated_count = 0
        
        stale_thresholds = {
            1: timedelta(hours=2),
            2: timedelta(hours=8),
        }
        
        for priority, threshold in stale_thresholds.items():
            stale_time = now - threshold
            
            stale_incidents = Incident.objects.filter(
                state='in_progress',
                priority=priority,
                updated_at__lt=stale_time
            )
            
            for incident in stale_incidents:
                incident.escalate(notes=f"Auto-escalated due to no activity for {threshold}")
                
                # Log the auto-escalation
                ActivityLog.log(
                    user=None,
                    action='escalate',
                    obj=incident,
                    details='Automatic escalation due to inactivity'
                )
                
                escalated_count += 1
                logger.info(f"Auto-escalated incident {incident.number}")
        
        return {'escalated_count': escalated_count}
        
    except Exception as exc:
        logger.error(f"Auto-escalation failed: {exc}")
        raise


@shared_task
def send_incident_assignment_email(incident_id, assigned_by_id):
    """Send email when incident is assigned to someone."""
    from incidents.models import Incident
    from cmdb.models import User
    
    try:
        incident = Incident.objects.select_related('assigned_to', 'caller').get(pk=incident_id)
        assigned_by = User.objects.get(pk=assigned_by_id) if assigned_by_id else None
        
        if incident.assigned_to and incident.assigned_to.email:
            subject = f'Incident Assigned: {incident.number}'
            message = f"""
INCIDENT ASSIGNMENT

You have been assigned to the following incident:

Incident: {incident.number}
Title: {incident.title}
Priority: P{incident.priority} - {incident.get_priority_display()}
Caller: {incident.caller.get_full_name() if incident.caller else 'Unknown'}
Due Date: {incident.due_date.strftime('%Y-%m-%d %H:%M')}

Description:
{incident.description[:500]}{'...' if len(incident.description) > 500 else ''}

{'Assigned by: ' + assigned_by.get_full_name() if assigned_by else ''}

---
PyService Mini-ITSM Platform
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[incident.assigned_to.email],
                fail_silently=False,
            )
            
            logger.info(f"Assignment email sent for incident {incident.number}")
            
    except Exception as exc:
        logger.error(f"Failed to send assignment email: {exc}")
