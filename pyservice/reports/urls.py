"""
Reports URL Configuration
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('export/incidents/', views.export_incidents_csv, name='export_incidents'),
    path('export/requests/', views.export_requests_csv, name='export_requests'),
    path('export/assets/', views.export_assets_csv, name='export_assets'),
    path('monthly/', views.monthly_summary, name='monthly_summary'),
]
