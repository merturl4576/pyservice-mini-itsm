"""
CMDB Forms
PyService Mini-ITSM Platform
"""

from django import forms
from .models import Department, Asset


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'asset_type', 'serial_number', 'model_name', 'manufacturer',
                  'status', 'assigned_to', 'purchase_date', 'purchase_cost', 
                  'warranty_end_date', 'location', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'asset_type': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'warranty_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only name and asset_type are required
        self.fields['serial_number'].required = False
        self.fields['model_name'].required = False
        self.fields['manufacturer'].required = False
        self.fields['status'].required = False
        self.fields['assigned_to'].required = False
        self.fields['purchase_date'].required = False
        self.fields['purchase_cost'].required = False
        self.fields['warranty_end_date'].required = False
        self.fields['location'].required = False
        self.fields['notes'].required = False
