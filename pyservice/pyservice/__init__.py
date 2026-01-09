"""
PyService Mini-ITSM Platform

This module initializes the Celery app to ensure it's loaded
when Django starts.
"""

# Import Celery app to ensure it's loaded
from .celery import app as celery_app

__all__ = ('celery_app',)

# Version
__version__ = '2.0.0'
