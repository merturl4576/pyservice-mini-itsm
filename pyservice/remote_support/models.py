"""
Remote Support Models
PyService Mini-ITSM Platform

Models for remote support session management.
"""

import secrets
import string
from django.db import models
from django.conf import settings
from django.utils import timezone


def generate_session_code():
    """Generate a unique 8-character session code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(8))


class RemoteSupportSession(models.Model):
    """Remote support session between user and IT technician."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    session_code = models.CharField(
        max_length=8, 
        unique=True, 
        default=generate_session_code,
        editable=False
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_requests'
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='support_sessions'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    anydesk_id = models.CharField(
        max_length=50,
        help_text="User's AnyDesk ID for remote connection"
    )
    is_voice_active = models.BooleanField(
        default=False,
        help_text="Whether voice-to-text features are currently active"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Session notes
    technician_notes = models.TextField(blank=True, help_text="Notes from technician after session")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Remote Support Session'
        verbose_name_plural = 'Remote Support Sessions'
    
    def __str__(self):
        return f"{self.session_code} - {self.subject}"
    
    def accept(self, technician):
        """Accept the session by a technician."""
        if self.status == 'pending':
            self.technician = technician
            self.status = 'accepted'
            self.accepted_at = timezone.now()
            self.save()
            return True
        return False
    
    def start(self):
        """Start the session."""
        if self.status == 'accepted':
            self.status = 'in_progress'
            self.save()
            return True
        return False
    
    def complete(self, notes=''):
        """Complete the session."""
        if self.status in ['accepted', 'in_progress']:
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.technician_notes = notes
            self.save()
            return True
        return False
    
    def cancel(self):
        """Cancel the session."""
        if self.status in ['pending', 'accepted']:
            self.status = 'cancelled'
            self.save()
            return True
        return False
    
    @property
    def duration(self):
        """Calculate session duration."""
        if self.accepted_at and self.completed_at:
            return self.completed_at - self.accepted_at
        return None
    
    def get_priority_color(self):
        """Get Bootstrap color class for priority."""
        colors = {
            'low': 'success',
            'medium': 'info',
            'high': 'warning',
            'urgent': 'danger',
        }
        return colors.get(self.priority, 'secondary')
    
    def get_status_color(self):
        """Get Bootstrap color class for status."""
        colors = {
            'pending': 'warning',
            'accepted': 'info',
            'in_progress': 'primary',
            'completed': 'success',
            'cancelled': 'secondary',
        }
        return colors.get(self.status, 'secondary')


class SessionMessage(models.Model):
    """Chat messages within a support session."""
    
    session = models.ForeignKey(
        RemoteSupportSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}"


class VoiceTranscript(models.Model):
    """Voice transcripts from speech-to-text during support session."""
    
    session = models.ForeignKey(
        RemoteSupportSession,
        on_delete=models.CASCADE,
        related_name='voice_transcripts'
    )
    speaker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.speaker.username}: {self.text[:50]}"
