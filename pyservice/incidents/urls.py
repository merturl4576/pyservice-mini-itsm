"""
Incident URLs
PyService Mini-ITSM Platform
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.incident_list, name='incident_list'),
    path('create/', views.incident_create, name='incident_create'),
    path('<int:pk>/', views.incident_detail, name='incident_detail'),
    path('<int:pk>/edit/', views.incident_update, name='incident_update'),
    path('<int:pk>/claim/', views.incident_claim, name='incident_claim'),
    path('<int:pk>/complete/', views.incident_complete, name='incident_complete'),
    path('<int:pk>/escalate/', views.incident_escalate, name='incident_escalate'),
    path('<int:pk>/delete/', views.incident_delete, name='incident_delete'),
]
