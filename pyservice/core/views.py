"""
Core App Views
PyService Mini-ITSM Platform
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ActivityLog


@login_required
def activity_log_list(request):
    """View recent activity logs (admin only)."""
    if request.user.role != 'admin':
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, 'Unauthorized access.')
        return redirect('dashboard')
    
    logs = ActivityLog.objects.all()[:100]
    return render(request, 'core/activity_log_list.html', {'logs': logs})
