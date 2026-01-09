"""
Report Tasks
PyService Mini-ITSM Platform

Celery tasks for report generation:
- Daily/Weekly/Monthly summaries
- Performance metrics
- SLA compliance reports
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.db.models import Count, Avg, Q, F
from django.db.models.functions import TruncDate
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import json

logger = get_task_logger(__name__)


@shared_task
def generate_daily_summary():
    """
    Generate daily summary report.
    Runs at 6 AM via Celery Beat.
    """
    from incidents.models import Incident
    from service_requests.models import ServiceRequest
    
    try:
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Incident statistics
        incidents_created = Incident.objects.filter(
            created_at__date=yesterday
        ).count()
        
        incidents_resolved = Incident.objects.filter(
            resolved_at__date=yesterday
        ).count()
        
        sla_breaches = Incident.objects.filter(
            created_at__date=yesterday,
            sla_breached=True
        ).count()
        
        # Request statistics
        requests_created = ServiceRequest.objects.filter(
            created_at__date=yesterday
        ).count()
        
        requests_completed = ServiceRequest.objects.filter(
            completed_at__date=yesterday
        ).count()
        
        # Calculate SLA compliance
        total_incidents = incidents_created or 1  # Avoid division by zero
        sla_compliance = ((total_incidents - sla_breaches) / total_incidents) * 100
        
        summary = {
            'date': str(yesterday),
            'incidents': {
                'created': incidents_created,
                'resolved': incidents_resolved,
                'sla_breaches': sla_breaches,
                'sla_compliance': round(sla_compliance, 2)
            },
            'requests': {
                'created': requests_created,
                'completed': requests_completed
            }
        }
        
        logger.info(f"Daily summary generated for {yesterday}: {summary}")
        
        # Send email to admins
        send_summary_email.delay('daily', summary)
        
        return summary
        
    except Exception as exc:
        logger.error(f"Failed to generate daily summary: {exc}")
        raise


@shared_task
def generate_weekly_report():
    """
    Generate weekly report.
    Runs every Monday at 7 AM via Celery Beat.
    """
    from incidents.models import Incident
    from service_requests.models import ServiceRequest
    from cmdb.models import User
    
    try:
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday() + 7)  # Last Monday
        week_end = week_start + timedelta(days=6)  # Last Sunday
        
        # Incident trends by day
        incidents_by_day = Incident.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=week_end
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Incidents by priority
        incidents_by_priority = Incident.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=week_end
        ).values('priority').annotate(
            count=Count('id')
        ).order_by('priority')
        
        # Top performers (most resolved incidents)
        top_performers = User.objects.filter(
            assigned_incidents__resolved_at__date__gte=week_start,
            assigned_incidents__resolved_at__date__lte=week_end
        ).annotate(
            resolved_count=Count('assigned_incidents')
        ).order_by('-resolved_count')[:5]
        
        # SLA compliance rate
        total_incidents = Incident.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=week_end
        ).count()
        
        sla_breaches = Incident.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=week_end,
            sla_breached=True
        ).count()
        
        sla_compliance = ((total_incidents - sla_breaches) / max(total_incidents, 1)) * 100
        
        # Average resolution time
        avg_resolution = Incident.objects.filter(
            resolved_at__date__gte=week_start,
            resolved_at__date__lte=week_end
        ).annotate(
            resolution_time=F('resolved_at') - F('created_at')
        ).aggregate(
            avg_time=Avg('resolution_time')
        )['avg_time']
        
        report = {
            'week': f"{week_start} to {week_end}",
            'total_incidents': total_incidents,
            'sla_breaches': sla_breaches,
            'sla_compliance': round(sla_compliance, 2),
            'avg_resolution_hours': avg_resolution.total_seconds() / 3600 if avg_resolution else None,
            'incidents_by_day': list(incidents_by_day),
            'incidents_by_priority': list(incidents_by_priority),
            'top_performers': [
                {'username': u.username, 'resolved': u.resolved_count}
                for u in top_performers
            ]
        }
        
        logger.info(f"Weekly report generated for {week_start} to {week_end}")
        
        # Send email to managers
        send_summary_email.delay('weekly', report)
        
        return report
        
    except Exception as exc:
        logger.error(f"Failed to generate weekly report: {exc}")
        raise


@shared_task
def generate_monthly_summary():
    """
    Generate monthly summary report.
    Runs on the 1st of each month at 8 AM.
    """
    from incidents.models import Incident
    from service_requests.models import ServiceRequest
    from cmdb.models import Asset
    
    try:
        today = timezone.now().date()
        # Get last month
        first_of_this_month = today.replace(day=1)
        last_of_prev_month = first_of_this_month - timedelta(days=1)
        first_of_prev_month = last_of_prev_month.replace(day=1)
        
        # Summary statistics
        incidents_total = Incident.objects.filter(
            created_at__date__gte=first_of_prev_month,
            created_at__date__lte=last_of_prev_month
        ).count()
        
        incidents_resolved = Incident.objects.filter(
            resolved_at__date__gte=first_of_prev_month,
            resolved_at__date__lte=last_of_prev_month
        ).count()
        
        requests_total = ServiceRequest.objects.filter(
            created_at__date__gte=first_of_prev_month,
            created_at__date__lte=last_of_prev_month
        ).count()
        
        requests_completed = ServiceRequest.objects.filter(
            completed_at__date__gte=first_of_prev_month,
            completed_at__date__lte=last_of_prev_month
        ).count()
        
        # Asset statistics
        assets_total = Asset.objects.count()
        assets_assigned = Asset.objects.filter(status='assigned').count()
        assets_in_stock = Asset.objects.filter(status='in_stock').count()
        
        report = {
            'month': first_of_prev_month.strftime('%B %Y'),
            'incidents': {
                'total': incidents_total,
                'resolved': incidents_resolved,
                'resolution_rate': round((incidents_resolved / max(incidents_total, 1)) * 100, 2)
            },
            'requests': {
                'total': requests_total,
                'completed': requests_completed,
                'completion_rate': round((requests_completed / max(requests_total, 1)) * 100, 2)
            },
            'assets': {
                'total': assets_total,
                'assigned': assets_assigned,
                'in_stock': assets_in_stock,
                'utilization_rate': round((assets_assigned / max(assets_total, 1)) * 100, 2)
            }
        }
        
        logger.info(f"Monthly summary generated for {first_of_prev_month.strftime('%B %Y')}")
        
        return report
        
    except Exception as exc:
        logger.error(f"Failed to generate monthly summary: {exc}")
        raise


@shared_task
def update_staff_performance():
    """
    Update staff performance scores.
    Runs every hour via Celery Beat.
    """
    from cmdb.models import User
    from incidents.models import Incident
    from service_requests.models import ServiceRequest
    
    try:
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        # Get all support staff
        support_staff = User.objects.filter(
            role__in=['it_support', 'technician', 'admin']
        )
        
        scores = []
        
        for user in support_staff:
            # Count resolved incidents
            resolved_incidents = Incident.objects.filter(
                assigned_to=user,
                resolved_at__gte=thirty_days_ago
            ).count()
            
            # Count SLA compliant incidents
            sla_compliant = Incident.objects.filter(
                assigned_to=user,
                resolved_at__gte=thirty_days_ago,
                sla_breached=False
            ).count()
            
            # Count completed requests
            completed_requests = ServiceRequest.objects.filter(
                assigned_to=user,
                completed_at__gte=thirty_days_ago
            ).count()
            
            # Calculate score (weighted)
            score = (
                resolved_incidents * 10 +
                sla_compliant * 5 +
                completed_requests * 8
            )
            
            scores.append({
                'user_id': user.pk,
                'username': user.username,
                'resolved_incidents': resolved_incidents,
                'sla_compliant': sla_compliant,
                'completed_requests': completed_requests,
                'score': score
            })
        
        # Sort by score
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"Updated performance scores for {len(scores)} staff members")
        return {'staff_count': len(scores), 'top_3': scores[:3]}
        
    except Exception as exc:
        logger.error(f"Failed to update performance scores: {exc}")
        raise


@shared_task(bind=True, max_retries=2)
def send_summary_email(self, report_type, data):
    """
    Send summary report email to administrators.
    """
    from cmdb.models import User
    
    try:
        # Get admin emails
        admins = User.objects.filter(
            role__in=['admin', 'manager'],
            is_active=True,
            email__isnull=False
        ).exclude(email='')
        
        if not admins.exists():
            logger.warning("No admin emails found for summary report")
            return {'status': 'no_recipients'}
        
        recipient_list = list(admins.values_list('email', flat=True))
        
        subject = f"[PyService] {report_type.title()} Report - {timezone.now().strftime('%Y-%m-%d')}"
        
        # Format the data nicely
        message = f"""
