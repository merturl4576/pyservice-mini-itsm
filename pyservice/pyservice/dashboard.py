"""
Dashboard Views
PyService Mini-ITSM Platform
Role-based dashboard views for different user types
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from incidents.models import Incident
from service_requests.models import ServiceRequest
from cmdb.models import Asset


@login_required
def dashboard(request):
    """Main dashboard view with role-based content."""
    user = request.user
    role = user.role
    
    # Base context
    context = {
        'user_role': role,
    }
    
    if role == 'admin':
        # Admin sees everything
        context.update({
            'open_incidents': Incident.objects.exclude(state__in=['resolved', 'closed']).count(),
            'critical_incidents': Incident.objects.filter(priority=1).exclude(state__in=['resolved', 'closed']).count(),
            'pending_requests': ServiceRequest.objects.filter(state='awaiting_approval').count(),
            'total_assets': Asset.objects.count(),
            'recent_incidents': Incident.objects.all().order_by('-created_at')[:10],
            'recent_requests': ServiceRequest.objects.all().order_by('-created_at')[:10],
            'recent_assets': Asset.objects.all().order_by('-created_at')[:10],
            'pending_approval_requests': ServiceRequest.objects.filter(state='awaiting_approval')[:5],
            'sla_breached_incidents': Incident.objects.filter(sla_breached=True).exclude(state__in=['resolved', 'closed'])[:5],
        })
        
    elif role == 'staff':
        # Staff sees their own service requests and assets
        # Active/open items first, then resolved
        my_open_requests = ServiceRequest.objects.filter(
            requested_by=user
        ).exclude(state__in=['closed', 'fulfilled']).order_by('-created_at')
        
        my_resolved_requests = ServiceRequest.objects.filter(
            requested_by=user,
            state__in=['closed', 'fulfilled']
        ).order_by('-updated_at')[:5]
        
        my_active_assets = Asset.objects.filter(
            assigned_to=user
        ).exclude(status__in=['retired']).order_by('-updated_at')
        
        my_retired_assets = Asset.objects.filter(
            assigned_to=user,
            status='retired'
        ).order_by('-updated_at')[:5]
        
        context.update({
            'my_open_requests': my_open_requests,
            'my_resolved_requests': my_resolved_requests,
            'my_active_assets': my_active_assets,
            'my_retired_assets': my_retired_assets,
            'open_requests_count': my_open_requests.count(),
            'active_assets_count': my_active_assets.count(),
        })
        
    elif role == 'it_support':
        # IT Support sees active incidents and assets they're working on
        # Active/in-progress items first, then resolved
        active_incidents = Incident.objects.filter(
            assigned_to=user
        ).exclude(state__in=['resolved', 'closed']).order_by('-priority', '-created_at')
        
        resolved_incidents = Incident.objects.filter(
            assigned_to=user,
            state__in=['resolved', 'closed']
        ).order_by('-updated_at')[:5]
        
        active_assets = Asset.objects.filter(
            status__in=['in_repair', 'under_review']
        ).order_by('-updated_at')
        
        resolved_assets = Asset.objects.filter(
            status__in=['assigned', 'in_stock']
        ).order_by('-updated_at')[:5]
        
        context.update({
            'active_incidents': active_incidents,
            'resolved_incidents': resolved_incidents,
            'active_assets': active_assets,
            'resolved_assets': resolved_assets,
            'active_incidents_count': active_incidents.count(),
            'active_assets_count': active_assets.count(),
        })
        
    elif role == 'technician':
        # Technician sees technical incidents and service requests
        # Active/unassigned technical issues first, then assigned ones, then resolved
        unassigned_incidents = Incident.objects.filter(
            assigned_to__isnull=True
        ).exclude(state__in=['resolved', 'closed']).order_by('-priority', '-created_at')
        
        my_active_incidents = Incident.objects.filter(
            assigned_to=user
        ).exclude(state__in=['resolved', 'closed']).order_by('-priority', '-created_at')
        
        my_resolved_incidents = Incident.objects.filter(
            assigned_to=user,
            state__in=['resolved', 'closed']
        ).order_by('-updated_at')[:5]
        
        # Technical service requests (e.g., software installation, hardware setup)
        unassigned_requests = ServiceRequest.objects.filter(
            assigned_to__isnull=True
        ).exclude(state__in=['closed', 'fulfilled']).order_by('-created_at')
        
        my_active_requests = ServiceRequest.objects.filter(
            assigned_to=user
        ).exclude(state__in=['closed', 'fulfilled']).order_by('-created_at')
        
        my_resolved_requests = ServiceRequest.objects.filter(
            assigned_to=user,
            state__in=['closed', 'fulfilled']
        ).order_by('-updated_at')[:5]
        
        context.update({
            'unassigned_incidents': unassigned_incidents,
            'my_active_incidents': my_active_incidents,
            'my_resolved_incidents': my_resolved_incidents,
            'unassigned_requests': unassigned_requests,
            'my_active_requests': my_active_requests,
            'my_resolved_requests': my_resolved_requests,
            'unassigned_count': unassigned_incidents.count() + unassigned_requests.count(),
            'active_count': my_active_incidents.count() + my_active_requests.count(),
        })
        
    else:
        # Default view for other roles (technician, manager)
        context.update({
            'open_incidents': Incident.objects.exclude(state__in=['resolved', 'closed']).count(),
            'critical_incidents': Incident.objects.filter(priority=1).exclude(state__in=['resolved', 'closed']).count(),
            'pending_requests': ServiceRequest.objects.filter(state='awaiting_approval').count(),
            'total_assets': Asset.objects.count(),
            'recent_incidents': Incident.objects.all().order_by('-created_at')[:5],
            'pending_approval_requests': ServiceRequest.objects.filter(state='awaiting_approval')[:5],
            'sla_breached_incidents': Incident.objects.filter(sla_breached=True).exclude(state__in=['resolved', 'closed'])[:5],
        })
    
    return render(request, 'dashboard.html', context)
