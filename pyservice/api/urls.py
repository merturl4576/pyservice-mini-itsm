"""
API URL Configuration
PyService Mini-ITSM Platform
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, UserViewSet, AssetViewSet,
    IncidentViewSet, ServiceRequestViewSet
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'users', UserViewSet)
router.register(r'assets', AssetViewSet)
router.register(r'incidents', IncidentViewSet)
router.register(r'requests', ServiceRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
