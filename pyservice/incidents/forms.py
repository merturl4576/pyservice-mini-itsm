"""
Incident Forms
PyService Mini-ITSM Platform
"""

from django import forms
from .models import Incident


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['title', 'description', 'location', 'caller', 'assigned_to', 'impact', 'urgency', 
                  'state', 'resolution_notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'required': True}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Building A, Floor 3'}),
            'caller': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'impact': forms.Select(attrs={'class': 'form-select'}),
            'urgency': forms.Select(attrs={'class': 'form-select'}),
            'state': forms.Select(attrs={'class': 'form-select'}),
            'resolution_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
