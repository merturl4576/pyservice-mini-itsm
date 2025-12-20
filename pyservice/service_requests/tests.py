"""
Service Request Module Tests
PyService Mini-ITSM Platform

Tests for ServiceRequest model and approval workflow
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import ServiceRequest
from cmdb.models import AssetInventory

User = get_user_model()


@pytest.mark.django_db
class TestServiceRequestModel:
    """Test ServiceRequest model functionality"""
    
    def test_service_request_creation(self):
        """Test creating a service request"""
        requester = User.objects.create_user(username="user", password="test")
        sr = ServiceRequest.objects.create(
            title="New Software Request",
            description="Need Adobe Photoshop",
            requester=requester,
            request_type="software"
        )
        assert sr.title == "New Software Request"
        assert sr.requester == requester
        assert sr.number is not None  # Auto-generated
        assert sr.state == "draft"
    
    def test_submit_service_request(self):
        """Test submitting a service request"""
        requester = User.objects.create_user(username="user", password="test")
        sr = ServiceRequest.objects.create(
            title="Software Request",
            requester=requester,
            request_type="software"
        )
        sr.submit()
        assert sr.state == "awaiting_approval"
    
    def test_auto_assign_hardware_in_stock(self):
        """Test auto-assignment when hardware is in stock"""
        requester = User.objects.create_user(username="user", password="test")
        # Create inventory
        AssetInventory.objects.create(item_type="laptop", quantity=5)
        
        sr = ServiceRequest.objects.create(
            title="Laptop Request",
            requester=requester,
            request_type="hardware",
            asset_type="laptop"
        )
        # Should auto-assign since laptop is in stock
        result = sr.auto_assign_asset_if_available()
        assert result is True
        assert sr.state == "approved"
    
    def test_auto_assign_hardware_out_of_stock(self):
        """Test that request goes to approval when out of stock"""
        requester = User.objects.create_user(username="user", password="test")
        # No inventory created - out of stock
        
        sr = ServiceRequest.objects.create(
            title="Phone Request",
            requester=requester,
            request_type="hardware",
            asset_type="phone"
        )
        result = sr.auto_assign_asset_if_available()
        assert result is False
        # Should need approval
    
    def test_approve_service_request(self):
        """Test approving a service request"""
        requester = User.objects.create_user(username="user", password="test")
        manager = User.objects.create_user(username="manager", password="test", role="manager")
        sr = ServiceRequest.objects.create(
            title="Request",
            requester=requester,
            request_type="software",
            state="awaiting_approval"
        )
        result = sr.approve(manager, "Approved by manager")
        assert result is True
        assert sr.state == "approved"
        assert sr.approver == manager
        assert sr.approved_at is not None
    
    def test_reject_service_request(self):
        """Test rejecting a service request"""
        requester = User.objects.create_user(username="user", password="test")
        manager = User.objects.create_user(username="manager", password="test", role="manager")
        sr = ServiceRequest.objects.create(
            title="Request",
            requester=requester,
            request_type="software",
            state="awaiting_approval"
        )
        result = sr.reject(manager, "Budget constraints")
        assert result is True
        assert sr.state == "rejected"
        assert sr.approver == manager
        assert sr.rejected_at is not None
    
    def test_claim_service_request(self):
        """Test IT staff claiming a service request"""
        requester = User.objects.create_user(username="user", password="test")
        it_staff = User.objects.create_user(username="it", password="test", role="it_support")
        sr = ServiceRequest.objects.create(
            title="Request",
            requester=requester,
            request_type="software",
            state="approved"
        )
        result = sr.claim(it_staff)
        assert result is True
        assert sr.assigned_to == it_staff
        assert sr.state == "in_progress"
    
    def test_complete_service_request(self):
        """Test completing a service request"""
        requester = User.objects.create_user(username="user", password="test")
        it_staff = User.objects.create_user(username="it", password="test", role="it_support")
        sr = ServiceRequest.objects.create(
            title="Request",
            requester=requester,
            request_type="software",
            state="in_progress",
            assigned_to=it_staff
        )
        result = sr.complete("Software installed successfully")
        assert result is True
        assert sr.state == "completed"
        assert sr.completed_at is not None
    
    def test_cancel_service_request(self):
        """Test canceling a service request"""
        requester = User.objects.create_user(username="user", password="test")
        sr = ServiceRequest.objects.create(
            title="Request",
            requester=requester,
            request_type="software"
        )
        sr.cancel()
        assert sr.state == "cancelled"
