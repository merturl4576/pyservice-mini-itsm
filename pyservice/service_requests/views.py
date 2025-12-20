"""
Service Request Views
PyService Mini-ITSM Platform
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ServiceRequest
from .forms import ServiceRequestForm
from cmdb.models import User


@login_required
def request_list(request):
    """List all service requests."""
    requests = ServiceRequest.objects.all()
    return render(request, 'service_requests/request_list.html', {'requests': requests})


@login_required
def request_detail(request, pk):
    """View service request details."""
    request_obj = get_object_or_404(ServiceRequest, pk=pk)
    return render(request, 'service_requests/request_detail.html', {'request_obj': request_obj})


@login_required
def request_create(request):
    """Create new service request."""
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            # Non-admin users can only create requests for themselves
            if request.user.role != 'admin':
                service_request.requester = request.user
            service_request.save()
            messages.success(request, 'Service request created successfully.')
            return redirect('request_list')
    else:
        form = ServiceRequestForm()
        # Pre-fill requester for non-admin users
        if request.user.role != 'admin':
            form.initial['requester'] = request.user.pk
    
    users = User.objects.all()
    it_users = User.objects.filter(role__in=['it_support', 'technician', 'admin'])
    is_admin = request.user.role == 'admin'
    return render(request, 'service_requests/request_form.html', {
        'form': form,
        'users': users,
        'it_users': it_users,
        'is_admin': is_admin
    })


@login_required
def request_update(request, pk):
    """Update existing service request."""
    request_obj = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, instance=request_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service request updated successfully.')
            return redirect('request_detail', pk=pk)
    else:
        form = ServiceRequestForm(instance=request_obj)
    
    users = User.objects.all()
    it_users = User.objects.filter(role__in=['it_support', 'technician', 'admin'])
    return render(request, 'service_requests/request_form.html', {
        'form': form,
        'users': users,
        'it_users': it_users
    })


@login_required
def request_submit(request, pk):
    """Submit request for approval."""
    request_obj = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == 'POST':
        if request_obj.submit():
            messages.success(request, 'Request submitted for approval.')
        else:
            messages.error(request, 'Cannot submit request in current state.')
    return redirect('request_detail', pk=pk)


@login_required
def request_approve(request, pk):
    """Approve a service request."""
    request_obj = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == 'POST':
        if request_obj.approve(request.user):
            messages.success(request, 'Request approved.')
        else:
            messages.error(request, 'Cannot approve request in current state.')
    return redirect('request_detail', pk=pk)


@login_required
def request_reject(request, pk):
    """Reject a service request."""
    request_obj = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == 'POST':
        if request_obj.reject(request.user):
            messages.warning(request, 'Request rejected.')
        else:
            messages.error(request, 'Cannot reject request in current state.')
    return redirect('request_detail', pk=pk)


@login_required
def request_claim(request, pk):
    """Support staff claims this request - I'll handle it."""
    request_obj = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == 'POST':
        # Only support roles can claim
        if request.user.role in ['it_support', 'technician', 'admin']:
            if request_obj.claim(request.user):
                messages.success(request, f'You are now assigned to this request.')
            else:
                messages.error(request, 'Cannot claim this request.')
        else:
            messages.error(request, 'Only support staff can claim requests.')
    return redirect('request_list')


@login_required
def request_complete(request, pk):
    """Mark request as completed."""
    request_obj = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == 'POST':
        # Only assigned user or admin can complete
        if request.user == request_obj.assigned_to or request.user.role == 'admin':
            if request_obj.complete():
                messages.success(request, 'Request marked as completed!')
            else:
                messages.error(request, 'Cannot complete this request.')
        else:
            messages.error(request, 'Only the assigned support can complete this request.')
    return redirect('request_list')


@login_required
def request_escalate(request, pk):
    """Request needs advanced help."""
    request_obj = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == 'POST':
        # Only assigned user can escalate
        if request.user == request_obj.assigned_to or request.user.role == 'admin':
            if request_obj.escalate('Needs advanced assistance'):
                messages.warning(request, 'Request escalated - needs advanced help.')
            else:
                messages.error(request, 'Cannot escalate this request.')
        else:
            messages.error(request, 'Only the assigned support can escalate this request.')
    return redirect('request_list')


@login_required
def request_delete(request, pk):
    """Delete a service request - Admin only."""
    request_obj = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == 'POST':
        # Only admin can delete
        if request.user.role == 'admin':
            request_number = request_obj.number
            request_obj.delete()
            messages.success(request, f'Request {request_number} deleted successfully.')
        else:
            messages.error(request, 'Only administrators can delete requests.')
    return redirect('request_list')
