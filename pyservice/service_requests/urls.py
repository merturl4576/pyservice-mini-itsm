"""
Service Request URLs
PyService Mini-ITSM Platform
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.request_list, name='request_list'),
    path('create/', views.request_create, name='request_create'),
    path('<int:pk>/', views.request_detail, name='request_detail'),
    path('<int:pk>/edit/', views.request_update, name='request_update'),
    path('<int:pk>/submit/', views.request_submit, name='request_submit'),
    path('<int:pk>/approve/', views.request_approve, name='request_approve'),
    path('<int:pk>/reject/', views.request_reject, name='request_reject'),
    path('<int:pk>/claim/', views.request_claim, name='request_claim'),
    path('<int:pk>/complete/', views.request_complete, name='request_complete'),
    path('<int:pk>/escalate/', views.request_escalate, name='request_escalate'),
    path('<int:pk>/delete/', views.request_delete, name='request_delete'),
]
