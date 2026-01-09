"""
Main URL Configuration
PyService Mini-ITSM Platform

Complete URL routing including:
- Web views
- API endpoints
- GraphQL
- Prometheus metrics
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.conf import settings
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

from .dashboard import dashboard, staff_leaderboard, staff_detail
from .calendar_view import calendar_page, calendar_events_api
from .sla_dashboard import sla_dashboard
from .search import global_search
from .selfservice import selfservice_portal


def home(request):
    """Redirect home to dashboard."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


urlpatterns = [
    # =========================================================================
    # Admin
    # =========================================================================
    path('admin/', admin.site.urls),
    
    # =========================================================================
    # Authentication
    # =========================================================================
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # =========================================================================
    # Main Views
    # =========================================================================
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('staff-leaderboard/', staff_leaderboard, name='staff_leaderboard'),
    path('staff-detail/<int:user_id>/', staff_detail, name='staff_detail'),
    
    # =========================================================================
    # Features
    # =========================================================================
    path('calendar/', calendar_page, name='calendar'),
    path('calendar/events/', calendar_events_api, name='calendar_events'),
    path('sla-dashboard/', sla_dashboard, name='sla_dashboard'),
    path('search/', global_search, name='global_search'),
    path('selfservice/', selfservice_portal, name='selfservice'),
    
    # =========================================================================
    # Application URLs
    # =========================================================================
    path('cmdb/', include('cmdb.urls')),
    path('incidents/', include('incidents.urls')),
    path('requests/', include('service_requests.urls')),
    path('notifications/', include('notifications.urls')),
    path('knowledge/', include('knowledge.urls')),
    path('reports/', include('reports.urls')),
    path('core/', include('core.urls')),
    path('support/', include('remote_support.urls')),
    
    # =========================================================================
    # REST API
    # =========================================================================
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    
    # =========================================================================
    # GraphQL
    # =========================================================================
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True)), name='graphql'),
    
    # =========================================================================
    # Prometheus Metrics (for monitoring)
    # =========================================================================
    path('', include('django_prometheus.urls')),
]

# Admin site customization
admin.site.site_header = 'PyService Admin'
admin.site.site_title = 'PyService'
admin.site.index_title = 'Administration'

# Debug toolbar (development only)
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
