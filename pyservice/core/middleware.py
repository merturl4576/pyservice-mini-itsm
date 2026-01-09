"""
Core Middleware
PyService Mini-ITSM Platform

Custom middleware for:
- Audit logging (all requests)
- Rate limiting
- Request timing
"""

import time
import json
import logging
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger('pyservice.audit')


class AuditMiddleware:
    """
    Middleware for comprehensive request audit logging.
    Logs all requests with user, IP, method, path, and timing.
    """
    
    # Paths to exclude from logging
    EXCLUDED_PATHS = [
        '/static/',
        '/media/',
        '/favicon.ico',
        '/health/',
        '/metrics',
        '/__debug__/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip excluded paths
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return self.get_response(request)
        
        # Start timing
        start_time = time.time()
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', 'unknown')
        
        # Store in request for later use
        request.client_ip = ip_address
        request.start_time = start_time
        
        # Process request
        response = self.get_response(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log the request
        self._log_request(request, response, duration, ip_address)
        
        # Add timing header
        response['X-Request-Duration'] = f'{duration:.3f}s'
        
        return response
    
    def _log_request(self, request, response, duration, ip_address):
        """Log request details for audit trail."""
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'ip_address': ip_address,
            'user_id': user.pk if user else None,
            'username': user.username if user else 'anonymous',
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
            'referer': request.META.get('HTTP_REFERER', '')[:500],
        }
        
        # Add query params for GET requests (exclude sensitive data)
        if request.method == 'GET' and request.GET:
            safe_params = {k: v for k, v in request.GET.items() 
                         if k.lower() not in ['password', 'token', 'key', 'secret']}
            log_data['query_params'] = safe_params
        
        # Log based on status code
        if response.status_code >= 500:
            logger.error(json.dumps(log_data))
        elif response.status_code >= 400:
            logger.warning(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))
    
    def process_exception(self, request, exception):
        """Log exceptions."""
        logger.exception(f"Exception during request to {request.path}: {exception}")
        return None


class RequestTimingMiddleware:
    """
    Middleware to add request timing information.
    Useful for performance monitoring.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Add headers
        response['X-Request-Start'] = str(start_time)
        response['X-Request-Duration'] = f'{duration:.4f}'
        
        # Log slow requests
        if duration > 1.0:  # More than 1 second
            logger.warning(f"Slow request: {request.method} {request.path} took {duration:.2f}s")
        
        return response


class SecurityHeadersMiddleware:
    """
    Add security headers to all responses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Only add HSTS in production
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class MaintenanceModeMiddleware:
    """
    Middleware to enable maintenance mode.
    Set MAINTENANCE_MODE=True in settings to enable.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if getattr(settings, 'MAINTENANCE_MODE', False):
            # Allow admin access
            if request.path.startswith('/admin/'):
                return self.get_response(request)
            
            # Allow health checks
            if request.path in ['/health/', '/api/health/']:
                return self.get_response(request)
            
            from django.http import JsonResponse
            return JsonResponse({
                'status': 'maintenance',
                'message': 'The system is currently under maintenance. Please try again later.'
            }, status=503)
        
        return self.get_response(request)
