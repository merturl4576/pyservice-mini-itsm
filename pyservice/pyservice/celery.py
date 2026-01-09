"""
Celery Configuration
PyService Mini-ITSM Platform

Celery app configuration for asynchronous task processing.
Tasks include: email notifications, SLA monitoring, report generation.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyservice.settings')

# Create Celery app
app = Celery('pyservice')

# Load config from Django settings, using CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all registered Django apps
app.autodiscover_tasks()

# =============================================================================
# Celery Beat Schedule - Periodic Tasks
# =============================================================================
app.conf.beat_schedule = {
    # Check for SLA breaches every 5 minutes
    'check-sla-breaches-every-5-minutes': {
        'task': 'incidents.tasks.check_sla_breaches',
        'schedule': crontab(minute='*/5'),
        'options': {'queue': 'high_priority'}
    },
    
    # Send SLA warning emails every 15 minutes
    'send-sla-warnings-every-15-minutes': {
        'task': 'incidents.tasks.send_sla_warning_emails',
        'schedule': crontab(minute='*/15'),
        'options': {'queue': 'default'}
    },
    
    # Generate daily summary report at 6 AM
    'generate-daily-report': {
        'task': 'reports.tasks.generate_daily_summary',
        'schedule': crontab(hour=6, minute=0),
        'options': {'queue': 'low_priority'}
    },
    
    # Generate weekly report every Monday at 7 AM
    'generate-weekly-report': {
        'task': 'reports.tasks.generate_weekly_report',
        'schedule': crontab(hour=7, minute=0, day_of_week=1),
        'options': {'queue': 'low_priority'}
    },
    
    # Clean up old notifications every day at midnight
    'cleanup-old-notifications': {
        'task': 'notifications.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=0, minute=0),
        'options': {'queue': 'low_priority'}
    },
    
    # Update staff performance scores every hour
    'update-performance-scores': {
        'task': 'reports.tasks.update_staff_performance',
        'schedule': crontab(minute=0),
        'options': {'queue': 'default'}
    },
}

# =============================================================================
# Celery Configuration
# =============================================================================
app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Istanbul',
    enable_utc=True,
    
    # Task execution
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=300,  # 5 minutes hard limit
    task_soft_time_limit=240,  # 4 minutes soft limit
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Result backend settings
    result_expires=86400,  # Results expire after 1 day
    
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Queue routing
    task_routes={
        'incidents.tasks.*': {'queue': 'high_priority'},
        'notifications.tasks.send_email_*': {'queue': 'email'},
        'reports.tasks.*': {'queue': 'low_priority'},
    },
    
    # Default queue
    task_default_queue='default',
    
    # Queues
    task_queues={
        'high_priority': {
            'exchange': 'high_priority',
            'routing_key': 'high_priority',
        },
        'default': {
            'exchange': 'default',
            'routing_key': 'default',
        },
        'low_priority': {
            'exchange': 'low_priority',
            'routing_key': 'low_priority',
        },
        'email': {
            'exchange': 'email',
            'routing_key': 'email',
        },
    },
)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery configuration."""
    print(f'Request: {self.request!r}')
