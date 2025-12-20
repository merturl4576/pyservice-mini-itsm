"""
Service Request Models
PyService Mini-ITSM Platform

This module implements service request workflow:
- Draft → Awaiting Approval → Assigned/Closed
- Manager approval workflow
"""

from django.db import models
from django.utils import timezone


class ServiceRequest(models.Model):
    """
    Service Request with approval workflow.
    
    Workflow States:
    1. Draft - Initial state, not yet submitted
    2. Awaiting Approval - Submitted, waiting for manager
    3. Approved - Manager approved, ready for fulfillment
    4. Assigned - Assigned to IT for fulfillment
    5. In Progress - Being worked on
    6. Needs Help - Support needs advanced assistance
    7. Completed - Request fulfilled
    8. Rejected - Manager rejected the request
    9. Cancelled - Requester cancelled
    """
    
    STATE_CHOICES = [
        ('draft', 'Draft'),
        ('awaiting_approval', 'Awaiting Approval'),
        ('approved', 'Approved'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('needs_help', 'Needs Advanced Help'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    REQUEST_TYPE_CHOICES = [
        ('software', 'Software Installation'),
        ('hardware', 'Hardware Request'),
        ('access', 'Access/Permissions'),
        ('account', 'Account Creation'),
        ('email', 'Email/Distribution List'),
        ('other', 'Other'),
    ]

    # Request identification
    number = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, default='other')
    
    # Location - where the requester is
    location = models.CharField(max_length=200, blank=True, help_text="Requester's location")
    
    # Asset request fields (for hardware requests)
    requested_asset_type = models.CharField(
        max_length=20,
        choices=[],  # Will be populated from Asset.ASSET_TYPE_CHOICES
        null=True,
        blank=True,
        help_text="Type of asset being requested (for hardware requests)"
    )
    allocated_asset = models.ForeignKey(
        'cmdb.Asset',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_requests',
        help_text="Asset allocated for this request"
    )
    
    # People involved
    requester = models.ForeignKey(
        'cmdb.User',
        on_delete=models.CASCADE,
        related_name='service_requests'
    )
    approver = models.ForeignKey(
        'cmdb.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests_to_approve',
        limit_choices_to={'role': 'manager'}
    )
    assigned_to = models.ForeignKey(
        'cmdb.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requests',
        limit_choices_to={'role__in': ['it_support', 'technician', 'admin']}
    )
    
    # State and workflow
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='draft')
    
    # Approval tracking
    approval_notes = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    
    # Fulfillment tracking
    fulfillment_notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            models.Case(
                models.When(state='completed', then=1),
                default=0,
                output_field=models.IntegerField()
            ),
            '-created_at'
        ]
        verbose_name = 'Service Request'
        verbose_name_plural = 'Service Requests'

    def __str__(self):
        return f"{self.number}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_request_number()
        super().save(*args, **kwargs)

    def _generate_request_number(self):
        """Generate unique request number like REQ0001234"""
        last_request = ServiceRequest.objects.order_by('-id').first()
        if last_request and last_request.number:
            try:
                last_num = int(last_request.number.replace('REQ', ''))
                return f"REQ{str(last_num + 1).zfill(7)}"
            except ValueError:
                pass
        return "REQ0000001"

    # Workflow actions
    def auto_assign_asset_if_available(self):
        """
        Automatically assign asset if available in stock.
        If asset is available: auto-assign and approve request.
        If not available: set to awaiting_approval for admin decision.
        
        Returns:
            bool: True if asset was auto-assigned, False if needs approval
        """
        if not self.requested_asset_type:
            return False
        
        # Import here to avoid circular imports
        from cmdb.models import Asset
        
        # Find first available asset of requested type
        available_asset = Asset.objects.filter(
            asset_type=self.requested_asset_type,
            status='in_stock',
            assigned_to__isnull=True
        ).first()
        
        if available_asset:
            # Asset available - auto-assign it
            available_asset.assign_to_user(self.requester)
            self.allocated_asset = available_asset
            self.state = 'approved'  # Auto-approve since asset is available
            self.approved_at = timezone.now()
            self.approval_notes = 'Auto-approved: Asset available in stock'
            self.save()
            return True
        else:
            # No asset available - needs admin approval
            self.state = 'awaiting_approval'
            self.save()
            return False
    
    def submit(self):
        """
        Submit request.
        For hardware requests with asset type: auto-check stock and assign if available.
        For other requests: normal approval workflow.
        """
        if self.state == 'draft':
            if self.request_type == 'hardware' and self.requested_asset_type:
                # Hardware request - try auto-assignment
                self.auto_assign_asset_if_available()
            else:
                # Normal request - needs approval
                self.state = 'awaiting_approval'
                self.save()
            return True
        return False

    def approve(self, approver, notes=''):
        """Manager approves the request."""
        if self.state == 'awaiting_approval':
            self.state = 'approved'
            self.approver = approver
            self.approval_notes = notes
            self.approved_at = timezone.now()
            self.save()
            return True
        return False

    def reject(self, approver, notes=''):
        """Manager rejects the request."""
        if self.state == 'awaiting_approval':
            self.state = 'rejected'
            self.approver = approver
            self.approval_notes = notes
            self.rejected_at = timezone.now()
            self.save()
            return True
        return False

    def assign(self, assignee):
        """Assign to IT staff for fulfillment."""
        if self.state in ['approved', 'assigned']:
            self.state = 'assigned'
            self.assigned_to = assignee
            self.save()
            return True
        return False

    def claim(self, support_user):
        """Support staff claims this request - I'll handle it."""
        if self.state in ['draft', 'approved', 'needs_help'] and not self.assigned_to:
            self.state = 'in_progress'
            self.assigned_to = support_user
            self.save()
            return True
        elif self.state == 'needs_help':
            # Another support can take over
            self.state = 'in_progress'
            self.assigned_to = support_user
            self.save()
            return True
        return False

    def start_work(self):
        """Start working on the request."""
        if self.state == 'assigned':
            self.state = 'in_progress'
            self.save()
            return True
        return False

    def complete(self, notes=''):
        """Mark request as completed."""
        if self.state in ['assigned', 'in_progress', 'needs_help']:
            self.state = 'completed'
            self.fulfillment_notes = notes
            self.completed_at = timezone.now()
            self.save()
            return True
        return False

    def escalate(self, notes=''):
        """Request needs advanced help from other support."""
        if self.state == 'in_progress':
            self.state = 'needs_help'
            self.fulfillment_notes = notes
            self.save()
            return True
        return False

    def cancel(self):
        """Cancel the request."""
        if self.state in ['draft', 'awaiting_approval']:
            self.state = 'cancelled'
            self.save()
            return True
        return False

