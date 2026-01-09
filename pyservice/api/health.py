"""
Health Check Endpoint
PyService Mini-ITSM Platform

Provides health check endpoints for container orchestration
and load balancer health probes.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import redis
import time


class HealthCheckView(APIView):
    """
    Basic health check endpoint.
    Returns 200 if the application is running.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'timestamp': time.time(),
            'service': 'pyservice-itsm',
            'version': getattr(settings, 'VERSION', '2.0.0'),
        })


class DetailedHealthCheckView(APIView):
    """
    Detailed health check with dependency status.
    Checks database, cache, and other services.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def get(self, request):
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'service': 'pyservice-itsm',
            'version': getattr(settings, 'VERSION', '2.0.0'),
            'checks': {}
        }
        
        # Check database
        health_status['checks']['database'] = self._check_database()
        
        # Check cache/Redis
        health_status['checks']['cache'] = self._check_cache()
        
        # Check Celery (if available)
        health_status['checks']['celery'] = self._check_celery()
        
        # Determine overall status
        failed_checks = [
            name for name, check in health_status['checks'].items()
            if check['status'] != 'healthy'
        ]
        
        if failed_checks:
            health_status['status'] = 'unhealthy'
            health_status['failed_checks'] = failed_checks
            return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response(health_status)
    
    def _check_database(self):
        """Check database connectivity."""
        try:
            start = time.time()
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            duration = time.time() - start
            
            return {
                'status': 'healthy',
                'response_time_ms': round(duration * 1000, 2),
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
            }
    
    def _check_cache(self):
        """Check cache/Redis connectivity."""
        try:
            start = time.time()
            
            # Try to set and get a test value
            test_key = 'health_check_test'
            test_value = str(time.time())
            
            cache.set(test_key, test_value, timeout=10)
            retrieved = cache.get(test_key)
            cache.delete(test_key)
            
            duration = time.time() - start
            
            if retrieved == test_value:
                return {
                    'status': 'healthy',
                    'response_time_ms': round(duration * 1000, 2),
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': 'Cache read/write mismatch',
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
            }
    
    def _check_celery(self):
        """Check Celery worker availability."""
        try:
            from pyservice.celery import app
            
            # Ping Celery workers
            inspect = app.control.inspect()
            stats = inspect.stats()
            
            if stats:
                worker_count = len(stats)
                return {
                    'status': 'healthy',
                    'workers': worker_count,
                }
            else:
                return {
                    'status': 'degraded',
                    'message': 'No Celery workers available',
                }
        except Exception as e:
            return {
                'status': 'degraded',
                'error': str(e),
                'message': 'Celery check failed - may not be running',
            }


class ReadinessCheckView(APIView):
    """
    Kubernetes-style readiness probe.
    Returns 200 only when the service is ready to accept traffic.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def get(self, request):
        # Check critical dependencies
        try:
            # Database must be accessible
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            
            return Response({'ready': True})
        except Exception as e:
            return Response(
                {'ready': False, 'error': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class LivenessCheckView(APIView):
    """
    Kubernetes-style liveness probe.
    Returns 200 if the application process is alive.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def get(self, request):
        return Response({'alive': True})


class MetricsView(APIView):
    """
    Basic application metrics endpoint.
    For detailed metrics, use Prometheus integration.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def get(self, request):
        from incidents.models import Incident
        from service_requests.models import ServiceRequest
        from cmdb.models import User, Asset
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        today = now.date()
        last_24h = now - timedelta(hours=24)
        
        try:
            metrics = {
                'timestamp': time.time(),
                'incidents': {
                    'total': Incident.objects.count(),
                    'open': Incident.objects.exclude(state__in=['resolved', 'closed']).count(),
                    'created_24h': Incident.objects.filter(created_at__gte=last_24h).count(),
                    'sla_breached': Incident.objects.filter(sla_breached=True, state__in=['new', 'in_progress']).count(),
                },
                'requests': {
                    'total': ServiceRequest.objects.count(),
                    'pending': ServiceRequest.objects.filter(state='awaiting_approval').count(),
                    'created_24h': ServiceRequest.objects.filter(created_at__gte=last_24h).count(),
                },
                'users': {
                    'total': User.objects.count(),
                    'active': User.objects.filter(is_active=True).count(),
                },
                'assets': {
                    'total': Asset.objects.count(),
                    'assigned': Asset.objects.filter(status='assigned').count(),
                    'in_stock': Asset.objects.filter(status='in_stock').count(),
                },
            }
            
            return Response(metrics)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
