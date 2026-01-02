"""
Reports Views
PyService Mini-ITSM Platform
Generate PDF and Excel reports
"""

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import io

from incidents.models import Incident
from service_requests.models import ServiceRequest
from cmdb.models import Asset, User, Department


@login_required
def reports_dashboard(request):
    """Main reports page."""
    if request.user.role not in ['admin', 'manager']:
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, 'Only administrators and managers can access reports.')
        return redirect('dashboard')
    
    now = timezone.now()
    
    # Basic stats for the report page
    context = {
        'total_incidents': Incident.objects.count(),
        'open_incidents': Incident.objects.exclude(state__in=['resolved', 'closed']).count(),
        'total_requests': ServiceRequest.objects.count(),
        'pending_requests': ServiceRequest.objects.filter(state='awaiting_approval').count(),
        'total_assets': Asset.objects.count(),
        'total_users': User.objects.count(),
        'total_departments': Department.objects.count(),
    }
    
    return render(request, 'reports/dashboard.html', context)


@login_required
def export_incidents_csv(request):
    """Export incidents to CSV."""
    if request.user.role not in ['admin', 'manager']:
        return HttpResponse('Unauthorized', status=403)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="incidents_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Number', 'Title', 'State', 'Priority', 'Impact', 'Urgency', 
                     'Caller', 'Assigned To', 'Created At', 'Due Date', 'SLA Breached'])
    
    incidents = Incident.objects.all().order_by('-created_at')
    for inc in incidents:
        writer.writerow([
            inc.number,
            inc.title,
            inc.get_state_display(),
            inc.get_priority_display(),
            inc.get_impact_display(),
            inc.get_urgency_display(),
            str(inc.caller) if inc.caller else '',
            str(inc.assigned_to) if inc.assigned_to else '',
            inc.created_at.strftime('%Y-%m-%d %H:%M'),
            inc.due_date.strftime('%Y-%m-%d %H:%M') if inc.due_date else '',
            'Yes' if inc.sla_breached else 'No',
        ])
    
    return response


@login_required
def export_requests_csv(request):
    """Export service requests to CSV."""
    if request.user.role not in ['admin', 'manager']:
        return HttpResponse('Unauthorized', status=403)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="requests_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Number', 'Title', 'State', 'Request Type', 'Requester', 
                     'Assigned To', 'Created At', 'Approved At'])
    
    requests = ServiceRequest.objects.all().order_by('-created_at')
    for req in requests:
        writer.writerow([
            req.number,
            req.title,
            req.get_state_display(),
            req.get_request_type_display() if hasattr(req, 'get_request_type_display') else '',
            str(req.requester) if req.requester else '',
            str(req.assigned_to) if req.assigned_to else '',
            req.created_at.strftime('%Y-%m-%d %H:%M'),
            req.approved_at.strftime('%Y-%m-%d %H:%M') if hasattr(req, 'approved_at') and req.approved_at else '',
        ])
    
    return response


@login_required
def export_assets_csv(request):
    """Export assets to CSV."""
    if request.user.role not in ['admin', 'manager']:
        return HttpResponse('Unauthorized', status=403)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="assets_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Type', 'Status', 'Serial Number', 'Assigned To', 
                     'Location', 'Purchase Date', 'Purchase Cost'])
    
    assets = Asset.objects.all().order_by('-created_at')
    for asset in assets:
        writer.writerow([
            asset.name,
            asset.get_asset_type_display(),
            asset.get_status_display(),
            asset.serial_number or '',
            str(asset.assigned_to) if asset.assigned_to else '',
            asset.location or '',
            asset.purchase_date.strftime('%Y-%m-%d') if asset.purchase_date else '',
            str(asset.purchase_cost) if asset.purchase_cost else '',
        ])
    
    return response


@login_required
def monthly_summary(request):
    """Generate monthly summary report view."""
    if request.user.role not in ['admin', 'manager']:
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, 'Unauthorized access.')
        return redirect('dashboard')
    
    # Get selected month (default: current)
    month_str = request.GET.get('month', timezone.now().strftime('%Y-%m'))
    try:
        year, month = map(int, month_str.split('-'))
        month_start = datetime(year, month, 1, tzinfo=timezone.get_current_timezone())
    except:
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate month end
    if month_start.month == 12:
        month_end = month_start.replace(year=month_start.year + 1, month=1)
    else:
        month_end = month_start.replace(month=month_start.month + 1)
    
    # Get stats for the month
    incidents_created = Incident.objects.filter(
        created_at__gte=month_start,
        created_at__lt=month_end
    ).count()
    
    incidents_resolved = Incident.objects.filter(
        state__in=['resolved', 'closed'],
        updated_at__gte=month_start,
        updated_at__lt=month_end
    ).count()
    
    requests_created = ServiceRequest.objects.filter(
        created_at__gte=month_start,
        created_at__lt=month_end
    ).count()
    
    requests_completed = ServiceRequest.objects.filter(
        state__in=['completed', 'fulfilled'],
        updated_at__gte=month_start,
        updated_at__lt=month_end
    ).count()
    
    # SLA compliance
    total_incidents_month = Incident.objects.filter(
        created_at__gte=month_start,
        created_at__lt=month_end
    ).count()
    sla_breached_month = Incident.objects.filter(
        created_at__gte=month_start,
        created_at__lt=month_end,
        sla_breached=True
    ).count()
    sla_compliance = round((total_incidents_month - sla_breached_month) / total_incidents_month * 100, 1) if total_incidents_month > 0 else 100
    
    context = {
        'month_start': month_start,
        'incidents_created': incidents_created,
        'incidents_resolved': incidents_resolved,
        'requests_created': requests_created,
        'requests_completed': requests_completed,
        'sla_compliance': sla_compliance,
        'sla_breached': sla_breached_month,
    }
    
    return render(request, 'reports/monthly_summary.html', context)
