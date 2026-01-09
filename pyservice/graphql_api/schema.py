"""
GraphQL API - Schema
PyService Mini-ITSM Platform

Main GraphQL schema combining all types and resolvers.
"""

import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model

from cmdb.models import Department, Asset
from incidents.models import Incident
from service_requests.models import ServiceRequest
from knowledge.models import Article, Category


User = get_user_model()


# =============================================================================
# Object Types
# =============================================================================

class DepartmentType(DjangoObjectType):
    class Meta:
        model = Department
        fields = ('id', 'name', 'code', 'description', 'created_at', 'updated_at')


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                  'role', 'department', 'phone', 'employee_id', 'is_active')
    
    full_name = graphene.String()
    
    def resolve_full_name(self, info):
        return self.get_full_name()


class AssetType(DjangoObjectType):
    class Meta:
        model = Asset
        fields = ('id', 'name', 'asset_type', 'serial_number', 'model_name',
                  'manufacturer', 'status', 'assigned_to', 'purchase_date',
                  'purchase_cost', 'warranty_end_date', 'location', 'notes',
                  'created_at', 'updated_at')


class IncidentType(DjangoObjectType):
    class Meta:
        model = Incident
        fields = ('id', 'number', 'title', 'description', 'state', 'priority',
                  'impact', 'urgency', 'caller', 'assigned_to', 'due_date',
                  'sla_breached', 'resolution_notes', 'created_at', 'resolved_at')
    
    sla_status = graphene.String()
    priority_display = graphene.String()
    
    def resolve_sla_status(self, info):
        return self.get_sla_status()
    
    def resolve_priority_display(self, info):
        return self.get_priority_display()


class ServiceRequestType(DjangoObjectType):
    class Meta:
        model = ServiceRequest
        fields = ('id', 'number', 'title', 'description', 'state', 'request_type',
                  'requester', 'assigned_to', 'approved_by', 'approval_notes',
                  'created_at', 'completed_at')


class DashboardStats(graphene.ObjectType):
    """Dashboard statistics."""
    
    total_incidents = graphene.Int()
    open_incidents = graphene.Int()
    sla_breached = graphene.Int()
    sla_compliance = graphene.Float()
    total_assets = graphene.Int()
    pending_requests = graphene.Int()
    
    def resolve_total_incidents(self, info):
        return Incident.objects.count()
    
    def resolve_open_incidents(self, info):
        return Incident.objects.exclude(state__in=['resolved', 'closed']).count()
    
    def resolve_sla_breached(self, info):
        return Incident.objects.filter(sla_breached=True).count()
    
    def resolve_sla_compliance(self, info):
        total = Incident.objects.count()
        breached = Incident.objects.filter(sla_breached=True).count()
        return ((total - breached) / max(total, 1)) * 100
    
    def resolve_total_assets(self, info):
        return Asset.objects.count()
    
    def resolve_pending_requests(self, info):
        return ServiceRequest.objects.filter(state='awaiting_approval').count()


# =============================================================================
# Queries
# =============================================================================

