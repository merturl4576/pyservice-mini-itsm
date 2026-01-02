"""
SLA Dashboard View
PyService Mini-ITSM Platform
SLA compliance monitoring and risk analysis
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
import json

from incidents.models import Incident


@login_required
def sla_dashboard(request):
    """SLA compliance and risk dashboard."""
    if request.user.role not in ['admin', 'manager', 'it_support']:
        messages.error(request, 'Unauthorized access.')
        return redirect('dashboard')
    
    now = timezone.now()
    
    # Overall SLA stats
    total_incidents = Incident.objects.count()
    sla_breached = Incident.objects.filter(sla_breached=True).count()
    sla_compliant = total_incidents - sla_breached
    sla_compliance_pct = round((sla_compliant / total_incidents * 100) if total_incidents > 0 else 100, 1)
    
    # Active incidents at risk (due date approaching)
    from datetime import timedelta
    warning_threshold = now + timedelta(hours=4)  # Due within 4 hours
    
    at_risk = Incident.objects.filter(
        due_date__lte=warning_threshold,
        sla_breached=False
    ).exclude(state__in=['resolved', 'closed']).order_by('due_date')
    
    # Already breached
    breached = Incident.objects.filter(
        sla_breached=True
    ).exclude(state__in=['resolved', 'closed']).order_by('-due_date')[:10]
    
    # SLA by priority
    priority_stats = []
    for priority_code, priority_name in Incident.PRIORITY_CHOICES:
        total_p = Incident.objects.filter(priority=priority_code).count()
        breached_p = Incident.objects.filter(priority=priority_code, sla_breached=True).count()
        compliant_p = total_p - breached_p
        pct = round((compliant_p / total_p * 100) if total_p > 0 else 100, 1)
        priority_stats.append({
            'priority': priority_name,
            'total': total_p,
            'compliant': compliant_p,
            'breached': breached_p,
            'percentage': pct,
        })
    
    # Chart data for SLA by priority
    chart_priority_data = json.dumps({
        'labels': [p['priority'] for p in priority_stats],
        'compliant': [p['compliant'] for p in priority_stats],
        'breached': [p['breached'] for p in priority_stats],
    })
    
    context = {
        'total_incidents': total_incidents,
        'sla_compliant': sla_compliant,
        'sla_breached': sla_breached,
        'sla_compliance_pct': sla_compliance_pct,
        'at_risk': at_risk,
        'breached': breached,
        'priority_stats': priority_stats,
        'chart_priority_data': chart_priority_data,
    }
    
    return render(request, 'sla_dashboard.html', context)
