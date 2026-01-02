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
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count
        from django.db.models.functions import TruncMonth
        import json
        
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
        
        # Chart Data 1: Incident States Distribution (Pie Chart)
        incident_states = Incident.objects.values('state').annotate(count=Count('id'))
        state_labels = []
        state_data = []
        state_colors = {
            'new': '#3b82f6',
            'in_progress': '#8b5cf6', 
            'resolved': '#10b981',
            'closed': '#6b7280',
            'escalated': '#f59e0b'
        }
        state_bg_colors = []
        for state in incident_states:
            state_display = dict(Incident.STATE_CHOICES).get(state['state'], state['state'])
            state_labels.append(state_display)
            state_data.append(state['count'])
            state_bg_colors.append(state_colors.get(state['state'], '#94a3b8'))
        
        context['chart_incident_states'] = json.dumps({
            'labels': state_labels,
            'data': state_data,
            'colors': state_bg_colors
        })
        
        # Chart Data 2: Monthly Trend (Line Chart - Last 6 months)
        now = timezone.now()
        months_data = []
        months_labels = []
        incidents_by_month = []
        requests_by_month = []
        
        for i in range(5, -1, -1):
            month_start = (now - timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i > 0:
                month_end = (now - timedelta(days=30*(i-1))).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                month_end = now
            
            month_label = month_start.strftime('%b %Y')
            months_labels.append(month_label)
            
            inc_count = Incident.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            incidents_by_month.append(inc_count)
            
            req_count = ServiceRequest.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            requests_by_month.append(req_count)
        
        context['chart_monthly_trend'] = json.dumps({
            'labels': months_labels,
            'incidents': incidents_by_month,
            'requests': requests_by_month
        })
        
        # Chart Data 3: SLA Compliance (Doughnut Chart)
        total_incidents = Incident.objects.count()
        sla_breached = Incident.objects.filter(sla_breached=True).count()
        sla_compliant = total_incidents - sla_breached
        sla_compliance_pct = round((sla_compliant / total_incidents * 100) if total_incidents > 0 else 100, 1)
        
        context['chart_sla_compliance'] = json.dumps({
            'compliant': sla_compliant,
            'breached': sla_breached,
            'percentage': sla_compliance_pct
        })
        context['sla_compliance_pct'] = sla_compliance_pct
        
        # Employee Performance Leaderboard
        # Get IT staff from IT Support and Technician roles
        from cmdb.models import User
        from django.db.models import Count, Q
        
        # Get all IT staff (it_support, technician roles)
        it_staff = User.objects.filter(role__in=['it_support', 'technician'])
        
        # Calculate performance for each staff member
        leaderboard = []
        for staff in it_staff:
            # Count resolved incidents
            resolved_incidents = Incident.objects.filter(
                assigned_to=staff,
                state__in=['resolved', 'closed']
            ).count()
            
            # Count completed service requests
            completed_requests = ServiceRequest.objects.filter(
                assigned_to=staff,
                state__in=['completed', 'fulfilled', 'closed']
            ).count()
            
            total_completed = resolved_incidents + completed_requests
            
            if total_completed > 0 or True:  # Show all IT staff
                leaderboard.append({
                    'user': staff,
                    'resolved_incidents': resolved_incidents,
                    'completed_requests': completed_requests,
                    'total': total_completed,
                })
        
        # Sort by total (descending)
        leaderboard.sort(key=lambda x: x['total'], reverse=True)
        
        # Add rank
        for i, entry in enumerate(leaderboard, 1):
            entry['rank'] = i
        
        context['leaderboard'] = leaderboard
        
    elif role == 'staff':
        # Staff sees their own service requests and assets
        # Active/open items first, then resolved
        my_open_requests = ServiceRequest.objects.filter(
            requester=user
        ).exclude(state__in=['closed', 'fulfilled']).order_by('-created_at')
        
        my_resolved_requests = ServiceRequest.objects.filter(
            requester=user,
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

@login_required
def staff_leaderboard(request):
    """Staff performance leaderboard - Admin only."""
    from cmdb.models import User, Department
    from django.shortcuts import redirect
    from django.contrib import messages
    from datetime import datetime
    from django.utils import timezone
    
    if request.user.role != 'admin':
        messages.error(request, 'Only administrators can access the leaderboard.')
        return redirect('dashboard')
    
    # Get selected month for filtering
    selected_month = request.GET.get('month', '')
    month_filter = None
    
    if selected_month:
        try:
            year, month = map(int, selected_month.split('-'))
            month_filter = (year, month)
        except:
            pass
    
    def get_department_leaderboard(department_name, month_filter=None):
        """Calculate leaderboard for a specific department."""
        try:
            dept = Department.objects.get(name__icontains=department_name)
            staff = User.objects.filter(department=dept)
        except Department.DoesNotExist:
            # If department doesn't exist, use role-based filtering
            if 'support' in department_name.lower():
                staff = User.objects.filter(role='it_support')
            else:
                staff = User.objects.filter(role='technician')
        
        leaderboard = []
        for member in staff:
            # Base querysets
            incidents_qs = Incident.objects.filter(
                assigned_to=member,
                state__in=['resolved', 'closed']
            )
            requests_qs = ServiceRequest.objects.filter(
                assigned_to=member,
                state__in=['completed', 'fulfilled', 'closed']
            )
            
            # Apply month filter if specified
            if month_filter:
                year, month = month_filter
                incidents_qs = incidents_qs.filter(
                    updated_at__year=year,
                    updated_at__month=month
                )
                requests_qs = requests_qs.filter(
                    updated_at__year=year,
                    updated_at__month=month
                )
            
            resolved_incidents = incidents_qs.count()
            completed_requests = requests_qs.count()
            total = resolved_incidents + completed_requests
            
            leaderboard.append({
                'user': member,
                'resolved_incidents': resolved_incidents,
                'completed_requests': completed_requests,
                'total': total,
            })
        
        leaderboard.sort(key=lambda x: x['total'], reverse=True)
        
        for i, entry in enumerate(leaderboard, 1):
            entry['rank'] = i
        
        return leaderboard
    
    # Get leaderboards for both departments
    servicenow_leaderboard = get_department_leaderboard('ServiceNow Support', month_filter)
    it_leaderboard = get_department_leaderboard('IT Department', month_filter)
    
    # Generate monthly rankings - only show completed months starting from December 2025
    from dateutil.relativedelta import relativedelta
    from datetime import datetime
    now = timezone.now()
    
    # Start date: December 2025 (first month data was collected)
    start_date = datetime(2025, 12, 1, tzinfo=now.tzinfo)
    
    monthly_rankings = []
    
    # Only include months that are complete (before current month)
    current_month_start = datetime(now.year, now.month, 1, tzinfo=now.tzinfo)
    check_date = start_date
    
    while check_date < current_month_start:
        month_start = check_date
        month_end = check_date + relativedelta(months=1)
        month_label = check_date.strftime('%B %Y')
        
        # Get all IT staff for this month
        all_staff = User.objects.filter(role__in=['it_support', 'technician'])
        month_leaderboard = []
        
        for staff in all_staff:
            # Use date range for timezone compatibility
            incidents = Incident.objects.filter(
                assigned_to=staff,
                state__in=['resolved', 'closed'],
                updated_at__gte=month_start,
                updated_at__lt=month_end
            ).count()
            
            requests = ServiceRequest.objects.filter(
                assigned_to=staff,
                state__in=['completed', 'fulfilled', 'closed'],
                updated_at__gte=month_start,
                updated_at__lt=month_end
            ).count()
            
            total = incidents + requests
            month_leaderboard.append({
                'user': staff,
                'incidents': incidents,
                'requests': requests,
                'total': total,
            })
        
        month_leaderboard.sort(key=lambda x: x['total'], reverse=True)
        for idx, entry in enumerate(month_leaderboard, 1):
            entry['rank'] = idx
        
        monthly_rankings.append({
            'month': month_label,
            'leaderboard': month_leaderboard[:5]  # Top 5 only
        })
        
        check_date = check_date + relativedelta(months=1)
    
    context = {
        'servicenow_leaderboard': servicenow_leaderboard,
        'it_leaderboard': it_leaderboard,
        'monthly_rankings': monthly_rankings,
    }
    
    return render(request, 'staff_leaderboard.html', context)


@login_required
def staff_detail(request, user_id):
    """Staff performance detail - shows all completed tickets with dates."""
    from cmdb.models import User
    from django.shortcuts import redirect, get_object_or_404
    from django.contrib import messages
    
    if request.user.role != 'admin':
        messages.error(request, 'Only administrators can access staff details.')
        return redirect('dashboard')
    
    staff_member = get_object_or_404(User, pk=user_id)
    
    # Get all resolved incidents
    resolved_incidents = Incident.objects.filter(
        assigned_to=staff_member,
        state__in=['resolved', 'closed']
    ).order_by('-updated_at')
    
    # Get all completed requests
    completed_requests = ServiceRequest.objects.filter(
        assigned_to=staff_member,
        state__in=['completed', 'fulfilled', 'closed']
    ).order_by('-updated_at')
    
    # Calculate monthly stats
    from collections import defaultdict
    monthly_stats = defaultdict(lambda: {'incidents': 0, 'requests': 0, 'total': 0})
    
    for incident in resolved_incidents:
        month_key = incident.updated_at.strftime('%Y-%m')
        monthly_stats[month_key]['incidents'] += 1
        monthly_stats[month_key]['total'] += 1
    
    for req in completed_requests:
        month_key = req.updated_at.strftime('%Y-%m')
        monthly_stats[month_key]['requests'] += 1
        monthly_stats[month_key]['total'] += 1
    
    # Sort monthly stats by date
    sorted_monthly = sorted(monthly_stats.items(), reverse=True)
    
    context = {
        'staff_member': staff_member,
        'resolved_incidents': resolved_incidents,
        'completed_requests': completed_requests,
        'monthly_stats': sorted_monthly,
        'total_incidents': resolved_incidents.count(),
        'total_requests': completed_requests.count(),
        'total_score': resolved_incidents.count() + completed_requests.count(),
    }
    
    return render(request, 'staff_detail.html', context)

