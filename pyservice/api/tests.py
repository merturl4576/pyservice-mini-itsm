"""
API Tests
PyService Mini-ITSM Platform

Comprehensive tests for REST API endpoints.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from incidents.models import Incident
from service_requests.models import ServiceRequest
from cmdb.models import Department, Asset

User = get_user_model()


@pytest.fixture
def api_client():
    """Create an API client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        role='staff'
    )


@pytest.fixture
def it_support_user(db):
    """Create an IT support user."""
    return User.objects.create_user(
        username='support',
        email='support@example.com',
        password='testpass123',
        role='it_support'
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        role='admin'
    )


@pytest.fixture
def department(db):
    """Create a test department."""
    return Department.objects.create(
        name='IT Department',
        code='IT',
        description='Information Technology'
    )


@pytest.fixture
def incident(db, user):
    """Create a test incident."""
    return Incident.objects.create(
        title='Test Incident',
        description='Test incident description',
        caller=user,
        impact=2,
        urgency=2
    )


@pytest.fixture
def asset(db, user):
    """Create a test asset."""
    return Asset.objects.create(
        name='Test Laptop',
        asset_type='laptop',
        serial_number='SN123456',
        status='in_stock'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Create an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Create an admin authenticated API client."""
    api_client.force_authenticate(user=admin_user)
    return api_client


# =============================================================================
# Health Check Tests
# =============================================================================

@pytest.mark.django_db
class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check(self, api_client):
        """Test basic health check endpoint."""
        response = api_client.get('/api/health/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'healthy'
    
    def test_health_check_detailed(self, api_client):
        """Test detailed health check endpoint."""
        response = api_client.get('/api/health/detailed/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]
        assert 'checks' in response.data
    
    def test_liveness_probe(self, api_client):
        """Test Kubernetes liveness probe."""
        response = api_client.get('/api/health/live/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['alive'] is True
    
    def test_readiness_probe(self, api_client):
        """Test Kubernetes readiness probe."""
        response = api_client.get('/api/health/ready/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]


# =============================================================================
# Authentication Tests
# =============================================================================

@pytest.mark.django_db
class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_obtain_token(self, api_client, user):
        """Test JWT token obtain."""
        response = api_client.post('/api/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_obtain_token_invalid(self, api_client, user):
        """Test JWT token obtain with invalid credentials."""
        response = api_client.post('/api/auth/token/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token(self, api_client, user):
        """Test JWT token refresh."""
        # First get tokens
        token_response = api_client.post('/api/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        refresh_token = token_response.data['refresh']
        
        # Refresh the token
        response = api_client.post('/api/auth/token/refresh/', {
            'refresh': refresh_token
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
    
    def test_protected_endpoint_without_auth(self, api_client):
        """Test accessing protected endpoint without authentication."""
        response = api_client.get('/api/incidents/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_protected_endpoint_with_auth(self, authenticated_client):
        """Test accessing protected endpoint with authentication."""
        response = authenticated_client.get('/api/incidents/')
        assert response.status_code == status.HTTP_200_OK


# =============================================================================
# Incident API Tests
# =============================================================================

@pytest.mark.django_db
class TestIncidentAPI:
    """Test incident API endpoints."""
    
    def test_list_incidents(self, authenticated_client, incident):
        """Test listing incidents."""
        response = authenticated_client.get('/api/incidents/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)
    
    def test_create_incident(self, authenticated_client, user):
        """Test creating an incident."""
        data = {
            'title': 'New Test Incident',
            'description': 'Description of the issue',
            'impact': 2,
            'urgency': 2
        }
        response = authenticated_client.post('/api/incidents/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Test Incident'
        assert 'number' in response.data
    
    def test_retrieve_incident(self, authenticated_client, incident):
        """Test retrieving a single incident."""
        response = authenticated_client.get(f'/api/incidents/{incident.pk}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == incident.title
    
    def test_update_incident(self, admin_client, incident):
        """Test updating an incident."""
        data = {'title': 'Updated Title'}
        response = admin_client.patch(f'/api/incidents/{incident.pk}/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Title'
    
    def test_resolve_incident(self, authenticated_client, incident, it_support_user):
        """Test resolving an incident."""
        authenticated_client.force_authenticate(user=it_support_user)
        response = authenticated_client.post(f'/api/incidents/{incident.pk}/resolve/', {
            'resolution_notes': 'Issue fixed'
        })
        assert response.status_code == status.HTTP_200_OK
        
        incident.refresh_from_db()
        assert incident.state == 'resolved'
    
    def test_my_incidents(self, authenticated_client, incident, it_support_user):
        """Test getting assigned incidents."""
        incident.assigned_to = it_support_user
        incident.save()
        
        authenticated_client.force_authenticate(user=it_support_user)
        response = authenticated_client.get('/api/incidents/my_incidents/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_open_incidents(self, authenticated_client, incident):
        """Test getting open incidents."""
        response = authenticated_client.get('/api/incidents/open_incidents/')
        assert response.status_code == status.HTTP_200_OK


# =============================================================================
# Asset API Tests
# =============================================================================

@pytest.mark.django_db
class TestAssetAPI:
    """Test asset API endpoints."""
    
    def test_list_assets(self, authenticated_client, asset):
        """Test listing assets."""
        response = authenticated_client.get('/api/assets/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_asset(self, admin_client):
        """Test creating an asset."""
        data = {
            'name': 'New Laptop',
            'asset_type': 'laptop',
            'serial_number': 'SN789012',
            'status': 'in_stock'
        }
        response = admin_client.post('/api/assets/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Laptop'
    
    def test_retrieve_asset(self, authenticated_client, asset):
        """Test retrieving a single asset."""
        response = authenticated_client.get(f'/api/assets/{asset.pk}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['serial_number'] == asset.serial_number
    
    def test_available_assets(self, authenticated_client, asset):
        """Test getting available assets."""
        response = authenticated_client.get('/api/assets/available/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_assign_asset(self, admin_client, asset, user):
        """Test assigning an asset to a user."""
        response = admin_client.post(f'/api/assets/{asset.pk}/assign/', {
            'user_id': user.pk
        })
        assert response.status_code == status.HTTP_200_OK
        
        asset.refresh_from_db()
        assert asset.assigned_to == user
        assert asset.status == 'assigned'
    
    def test_return_asset(self, admin_client, asset, user):
        """Test returning an asset to stock."""
        asset.assign_to_user(user)
        
        response = admin_client.post(f'/api/assets/{asset.pk}/return_stock/')
        assert response.status_code == status.HTTP_200_OK
        
        asset.refresh_from_db()
        assert asset.status == 'in_stock'
        assert asset.assigned_to is None


# =============================================================================
# Service Request API Tests
# =============================================================================

@pytest.mark.django_db
class TestServiceRequestAPI:
    """Test service request API endpoints."""
    
    def test_list_requests(self, authenticated_client):
        """Test listing service requests."""
        response = authenticated_client.get('/api/requests/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_request(self, authenticated_client, user):
        """Test creating a service request."""
        data = {
            'title': 'New Laptop Request',
            'description': 'I need a new laptop',
            'request_type': 'hardware'
        }
        response = authenticated_client.post('/api/requests/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Laptop Request'
    
    def test_submit_request(self, authenticated_client, user):
        """Test submitting a service request."""
        request = ServiceRequest.objects.create(
            title='Test Request',
            description='Test description',
            request_type='software',
            requester=user,
            state='draft'
        )
        
        response = authenticated_client.post(f'/api/requests/{request.pk}/submit/')
        assert response.status_code == status.HTTP_200_OK
        
        request.refresh_from_db()
        assert request.state in ['awaiting_approval', 'approved']


# =============================================================================
# Department API Tests
# =============================================================================

@pytest.mark.django_db
class TestDepartmentAPI:
    """Test department API endpoints."""
    
    def test_list_departments(self, authenticated_client, department):
        """Test listing departments."""
        response = authenticated_client.get('/api/departments/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_department(self, admin_client):
        """Test creating a department."""
        data = {
            'name': 'Marketing',
            'code': 'MKT',
            'description': 'Marketing Department'
        }
        response = admin_client.post('/api/departments/', data)
        assert response.status_code == status.HTTP_201_CREATED


# =============================================================================
# Search API Tests
# =============================================================================

@pytest.mark.django_db
class TestSearchAPI:
    """Test search API endpoints."""
    
    def test_global_search(self, authenticated_client, incident, asset):
        """Test global search endpoint."""
        response = authenticated_client.get('/api/search/?q=test')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
    
    def test_search_suggestions(self, authenticated_client, incident):
        """Test search suggestions endpoint."""
        response = authenticated_client.get('/api/search/suggestions/?q=INC')
        assert response.status_code == status.HTTP_200_OK
        assert 'suggestions' in response.data
    
    def test_search_empty_query(self, authenticated_client):
        """Test search with empty query."""
        response = authenticated_client.get('/api/search/?q=')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# =============================================================================
# Metrics API Tests
# =============================================================================

@pytest.mark.django_db
class TestMetricsAPI:
    """Test metrics API endpoints."""
    
    def test_metrics_endpoint(self, api_client, incident, asset):
        """Test metrics endpoint."""
        response = api_client.get('/api/health/metrics/')
        assert response.status_code == status.HTTP_200_OK
        assert 'incidents' in response.data
        assert 'assets' in response.data