class Query(graphene.ObjectType):
    """Root query for GraphQL API."""
    
    # Single item queries
    incident = graphene.Field(IncidentType, id=graphene.ID(), number=graphene.String())
    asset = graphene.Field(AssetType, id=graphene.ID())
    user = graphene.Field(UserType, id=graphene.ID())
    department = graphene.Field(DepartmentType, id=graphene.ID())
    service_request = graphene.Field(ServiceRequestType, id=graphene.ID())
    
    # List queries
    all_incidents = graphene.List(IncidentType, state=graphene.String(), limit=graphene.Int())
    all_assets = graphene.List(AssetType, status=graphene.String(), limit=graphene.Int())
    all_users = graphene.List(UserType, role=graphene.String())
    all_departments = graphene.List(DepartmentType)
    all_service_requests = graphene.List(ServiceRequestType, state=graphene.String())
    
    # Custom queries
    open_incidents = graphene.List(IncidentType)
    my_incidents = graphene.List(IncidentType)
    sla_at_risk = graphene.List(IncidentType)
    
    # Dashboard stats
    dashboard_stats = graphene.Field(DashboardStats)
    
    def resolve_incident(self, info, id=None, number=None):
        if id:
            return Incident.objects.get(pk=id)
        if number:
            return Incident.objects.get(number=number)
        return None
    
    def resolve_asset(self, info, id):
        return Asset.objects.get(pk=id)
    
    def resolve_user(self, info, id):
        return User.objects.get(pk=id)
    
    def resolve_department(self, info, id):
        return Department.objects.get(pk=id)
    
    def resolve_service_request(self, info, id):
        return ServiceRequest.objects.get(pk=id)
    
    def resolve_all_incidents(self, info, state=None, limit=None):
        qs = Incident.objects.all()
        if state:
            qs = qs.filter(state=state)
        if limit:
            qs = qs[:limit]
        return qs
    
    def resolve_all_assets(self, info, status=None, limit=None):
        qs = Asset.objects.all()
        if status:
            qs = qs.filter(status=status)
        if limit:
            qs = qs[:limit]
        return qs
    
    def resolve_all_users(self, info, role=None):
        qs = User.objects.all()
        if role:
            qs = qs.filter(role=role)
        return qs
    
    def resolve_all_departments(self, info):
        return Department.objects.all()
    
    def resolve_all_service_requests(self, info, state=None):
        qs = ServiceRequest.objects.all()
        if state:
            qs = qs.filter(state=state)
        return qs
    
    def resolve_open_incidents(self, info):
        return Incident.objects.exclude(state__in=['resolved', 'closed'])
    
    def resolve_my_incidents(self, info):
        user = info.context.user
        if user.is_authenticated:
            return Incident.objects.filter(assigned_to=user)
        return Incident.objects.none()
    
    def resolve_sla_at_risk(self, info):
        from django.utils import timezone
        from datetime import timedelta
        
        warning_threshold = timezone.now() + timedelta(hours=4)
        return Incident.objects.filter(
            state__in=['new', 'in_progress'],
            sla_breached=False,
            due_date__lte=warning_threshold
        )
    
    def resolve_dashboard_stats(self, info):
        return DashboardStats()


# =============================================================================
# Mutations
# =============================================================================

class CreateIncident(graphene.Mutation):
    """Create a new incident."""
    
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        impact = graphene.Int(required=True)
        urgency = graphene.Int(required=True)
    
    incident = graphene.Field(IncidentType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, title, description, impact, urgency):
        user = info.context.user
        if not user.is_authenticated:
            return CreateIncident(success=False, message="Authentication required")
        
        incident = Incident.objects.create(
            title=title,
            description=description,
            impact=impact,
            urgency=urgency,
            caller=user
        )
        
        return CreateIncident(incident=incident, success=True, message="Incident created")


class UpdateIncidentState(graphene.Mutation):
    """Update incident state."""
    
    class Arguments:
        incident_id = graphene.ID(required=True)
        state = graphene.String(required=True)
        notes = graphene.String()
    
    incident = graphene.Field(IncidentType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, incident_id, state, notes=None):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateIncidentState(success=False, message="Authentication required")
        
        try:
            incident = Incident.objects.get(pk=incident_id)
            
            if state == 'resolved':
                incident.complete(notes or '')
            elif state == 'escalated':
                incident.escalate(notes or '')
            elif state == 'in_progress':
                incident.claim(user)
            else:
                incident.state = state
                incident.save()
            
            return UpdateIncidentState(incident=incident, success=True, message=f"State updated to {state}")
        except Incident.DoesNotExist:
            return UpdateIncidentState(success=False, message="Incident not found")


class CreateServiceRequest(graphene.Mutation):
    """Create a new service request."""
    
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        request_type = graphene.String(required=True)
    
    request = graphene.Field(ServiceRequestType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, title, description, request_type):
        user = info.context.user
        if not user.is_authenticated:
            return CreateServiceRequest(success=False, message="Authentication required")
        
        request = ServiceRequest.objects.create(
            title=title,
            description=description,
            request_type=request_type,
            requester=user
        )
        
        return CreateServiceRequest(request=request, success=True, message="Request created")


class Mutation(graphene.ObjectType):
    """Root mutation for GraphQL API."""
    
    create_incident = CreateIncident.Field()
    update_incident_state = UpdateIncidentState.Field()
    create_service_request = CreateServiceRequest.Field()


# =============================================================================
# Schema
# =============================================================================

schema = graphene.Schema(query=Query, mutation=Mutation)
