"""
Incident Views
PyService Mini-ITSM Platform
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Incident
from .forms import IncidentForm
from cmdb.models import User


@login_required
def incident_list(request):
    """List all incidents with filtering."""
    incidents = Incident.objects.all()
    
    # Apply filters
    state = request.GET.get('state')
    if state:
        incidents = incidents.filter(state=state)
    
    priority = request.GET.get('priority')
    if priority:
        incidents = incidents.filter(priority=priority)
    
    search = request.GET.get('search')
    if search:
        incidents = incidents.filter(title__icontains=search)
    
    # Pagination
    paginator = Paginator(incidents, 20)
    page = request.GET.get('page')
    incidents = paginator.get_page(page)
    
    return render(request, 'incidents/incident_list.html', {'incidents': incidents})


@login_required
def incident_detail(request, pk):
    """View incident details."""
    incident = get_object_or_404(Incident, pk=pk)
    return render(request, 'incidents/incident_detail.html', {'incident': incident})


@login_required
def incident_create(request):
    """Create new incident."""
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            # Non-admin users can only create incidents for themselves
            if request.user.role != 'admin':
                incident.caller = request.user
            incident.save()
            messages.success(request, 'Incident created successfully.')
            return redirect('incident_list')
    else:
        form = IncidentForm()
        # Pre-fill caller for non-admin users
        if request.user.role != 'admin':
            form.initial['caller'] = request.user.pk
    
    users = User.objects.all()
    it_users = User.objects.filter(role__in=['it_support', 'technician', 'admin'])
    is_admin = request.user.role == 'admin'
    return render(request, 'incidents/incident_form.html', {
        'form': form,
        'users': users,
        'it_users': it_users,
        'is_admin': is_admin
    })


@login_required
def incident_update(request, pk):
    """Update existing incident."""
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == 'POST':
        form = IncidentForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            messages.success(request, 'Incident updated successfully.')
            return redirect('incident_detail', pk=pk)
    else:
        form = IncidentForm(instance=incident)
    
    users = User.objects.all()
    it_users = User.objects.filter(role__in=['it_support', 'technician', 'admin'])
    is_admin = request.user.role == 'admin'
    return render(request, 'incidents/incident_form.html', {
        'form': form,
        'users': users,
        'it_users': it_users,
        'is_admin': is_admin
    })


@login_required
def incident_claim(request, pk):
    """Support staff claims this incident - I'll handle it."""
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == 'POST':
        # Only support roles can claim
        if request.user.role in ['it_support', 'technician', 'admin']:
            if incident.claim(request.user):
                messages.success(request, f'You are now assigned to this incident.')
            else:
                messages.error(request, 'Cannot claim this incident.')
        else:
            messages.error(request, 'Only support staff can claim incidents.')
    return redirect('incident_list')


@login_required
def incident_complete(request, pk):
    """Mark incident as resolved."""
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == 'POST':
        # Only assigned user or admin can complete
        if request.user == incident.assigned_to or request.user.role == 'admin':
            if incident.complete():
                messages.success(request, 'Incident marked as resolved!')
            else:
                messages.error(request, 'Cannot complete this incident.')
        else:
            messages.error(request, 'Only the assigned support can complete this incident.')
    return redirect('incident_list')


@login_required
def incident_escalate(request, pk):
    """Incident needs advanced help."""
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == 'POST':
        # Only assigned user can escalate
        if request.user == incident.assigned_to or request.user.role == 'admin':
            if incident.escalate('Needs advanced assistance'):
                messages.warning(request, 'Incident escalated - needs advanced help.')
            else:
                messages.error(request, 'Cannot escalate this incident.')
        else:
            messages.error(request, 'Only the assigned support can escalate this incident.')
    return redirect('incident_list')


@login_required
def incident_delete(request, pk):
    """Delete an incident - Admin only."""
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == 'POST':
        # Only admin can delete
        if request.user.role == 'admin':
            incident_number = incident.number
            incident.delete()
            messages.success(request, f'Incident {incident_number} deleted successfully.')
        else:
            messages.error(request, 'Only administrators can delete incidents.')
    return redirect('incident_list')
