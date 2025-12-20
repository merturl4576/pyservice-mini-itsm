"""
Main URL Configuration
PyService Mini-ITSM Platform
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

from .dashboard import dashboard


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
    
    # Apps
    path('cmdb/', include('cmdb.urls')),
    path('incidents/', include('incidents.urls')),
    path('requests/', include('service_requests.urls')),
    
    # API
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
]

# Admin site customization
admin.site.site_header = 'PyService Admin'
admin.site.site_title = 'PyService'
admin.site.index_title = 'Administration'
