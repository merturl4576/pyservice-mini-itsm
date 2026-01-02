"""
Main URL Configuration
PyService Mini-ITSM Platform
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

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
    # Admin
    path('admin/', admin.site.urls),
    
    # Auth
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Main
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('staff-leaderboard/', staff_leaderboard, name='staff_leaderboard'),
    path('staff-detail/<int:user_id>/', staff_detail, name='staff_detail'),
    
    # New Features
    path('calendar/', calendar_page, name='calendar'),
    path('calendar/events/', calendar_events_api, name='calendar_events'),
    path('sla-dashboard/', sla_dashboard, name='sla_dashboard'),
    path('search/', global_search, name='global_search'),
    path('selfservice/', selfservice_portal, name='selfservice'),
    
    # Apps
    path('cmdb/', include('cmdb.urls')),
    path('incidents/', include('incidents.urls')),
    path('requests/', include('service_requests.urls')),
    path('notifications/', include('notifications.urls')),
    path('knowledge/', include('knowledge.urls')),
    path('reports/', include('reports.urls')),
    path('core/', include('core.urls')),
    
    # API
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
]

# Admin site customization
admin.site.site_header = 'PyService Admin'
admin.site.site_title = 'PyService'
admin.site.index_title = 'Administration'

