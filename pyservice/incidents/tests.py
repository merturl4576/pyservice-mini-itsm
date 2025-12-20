"""
Incident Module Tests
PyService Mini-ITSM Platform

Tests for Incident model including priority calculation and SLA tracking
"""

import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import Incident

User = get_user_model()


@pytest.mark.django_db
class TestIncidentModel:
    """Test Incident model functionality"""
    
    def test_incident_creation(self):
        """Test creating an incident"""
        caller = User.objects.create_user(username="caller", password="test")
        incident = Incident.objects.create(
            title="Computer not working",
            description="My computer won't start",
            caller=caller,
            impact=1,
            urgency=1
        )
        assert incident.title == "Computer not working"
        assert incident.caller == caller
        assert incident.number is not None  # Auto-generated
    
    def test_priority_calculation_critical(self):
        """Test P1 (Critical) priority calculation"""
        caller = User.objects.create_user(username="test", password="test")
        incident = Incident.objects.create(
            title="Server Down",
            caller=caller,
            impact=1,  # High
            urgency=1  # High
        )
        assert incident.priority == 1  # P1 - Critical
    
    def test_priority_calculation_high(self):
        """Test P2 (High) priority calculation"""
        caller = User.objects.create_user(username="test", password="test")
        incident = Incident.objects.create(
            title="Email Issue",
            caller=caller,
            impact=1,  # High
            urgency=2  # Medium
        )
        assert incident.priority == 2  # P2 - High
    
    def test_priority_calculation_low(self):
        """Test P4 (Low) priority calculation"""
        caller = User.objects.create_user(username="test", password="test")
        incident = Incident.objects.create(
            title="Minor Issue",
            caller=caller,
            impact=3,  # Low
            urgency=3  # Low
        )
        assert incident.priority == 4  # P4 - Low
    
    def test_sla_deadline_critical(self):
        """Test SLA deadline for critical incidents (4 hours)"""
        caller = User.objects.create_user(username="test", password="test")
        incident = Incident.objects.create(
            title="Critical",
            caller=caller,
            impact=1,
            urgency=1
        )
        # P1 should have 4 hour SLA
        expected_due = incident.created_at + timedelta(hours=4)
        # Allow 1 second tolerance
        assert abs((incident.due_date - expected_due).total_seconds()) < 1
    
    def test_sla_deadline_high(self):
        """Test SLA deadline for high priority incidents (24 hours)"""
        caller = User.objects.create_user(username="test", password="test")
        incident = Incident.objects.create(
            title="High Priority",
            caller=caller,
            impact=1,
            urgency=2
        )
        # P2 should have 24 hour SLA
        expected_due = incident.created_at + timedelta(hours=24)
        assert abs((incident.due_date - expected_due).total_seconds()) < 1
    
    def test_sla_status_on_time(self):
        """Test SLA status when incident is on time"""
        caller = User.objects.create_user(username="test", password="test")
        incident = Incident.objects.create(
            title="Test",
            caller=caller,
            impact=3,
            urgency=3
        )
        # Just created, should be on time
        assert incident.get_sla_status() == "On Time"
    
    def test_claim_incident(self):
        """Test claiming an incident"""
        caller = User.objects.create_user(username="caller", password="test")
        support = User.objects.create_user(username="support", password="test", role="it_support")
        incident = Incident.objects.create(
            title="Test",
            caller=caller,
            impact=2,
            urgency=2
        )
        result = incident.claim(support)
        assert result is True
        assert incident.assigned_to == support
        assert incident.state == "in_progress"
    
    def test_complete_incident(self):
        """Test completing an incident"""
        caller = User.objects.create_user(username="caller", password="test")
        incident = Incident.objects.create(
            title="Test",
            caller=caller,
            impact=2,
            urgency=2
        )
        result = incident.complete("Issue fixed")
        assert result is True
        assert incident.state == "resolved"
        assert incident.resolved_at is not None
    
    def test_escalate_incident(self):
        """Test escalating an incident"""
        caller = User.objects.create_user(username="caller", password="test")
        support = User.objects.create_user(username="support", password="test", role="it_support")
        incident = Incident.objects.create(
            title="Test",
            caller=caller,
            impact=2,
            urgency=2,
            assigned_to=support,
            state="in_progress"
        )
        result = incident.escalate("Needs senior help")
        assert result is True
        assert incident.state == "escalated"
