"""
CMDB (Configuration Management Database) Models
PyService Mini-ITSM Platform

This module implements ITIL-compliant asset management functionality:
- Department: Organizational units
- User: Extended Django user with department and role
- Asset: IT assets with status tracking
- AssetInventory: Company inventory of available items
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Department(models.Model):
    """
    Organizational department for user grouping.
    ITIL: Part of organizational structure for incident routing.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def save(self, *args, **kwargs):
        # Auto-generate code if not provided
        if not self.code:
            self.code = self.name[:20].upper().replace(' ', '_')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Extended User model with ITSM-specific fields.
    Extends AbstractUser to maintain Django's auth functionality.
    """
    ROLE_CHOICES = [
        ('staff', 'Staff'),
        ('it_support', 'IT Support'),
        ('technician', 'Technician'),
        ('manager', 'Manager'),
        ('admin', 'Administrator'),
    ]

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    phone = models.CharField(max_length=20, blank=True)
    employee_id = models.CharField(max_length=20, blank=True, unique=True, null=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    def get_available_assets(self):
        """
        ITIL Logic: When a staff member is created, suggest available 'In Stock' assets.
        Returns queryset of assets that can be assigned.
        """
        return Asset.objects.filter(status='in_stock')


class AssetInventory(models.Model):
    """
    Company inventory - how many of each item type the company has.
    """
    ITEM_TYPE_CHOICES = [
        ('laptop', 'Laptop'),
        ('desktop', 'Desktop'),
        ('monitor', 'Monitor'),
        ('phone', 'Phone'),
        ('printer', 'Printer'),
        ('network', 'Network Equipment'),
        ('software', 'Software License'),
        ('other', 'Other'),
    ]
    
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, unique=True)
    quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['item_type']
        verbose_name = 'Asset Inventory'
        verbose_name_plural = 'Asset Inventory'
    
    def __str__(self):
        return f"{self.get_item_type_display()}: {self.quantity}"
    
    @classmethod
    def get_or_create_inventory(cls, item_type):
        """Get or create inventory record for item type."""
        obj, created = cls.objects.get_or_create(item_type=item_type)
        return obj
    
    @classmethod
    def check_availability(cls, item_type):
        """Check if item type is available in stock."""
        try:
            inv = cls.objects.get(item_type=item_type)
            return inv.quantity > 0
        except cls.DoesNotExist:
            return False
    
    @classmethod
    def decrement(cls, item_type):
        """Decrement inventory for item type."""
        try:
            inv = cls.objects.get(item_type=item_type)
            if inv.quantity > 0:
                inv.quantity -= 1
                inv.save()
                return True
        except cls.DoesNotExist:
            pass
        return False


class Asset(models.Model):
    """
    IT Asset model for CMDB.
    Tracks hardware and software assets with their lifecycle status.
    """
    ASSET_TYPE_CHOICES = [
        ('laptop', 'Laptop'),
        ('desktop', 'Desktop'),
        ('monitor', 'Monitor'),
        ('phone', 'Phone'),
        ('printer', 'Printer'),
        ('network', 'Network Equipment'),
        ('software', 'Software License'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('assigned', 'Assigned'),
        ('under_review', 'Under Review'),
        ('declined', 'Declined'),
        ('in_repair', 'In Repair'),
        ('retired', 'Retired'),
    ]

    name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    model_name = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_stock')
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assets'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_assets'
    )
    
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    warranty_end_date = models.DateField(null=True, blank=True)
    
    location = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

    def assign_to_user(self, user):
        """Assign this asset to a user and update status."""
        self.assigned_to = user
        self.status = 'assigned'
        self.save()

    def return_to_stock(self):
        """Return asset to stock (unassign)."""
        self.assigned_to = None
        self.status = 'in_stock'
        self.save()

    def send_for_repair(self):
        """Mark asset as in repair."""
        self.status = 'in_repair'
        self.save()

    def retire(self):
        """Retire the asset."""
        self.assigned_to = None
        self.status = 'retired'
        self.save()
    
    def approve(self):
        """Admin approves the asset request."""
        if self.status == 'under_review':
            self.status = 'assigned'
            self.save()
            return True
        return False
    
    def decline(self):
        """Admin declines the asset request."""
        if self.status == 'under_review':
            self.status = 'declined'
            self.save()
            return True
        return False

