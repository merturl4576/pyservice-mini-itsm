"""
CMDB URLs
PyService Mini-ITSM Platform
"""

from django.urls import path
from . import views

urlpatterns = [
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/create/', views.asset_create, name='asset_create'),
    path('assets/<int:pk>/', views.asset_detail, name='asset_detail'),
    path('assets/<int:pk>/edit/', views.asset_update, name='asset_update'),
    path('assets/<int:pk>/approve/', views.asset_approve, name='asset_approve'),
    path('assets/<int:pk>/decline/', views.asset_decline, name='asset_decline'),
    path('assets/<int:pk>/delete/', views.asset_delete, name='asset_delete'),
    
    path('inventory/edit/', views.inventory_edit, name='inventory_edit'),
    
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_update, name='department_update'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
]
