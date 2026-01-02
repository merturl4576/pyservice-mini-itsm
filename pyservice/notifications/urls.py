"""
Notifications URL Configuration
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('api/', views.notification_api, name='notification_api'),
    path('mark-read/<int:notification_id>/', views.mark_as_read, name='notification_mark_read'),
    path('mark-all-read/', views.mark_all_as_read, name='notification_mark_all_read'),
]