PyService {report_type.title()} Report
{'=' * 40}

Generated: {timezone.now().strftime('%Y-%m-%d %H:%M')}

Report Data:
{json.dumps(data, indent=2, default=str)}

---
PyService Mini-ITSM Platform
Automated Report
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        logger.info(f"{report_type.title()} report email sent to {len(recipient_list)} recipients")
        return {'status': 'sent', 'recipients': len(recipient_list)}
        
    except Exception as exc:
        logger.error(f"Failed to send summary email: {exc}")
        raise self.retry(exc=exc, countdown=300)


@shared_task
def export_incident_report_to_pdf(start_date, end_date, user_id):
    """
    Generate and export incident report as PDF.
    This task is triggered manually by users.
    """
    # PDF generation will be handled by the pdf_generator module
    # This task queues the job and notifies user when ready
    from notifications.models import Notification
    from cmdb.models import User
    
    try:
        user = User.objects.get(pk=user_id)
        
        # TODO: Implement PDF generation
        # pdf_path = generate_incident_pdf(start_date, end_date)
        
        Notification.create_notification(
            user=user,
            notification_type='general',
            title='Report Ready',
            message=f'Your incident report for {start_date} to {end_date} is ready for download.',
            link='/reports/downloads/'
        )
        
        logger.info(f"PDF report generated for user {user.username}")
        return {'status': 'completed'}
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {'status': 'user_not_found'}
    except Exception as exc:
        logger.error(f"Failed to generate PDF report: {exc}")
        raise
