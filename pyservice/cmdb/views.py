"""
CMDB Views
PyService Mini-ITSM Platform
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department, User, Asset, AssetInventory
from .forms import DepartmentForm, AssetForm


@login_required
def asset_list(request):
    """List all assets with inventory table."""
    assets = Asset.objects.all()
    inventory = AssetInventory.objects.all()
    return render(request, 'cmdb/asset_list.html', {
        'assets': assets,
        'inventory': inventory
    })


@login_required
def inventory_edit(request):
    """Edit company inventory - Admin only."""
    if request.user.role != 'admin':
        messages.error(request, 'Only administrators can edit inventory.')
        return redirect('asset_list')
    
    inventory = AssetInventory.objects.all()
    
    if request.method == 'POST':
        for item in inventory:
            field_name = f'qty_{item.item_type}'
            if field_name in request.POST:
                try:
                    new_qty = int(request.POST[field_name])
                    if new_qty >= 0:
                        item.quantity = new_qty
                        item.save()
                except ValueError:
                    pass
        messages.success(request, 'Inventory updated successfully.')
        return redirect('asset_list')
    
    return render(request, 'cmdb/inventory_edit.html', {'inventory': inventory})


@login_required
def asset_detail(request, pk):
    """View asset details."""
    asset = get_object_or_404(Asset, pk=pk)
    return render(request, 'cmdb/asset_detail.html', {'asset': asset})


@login_required
def asset_create(request):
    """Create new asset with inventory check."""
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            asset_type = asset.asset_type
            
            # Non-admin: auto-assign to self
            if request.user.role != 'admin':
                asset.assigned_to = request.user
                asset.created_by = request.user
            else:
                asset.created_by = request.user
            
            # "Other" type always needs admin review
            if asset_type == 'other':
                asset.status = 'under_review'
                asset.save()
                messages.warning(request, 'Asset created but needs admin approval (custom item type).')
            # Check inventory availability
            elif AssetInventory.check_availability(asset_type):
                # Item in stock - decrement and assign
                AssetInventory.decrement(asset_type)
                asset.status = 'assigned'
                asset.save()
                messages.success(request, f'Asset created and assigned! {asset.get_asset_type_display()} stock decremented.')
            else:
                # Not in stock - needs admin review
                asset.status = 'under_review'
                asset.save()
                messages.warning(request, f'Asset created but needs admin approval (no {asset.get_asset_type_display()} in stock).')
            
            return redirect('asset_list')
    else:
        form = AssetForm()
    
    users = User.objects.all()
    is_admin = request.user.role == 'admin'
    return render(request, 'cmdb/asset_form.html', {
        'form': form,
        'users': users,
        'is_admin': is_admin
    })


@login_required
def asset_update(request, pk):
    """Update existing asset."""
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asset updated successfully.')
            return redirect('asset_detail', pk=pk)
    else:
        form = AssetForm(instance=asset)
    
    users = User.objects.all()
    is_admin = request.user.role == 'admin'
    return render(request, 'cmdb/asset_form.html', {
        'form': form,
        'users': users,
        'is_admin': is_admin
    })


@login_required
def asset_approve(request, pk):
    """Admin approves asset request."""
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        if request.user.role == 'admin':
            if asset.approve():
                messages.success(request, f'Asset {asset.name} approved and assigned.')
            else:
                messages.error(request, 'Cannot approve this asset.')
        else:
            messages.error(request, 'Only administrators can approve assets.')
    return redirect('asset_list')


@login_required
def asset_decline(request, pk):
    """Admin declines asset request."""
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        if request.user.role == 'admin':
            if asset.decline():
                messages.warning(request, f'Asset {asset.name} declined.')
            else:
                messages.error(request, 'Cannot decline this asset.')
        else:
            messages.error(request, 'Only administrators can decline assets.')
    return redirect('asset_list')


@login_required
def asset_delete(request, pk):
    """Delete an asset - Admin only."""
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        if request.user.role == 'admin':
            asset_name = asset.name
            asset.delete()
            messages.success(request, f'Asset {asset_name} deleted successfully.')
        else:
            messages.error(request, 'Only administrators can delete assets.')
    return redirect('asset_list')


@login_required
def department_list(request):
    """List departments - admins see all, others see only their own."""
    is_admin = request.user.role == 'admin'
    
    if is_admin:
        # Admin sees all departments with members
        departments = Department.objects.all().prefetch_related('users')
    else:
        # Non-admin users see only their own department
        if request.user.department:
            departments = Department.objects.filter(pk=request.user.department.pk).prefetch_related('users')
        else:
            departments = Department.objects.none()
    
    return render(request, 'cmdb/department_list.html', {
        'departments': departments,
        'is_admin': is_admin
    })


@login_required
def department_create(request):
    """Create new department - Admin only."""
    if request.user.role != 'admin':
        messages.error(request, 'Only administrators can create departments.')
        return redirect('asset_list')
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created successfully.')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    
    return render(request, 'cmdb/department_form.html', {'form': form})


@login_required
def department_update(request, pk):
    """Update existing department - Admin only."""
    if request.user.role != 'admin':
        messages.error(request, 'Only administrators can edit departments.')
        return redirect('asset_list')
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully.')
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    
    return render(request, 'cmdb/department_form.html', {'form': form})


@login_required
def department_delete(request, pk):
    """Delete a department - Admin only."""
    if request.user.role != 'admin':
        messages.error(request, 'Only administrators can delete departments.')
        return redirect('department_list')
    
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        try:
            department_name = department.name
            department.delete()
            messages.success(request, f'Department "{department_name}" deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting department: {str(e)}')
    
    return redirect('department_list')

