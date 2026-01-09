"""
ASGI Configuration
PyService Mini-ITSM Platform

ASGI config with Django Channels for WebSocket support.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyservice.settings')

# Initialize Django ASGI application early
django_asgi_app = get_asgi_application()

# Import WebSocket URL patterns after Django setup
from notifications.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # HTTP requests are handled by Django's ASGI application
    "http": django_asgi_app,
    
    # WebSocket connections with authentication
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
