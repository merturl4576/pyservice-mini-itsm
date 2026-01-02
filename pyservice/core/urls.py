"""
Core App URL Configuration
"""

from django.urls import path
from . import views

urlpatterns = [
    path('activity-log/', views.activity_log_list, name='activity_log'),
]
