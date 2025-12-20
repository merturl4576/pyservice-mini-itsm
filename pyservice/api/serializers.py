"""
API Serializers
PyService Mini-ITSM Platform

Serializers for Django REST Framework API endpoints.
"""

from rest_framework import serializers
from cmdb.models import Department, User, Asset
from incidents.models import Incident
from service_requests.models import ServiceRequest


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description', 'created_at']
        read_only_fields = ['created_at']


class UserSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'department', 'department_name', 'role', 'phone', 'employee_id']
        read_only_fields = ['id']


class AssetSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    asset_type_display = serializers.CharField(source='get_asset_type_display', read_only=True)
    
    class Meta:
        model = Asset
        fields = ['id', 'name', 'asset_type', 'asset_type_display', 'serial_number', 
                  'model_name', 'manufacturer', 'status', 'status_display',
                  'assigned_to', 'assigned_to_name', 'location', 'purchase_date',
                  'purchase_cost', 'warranty_end_date', 'notes', 'created_at']
        read_only_fields = ['created_at']


class IncidentSerializer(serializers.ModelSerializer):
    caller_name = serializers.CharField(source='caller.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    sla_status = serializers.CharField(source='get_sla_status', read_only=True)
    
    class Meta:
        model = Incident
        fields = ['id', 'number', 'title', 'description', 
                  'caller', 'caller_name', 'assigned_to', 'assigned_to_name',
                  'impact', 'urgency', 'priority', 'priority_display',
                  'state', 'state_display', 'due_date', 'sla_breached', 'sla_status',
                  'resolution_notes', 'resolved_at', 'created_at', 'updated_at']
        read_only_fields = ['number', 'priority', 'due_date', 'sla_breached', 'created_at', 'updated_at']


class ServiceRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = ['id', 'number', 'title', 'description', 'request_type', 'request_type_display',
                  'requester', 'requester_name', 'approver', 'assigned_to', 'assigned_to_name',
                  'state', 'state_display', 'approval_notes', 'approved_at', 'rejected_at',
                  'fulfillment_notes', 'completed_at', 'created_at', 'updated_at']
        read_only_fields = ['number', 'approved_at', 'rejected_at', 'completed_at', 'created_at', 'updated_at']
