"""
API Views
PyService Mini-ITSM Platform

ViewSets for CRUD operations via REST API.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from cmdb.models import Department, User, Asset
from incidents.models import Incident
from service_requests.models import ServiceRequest
from .serializers import (
    DepartmentSerializer, UserSerializer, AssetSerializer,
    IncidentSerializer, ServiceRequestSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """API endpoint for departments."""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def assets(self, request, pk=None):
        """Get all assets assigned to this user."""
        user = self.get_object()
        assets = user.assets.all()
        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data)


class AssetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for IT assets.
    Supports full CRUD operations.
    """
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'asset_type', 'assigned_to']
    search_fields = ['name', 'serial_number', 'model_name']
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available (in stock) assets."""
        assets = Asset.objects.filter(status='in_stock')
        serializer = self.get_serializer(assets, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign asset to a user."""
        asset = self.get_object()
        user_id = request.data.get('user_id')
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
                asset.assign_to_user(user)
                return Response({'status': 'Asset assigned successfully'})
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def return_stock(self, request, pk=None):
        """Return asset to stock."""
        asset = self.get_object()
        asset.return_to_stock()
        return Response({'status': 'Asset returned to stock'})


class IncidentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for incidents.
    Implements ITIL incident management.
    """
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['state', 'priority', 'assigned_to', 'sla_breached']
    search_fields = ['number', 'title', 'description']
    
    @action(detail=False, methods=['get'])
    def my_incidents(self, request):
        """Get incidents assigned to current user."""
        incidents = Incident.objects.filter(assigned_to=request.user)
        serializer = self.get_serializer(incidents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def open_incidents(self, request):
        """Get all open (non-closed) incidents."""
        incidents = Incident.objects.exclude(state__in=['resolved', 'closed'])
        serializer = self.get_serializer(incidents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an incident."""
        incident = self.get_object()
        incident.state = 'resolved'
        incident.resolution_notes = request.data.get('resolution_notes', '')
        incident.save()
        return Response({'status': 'Incident resolved'})


class ServiceRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for service requests.
    Implements approval workflow.
    """
    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['state', 'request_type', 'assigned_to']
    search_fields = ['number', 'title', 'description']
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit request for approval."""
        req = self.get_object()
        if req.submit():
            return Response({'status': 'Request submitted for approval'})
        return Response({'error': 'Cannot submit request in current state'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a request."""
        req = self.get_object()
        notes = request.data.get('notes', '')
        if req.approve(request.user, notes):
            return Response({'status': 'Request approved'})
        return Response({'error': 'Cannot approve request in current state'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a request."""
        req = self.get_object()
        notes = request.data.get('notes', '')
        if req.reject(request.user, notes):
            return Response({'status': 'Request rejected'})
        return Response({'error': 'Cannot reject request in current state'}, 
                       status=status.HTTP_400_BAD_REQUEST)
