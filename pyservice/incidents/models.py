"""
Incident Management Models
PyService Mini-ITSM Platform

This module implements ITIL-compliant incident management:
- Impact + Urgency = Priority (Priority Matrix)
- SLA-based due date calculation
- State machine for incident lifecycle
"""

from django.db import models
from django.utils import timezone
from datetime import timedelta


class Incident(models.Model):
    """
    ITIL-Compliant Incident Model.
    
    Priority Matrix:
    - Priority is calculated based on Impact x Urgency
    - SLA due dates are set based on priority level
    """
    
    # Impact levels (How many users/services affected)
    IMPACT_CHOICES = [
        (1, '1 - High (Enterprise-wide)'),
        (2, '2 - Medium (Department-wide)'),
        (3, '3 - Low (Individual user)'),
    ]
    
    # Urgency levels (How time-sensitive)
    URGENCY_CHOICES = [
        (1, '1 - High (Critical business function)'),
        (2, '2 - Medium (Normal business function)'),
        (3, '3 - Low (Non-critical function)'),
    ]
    
    # Calculated Priority levels
    PRIORITY_CHOICES = [
        (1, 'P1 - Critical'),
        (2, 'P2 - High'),
        (3, 'P3 - Medium'),
        (4, 'P4 - Low'),
    ]
    
    # Incident lifecycle states
    STATE_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('needs_help', 'Needs Advanced Help'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    # SLA times in hours based on priority
    SLA_HOURS = {
        1: 4,    # Critical: 4 hours
        2: 24,   # High: 24 hours
        3: 48,   # Medium: 48 hours
        4: 72,   # Low: 72 hours
    }

    # Basic information
    number = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Location - where the caller is
    location = models.CharField(max_length=200, blank=True, help_text="Caller's location")
    
    # People involved
    caller = models.ForeignKey(
        'cmdb.User',
        on_delete=models.CASCADE,
        related_name='reported_incidents',
        help_text='User who reported the incident'
    )
    assigned_to = models.ForeignKey(
        'cmdb.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents',
        limit_choices_to={'role__in': ['it_support', 'technician', 'admin']},
        help_text='IT Staff assigned to resolve'
    )
    
    # Priority calculation fields
    impact = models.IntegerField(choices=IMPACT_CHOICES, default=3)
    urgency = models.IntegerField(choices=URGENCY_CHOICES, default=3)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, editable=False, default=4)
    
    # State management
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='new')
    
    # SLA tracking
    due_date = models.DateTimeField(null=True, blank=True, editable=False)
    sla_breached = models.BooleanField(default=False)
    
    # Resolution
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            models.Case(
                models.When(state='resolved', then=1),
                models.When(state='closed', then=2),
                default=0,
                output_field=models.IntegerField()
            ),
            'priority',
            '-created_at'
        ]
        verbose_name = 'Incident'
        verbose_name_plural = 'Incidents'

    def __str__(self):
        return f"{self.number}: {self.title}"

    def save(self, *args, **kwargs):
        # Generate incident number if new
        if not self.number:
            self.number = self._generate_incident_number()
        
        # Calculate priority based on Impact x Urgency matrix
        self.priority = self._calculate_priority()
        
        # Calculate SLA due date based on priority
        if not self.due_date:
            self.due_date = self._calculate_due_date()
        
        # Check SLA breach
        if self.due_date and timezone.now() > self.due_date and self.state not in ['resolved', 'closed']:
            self.sla_breached = True
        
        # Set resolved timestamp
        if self.state == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        
        super().save(*args, **kwargs)

    def _generate_incident_number(self):
        """Generate unique incident number like INC0001234"""
        last_incident = Incident.objects.order_by('-id').first()
        if last_incident and last_incident.number:
            try:
                last_num = int(last_incident.number.replace('INC', ''))
                return f"INC{str(last_num + 1).zfill(7)}"
            except ValueError:
                pass
        return "INC0000001"

    def _calculate_priority(self):
        """
        ITIL Priority Matrix:
        
        Impact/Urgency |  High(1)  |  Med(2)  |  Low(3)
        ---------------|-----------|----------|----------
        High(1)        |  P1       |  P2      |  P3
        Medium(2)      |  P2       |  P3      |  P4
        Low(3)         |  P3       |  P4      |  P4
        """
        matrix = {
            (1, 1): 1,  # High Impact + High Urgency = P1 Critical
            (1, 2): 2,  # High Impact + Medium Urgency = P2 High
            (1, 3): 3,  # High Impact + Low Urgency = P3 Medium
            (2, 1): 2,  # Medium Impact + High Urgency = P2 High
            (2, 2): 3,  # Medium Impact + Medium Urgency = P3 Medium
            (2, 3): 4,  # Medium Impact + Low Urgency = P4 Low
            (3, 1): 3,  # Low Impact + High Urgency = P3 Medium
            (3, 2): 4,  # Low Impact + Medium Urgency = P4 Low
            (3, 3): 4,  # Low Impact + Low Urgency = P4 Low
        }
        return matrix.get((self.impact, self.urgency), 4)

    def _calculate_due_date(self):
        """
        Calculate SLA due date based on priority.
        
        SLA Response Times:
        - P1 Critical: 4 hours
        - P2 High: 24 hours
        - P3 Medium: 48 hours
        - P4 Low: 72 hours
        """
        hours = self.SLA_HOURS.get(self.priority, 72)
        return timezone.now() + timedelta(hours=hours)

    def get_sla_status(self):
        """Get human-readable SLA status."""
        if self.state in ['resolved', 'closed']:
            if self.sla_breached:
                return "Resolved (SLA Breached)"
            return "Resolved (Within SLA)"
        
        if not self.due_date:
            return "No SLA"
        
        remaining = self.due_date - timezone.now()
        if remaining.total_seconds() < 0:
            hours_breach = abs(remaining.total_seconds()) / 3600
            return f"BREACHED by {int(hours_breach)} hours"
        
        hours = remaining.total_seconds() / 3600
        if hours < 1:
            return f"{int(remaining.total_seconds() / 60)} minutes remaining"
        return f"{int(hours)} hours remaining"

    # Workflow actions
    def claim(self, support_user):
        """Support staff claims this incident - I'll handle it."""
        if self.state in ['new', 'needs_help'] and (not self.assigned_to or self.state == 'needs_help'):
            self.state = 'in_progress'
            self.assigned_to = support_user
            self.save()
            return True
        return False

    def complete(self, notes=''):
        """Mark incident as resolved."""
        if self.state in ['in_progress', 'needs_help']:
            self.state = 'resolved'
            self.resolution_notes = notes
            self.resolved_at = timezone.now()
            self.save()
            return True
        return False

    def escalate(self, notes=''):
        """Incident needs advanced help from other support."""
        if self.state == 'in_progress':
            self.state = 'needs_help'
            self.resolution_notes = notes
            self.save()
            return True
        return False

