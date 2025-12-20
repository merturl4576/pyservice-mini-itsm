"""
CMDB Module Tests
PyService Mini-ITSM Platform

Tests for Department, User, Asset, and AssetInventory models
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Department, Asset, AssetInventory

User = get_user_model()


@pytest.mark.django_db
class TestDepartmentModel:
    """Test Department model functionality"""
    
    def test_department_creation(self):
        """Test creating a department"""
        dept = Department.objects.create(
            name="IT Department",
            description="Information Technology"
        )
        assert dept.name == "IT Department"
        assert dept.code == "IT_DEPARTMENT"  # Auto-generated
    
    def test_department_str(self):
        """Test department string representation"""
        dept = Department.objects.create(name="HR")
        assert str(dept) == "HR"


@pytest.mark.django_db
class TestUserModel:
    """Test User model functionality"""
    
    def test_user_creation_with_department(self):
        """Test creating a user with department"""
        dept = Department.objects.create(name="Engineering")
        user = User.objects.create_user(
            username="john",
            email="john@example.com",
            password="testpass123",
            department=dept,
            role="staff"
        )
        assert user.username == "john"
        assert user.department == dept
        assert user.role == "staff"
    
    def test_get_available_assets(self):
        """Test that users can see available assets"""
        user = User.objects.create_user(username="test", password="test")
        Asset.objects.create(
            name="Laptop 1",
            asset_type="laptop",
            status="in_stock"
        )
        Asset.objects.create(
            name="Laptop 2",
            asset_type="laptop",
            status="assigned"
        )
        available = user.get_available_assets()
        assert available.count() == 1


@pytest.mark.django_db
class TestAssetInventoryModel:
    """Test AssetInventory model functionality"""
    
    def test_inventory_creation(self):
        """Test creating inventory record"""
        inv = AssetInventory.objects.create(
            item_type="laptop",
            quantity=10
        )
        assert inv.quantity == 10
        assert inv.item_type == "laptop"
    
    def test_check_availability(self):
        """Test checking if items are available"""
        AssetInventory.objects.create(item_type="laptop", quantity=5)
        assert AssetInventory.check_availability("laptop") is True
        assert AssetInventory.check_availability("phone") is False
    
    def test_decrement_inventory(self):
        """Test decrementing inventory"""
        inv = AssetInventory.objects.create(item_type="laptop", quantity=5)
        result = AssetInventory.decrement("laptop")
        assert result is True
        inv.refresh_from_db()
        assert inv.quantity == 4


@pytest.mark.django_db
class TestAssetModel:
    """Test Asset model functionality"""
    
    def test_asset_creation(self):
        """Test creating an asset"""
        asset = Asset.objects.create(
            name="Dell Laptop",
            asset_type="laptop",
            serial_number="ABC123",
            status="in_stock"
        )
        assert asset.name == "Dell Laptop"
        assert asset.status == "in_stock"
    
    def test_assign_to_user(self):
        """Test assigning asset to user"""
        user = User.objects.create_user(username="test", password="test")
        asset = Asset.objects.create(
            name="Laptop",
            asset_type="laptop",
            status="in_stock"
        )
        asset.assign_to_user(user)
        assert asset.assigned_to == user
        assert asset.status == "assigned"
    
    def test_return_to_stock(self):
        """Test returning asset to stock"""
        user = User.objects.create_user(username="test", password="test")
        asset = Asset.objects.create(
            name="Laptop",
            asset_type="laptop",
            status="assigned",
            assigned_to=user
        )
        asset.return_to_stock()
        assert asset.assigned_to is None
        assert asset.status == "in_stock"
    
    def test_asset_approve(self):
        """Test approving an asset request"""
        asset = Asset.objects.create(
            name="Laptop",
            asset_type="laptop",
            status="under_review"
        )
        result = asset.approve()
        assert result is True
        assert asset.status == "assigned"
    
    def test_asset_decline(self):
        """Test declining an asset request"""
        asset = Asset.objects.create(
            name="Laptop",
            asset_type="laptop",
            status="under_review"
        )
        result = asset.decline()
        assert result is True
        assert asset.status == "declined"
