"""
Calendar View
PyService Mini-ITSM Platform
SLA due dates and scheduling calendar
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from incidents.models import Incident
from service_requests.models import ServiceRequest


@login_required
def calendar_page(request):
    """Calendar view page."""
    return render(request, 'calendar.html')


@login_required
def calendar_events_api(request):
    """API endpoint for calendar events (FullCalendar format)."""
    events = []
    user = request.user
    
    # Get incidents with due dates - only show user's own incidents
    # User can see incidents they created (caller) or are assigned to
    from django.db.models import Q
    incidents = Incident.objects.exclude(state__in=['resolved', 'closed']).filter(
        due_date__isnull=False
    ).filter(
        Q(caller=user) | Q(assigned_to=user)
    )
    
    for inc in incidents:
        # Color based on priority
        if inc.priority == 1:
            color = '#ef4444'  # Critical - Red
        elif inc.priority == 2:
            color = '#f97316'  # High - Orange
        elif inc.priority == 3:
            color = '#eab308'  # Medium - Yellow
        else:
            color = '#22c55e'  # Low - Green
        
        # Check if SLA breached
        if inc.sla_breached:
            color = '#dc2626'  # Dark red for breached
        
        events.append({
            'id': f'inc-{inc.pk}',
            'title': inc.title[:40],
            'start': inc.due_date.isoformat(),
            'url': f'/incidents/{inc.pk}/',
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'type': 'incident',
                'priority': inc.get_priority_display(),
                'state': inc.get_state_display(),
            }
        })
    
    # Get service requests - only show user's own requests
    requests = ServiceRequest.objects.exclude(
        state__in=['completed', 'fulfilled', 'closed']
    ).filter(requester=user)
    
    for req in requests:
        events.append({
            'id': f'req-{req.pk}',
            'title': req.title[:40],
            'start': req.created_at.isoformat(),
            'url': f'/requests/{req.pk}/',
            'backgroundColor': '#3b82f6',  # Blue
            'borderColor': '#3b82f6',
            'extendedProps': {
                'type': 'request',
                'state': req.get_state_display(),
            }
        })
    
    return JsonResponse(events, safe=False)
