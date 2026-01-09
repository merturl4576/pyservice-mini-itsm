"""
Pytest Configuration
PyService Mini-ITSM Platform

Shared fixtures for all tests.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from cmdb.models import Department, Asset
from incidents.models import Incident
from service_requests.models import ServiceRequest

User = get_user_model()


# =============================================================================
# User Fixtures
# =============================================================================

@pytest.fixture
def user_password():
    """Default password for test users."""
    return 'testpass123'


@pytest.fixture
def staff_user(db, user_password):
    """Create a staff user."""
    return User.objects.create_user(
        username='staffuser',
        email='staff@example.com',
        password=user_password,
        first_name='Staff',
        last_name='User',
        role='staff'
    )


@pytest.fixture
def it_support(db, user_password):
    """Create an IT support user."""
    return User.objects.create_user(
        username='itsupport',
        email='itsupport@example.com',
        password=user_password,
        first_name='IT',
        last_name='Support',
        role='it_support'
    )


@pytest.fixture
def technician(db, user_password):
    """Create a technician user."""
    return User.objects.create_user(
        username='technician',
        email='technician@example.com',
        password=user_password,
        first_name='Tech',
        last_name='Nician',
        role='technician'
    )


@pytest.fixture
def manager(db, user_password):
    """Create a manager user."""
    return User.objects.create_user(
        username='manager',
        email='manager@example.com',
        password=user_password,
        first_name='Manager',
        last_name='User',
        role='manager'
    )


@pytest.fixture
def admin(db, user_password):
    """Create an admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password=user_password,
        first_name='Admin',
        last_name='User',
        role='admin'
    )


# =============================================================================
# Department Fixtures
# =============================================================================

@pytest.fixture
def it_department(db):
    """Create IT department."""
    return Department.objects.create(
        name='IT Department',
        code='IT',
        description='Information Technology Department'
    )


@pytest.fixture
def hr_department(db):
    """Create HR department."""
    return Department.objects.create(
        name='Human Resources',
        code='HR',
        description='Human Resources Department'
    )


@pytest.fixture
def finance_department(db):
    """Create Finance department."""
    return Department.objects.create(
        name='Finance',
        code='FIN',
        description='Finance Department'
    )


# =============================================================================
# Asset Fixtures
# =============================================================================

@pytest.fixture
def laptop(db):
    """Create a laptop asset."""
    return Asset.objects.create(
        name='Dell Latitude 5520',
        asset_type='laptop',
        serial_number='DELL001',
        model_name='Latitude 5520',
        manufacturer='Dell',
        status='in_stock'
    )


@pytest.fixture
def monitor(db):
    """Create a monitor asset."""
    return Asset.objects.create(
        name='LG 27" Monitor',
        asset_type='monitor',
        serial_number='LG001',
        model_name='27UK850',
        manufacturer='LG',
        status='in_stock'
    )


@pytest.fixture
def assigned_laptop(db, staff_user):
    """Create an assigned laptop asset."""
    asset = Asset.objects.create(
        name='MacBook Pro',
        asset_type='laptop',
        serial_number='APPLE001',
        model_name='MacBook Pro 14"',
        manufacturer='Apple',
        status='assigned',
        assigned_to=staff_user
    )
    return asset


# =============================================================================
# Incident Fixtures
# =============================================================================

@pytest.fixture
def critical_incident(db, staff_user):
    """Create a P1 critical incident."""
    return Incident.objects.create(
        title='Server Down',
        description='Main production server is not responding',
        caller=staff_user,
        impact=1,
        urgency=1
    )


@pytest.fixture
def high_incident(db, staff_user):
    """Create a P2 high priority incident."""
    return Incident.objects.create(
        title='Email Not Working',
        description='Cannot send or receive emails',
        caller=staff_user,
        impact=1,
        urgency=2
    )


@pytest.fixture
def medium_incident(db, staff_user):
    """Create a P3 medium priority incident."""
    return Incident.objects.create(
        title='Slow Computer',
        description='Computer is running slowly',
        caller=staff_user,
        impact=2,
        urgency=2
    )


@pytest.fixture
def low_incident(db, staff_user):
    """Create a P4 low priority incident."""
    return Incident.objects.create(
        title='Software Update',
        description='Need to update software to latest version',
        caller=staff_user,
        impact=3,
        urgency=3
    )


@pytest.fixture
def assigned_incident(db, staff_user, it_support):
    """Create an assigned incident."""
    incident = Incident.objects.create(
        title='Assigned Incident',
        description='This incident is assigned',
        caller=staff_user,
        impact=2,
        urgency=2,
        assigned_to=it_support,
        state='in_progress'
    )
    return incident


@pytest.fixture
def resolved_incident(db, staff_user, it_support):
    """Create a resolved incident."""
    incident = Incident.objects.create(
        title='Resolved Incident',
        description='This incident was resolved',
        caller=staff_user,
        impact=2,
        urgency=2,
        assigned_to=it_support,
        state='resolved',
        resolution_notes='Issue fixed by restarting the service'
    )
    return incident


# =============================================================================
# Service Request Fixtures
# =============================================================================

@pytest.fixture
def hardware_request(db, staff_user):
    """Create a hardware service request."""
    return ServiceRequest.objects.create(
        title='New Laptop Request',
        description='I need a new laptop for my work',
        request_type='hardware',
        requester=staff_user,
        state='draft'
    )


@pytest.fixture
def software_request(db, staff_user):
    """Create a software service request."""
    return ServiceRequest.objects.create(
        title='Adobe Creative Suite',
        description='I need Adobe Creative Suite for design work',
        request_type='software',
        requester=staff_user,
        state='draft'
    )


@pytest.fixture
def pending_request(db, staff_user):
    """Create a pending service request."""
    return ServiceRequest.objects.create(
        title='Pending Request',
        description='This request is awaiting approval',
        request_type='hardware',
        requester=staff_user,
        state='awaiting_approval'
    )


# =============================================================================
# API Client Fixtures
# =============================================================================

@pytest.fixture
def api_client():
    """Create an API client."""
    return APIClient()


@pytest.fixture
def staff_client(api_client, staff_user):
    """Create a staff authenticated API client."""
    api_client.force_authenticate(user=staff_user)
    return api_client


@pytest.fixture
def support_client(api_client, it_support):
    """Create an IT support authenticated API client."""
    api_client.force_authenticate(user=it_support)
    return api_client


@pytest.fixture
def manager_client(api_client, manager):
    """Create a manager authenticated API client."""
    api_client.force_authenticate(user=manager)
    return api_client


@pytest.fixture
def admin_client(api_client, admin):
    """Create an admin authenticated API client."""
    api_client.force_authenticate(user=admin)
    return api_client


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture
def sample_data(db, it_department, staff_user, it_support, laptop, critical_incident, hardware_request):
    """Create a complete set of sample data."""
    staff_user.department = it_department
    staff_user.save()
    
    return {
        'department': it_department,
        'staff_user': staff_user,
        'it_support': it_support,
        'laptop': laptop,
        'incident': critical_incident,
        'request': hardware_request,
    }
