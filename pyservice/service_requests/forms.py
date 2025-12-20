"""
Service Request Forms
PyService Mini-ITSM Platform
"""

from django import forms
from .models import ServiceRequest


class ServiceRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamically populate asset type choices from Asset model
        from cmdb.models import Asset
        self.fields['requested_asset_type'].choices = [('', '--- Select Asset Type ---')] + list(Asset.ASSET_TYPE_CHOICES)
        self.fields['requested_asset_type'].required = False
        
    class Meta:
        model = ServiceRequest
        fields = ['title', 'description', 'request_type', 'requested_asset_type', 'location', 'requester', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'required': True}),
            'request_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_request_type'}),
            'requested_asset_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_requested_asset_type'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Building A, Floor 3, Room 301'}),
            'requester': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }
