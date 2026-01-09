"""
API URL Configuration
PyService Mini-ITSM Platform

Complete API routing including:
- REST API (ViewSets)
- JWT Authentication
- Health checks
- GraphQL
- Search
- Reports
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from .views import (
    DepartmentViewSet, UserViewSet, AssetViewSet,
    IncidentViewSet, ServiceRequestViewSet
)
from .auth import (
    CustomTokenObtainPairView, LogoutView, UserProfileView,
    TwoFactorSetupView, TwoFactorVerifyView, TwoFactorDisableView
)
from .health import (
    HealthCheckView, DetailedHealthCheckView,
    ReadinessCheckView, LivenessCheckView, MetricsView
)
from search.views import GlobalSearchView, SearchSuggestionsView

# =============================================================================
# REST API Router
# =============================================================================
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'users', UserViewSet)
router.register(r'assets', AssetViewSet)
router.register(r'incidents', IncidentViewSet)
router.register(r'requests', ServiceRequestViewSet)

# =============================================================================
# URL Patterns
# =============================================================================
urlpatterns = [
    # REST API
    path('', include(router.urls)),
    
    # ---------------------------------------------------------------------
    # Authentication
    # ---------------------------------------------------------------------
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
    
    # 2FA
    path('auth/2fa/setup/', TwoFactorSetupView.as_view(), name='2fa_setup'),
    path('auth/2fa/verify/', TwoFactorVerifyView.as_view(), name='2fa_verify'),
    path('auth/2fa/disable/', TwoFactorDisableView.as_view(), name='2fa_disable'),
    
    # ---------------------------------------------------------------------
    # Health Checks
    # ---------------------------------------------------------------------
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('health/detailed/', DetailedHealthCheckView.as_view(), name='health_detailed'),
    path('health/ready/', ReadinessCheckView.as_view(), name='health_ready'),
    path('health/live/', LivenessCheckView.as_view(), name='health_live'),
    path('health/metrics/', MetricsView.as_view(), name='health_metrics'),
    
    # ---------------------------------------------------------------------
    # Search
    # ---------------------------------------------------------------------
    path('search/', GlobalSearchView.as_view(), name='global_search'),
    path('search/suggestions/', SearchSuggestionsView.as_view(), name='search_suggestions'),
    
    # ---------------------------------------------------------------------
    # API Documentation
    # ---------------------------------------------------------------------
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
