"""
CMDB Admin Configuration
PyService Mini-ITSM Platform
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Department, User, Asset


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'get_full_name', 'department', 'role', 'is_active']
    list_editable = ['department', 'role']  # Allow inline editing of department and role
    list_filter = ['role', 'department', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['username']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('ITSM Information', {
            'fields': ('department', 'role', 'phone', 'employee_id')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('ITSM Information', {
            'fields': ('department', 'role', 'phone', 'employee_id')
        }),
    )
    
    actions = ['assign_to_department', 'remove_from_department']
    
    def assign_to_department(self, request, queryset):
        """Custom action to assign users to a department"""
        from django.contrib import messages
        from django import forms
        from django.shortcuts import render
        
        class DepartmentForm(forms.Form):
            department = forms.ModelChoiceField(
                queryset=Department.objects.all(),
                required=True,
                label='Select Department'
            )
        
        if 'apply' in request.POST:
            form = DepartmentForm(request.POST)
            if form.is_valid():
                department = form.cleaned_data['department']
                count = queryset.update(department=department)
                self.message_user(
                    request,
                    f'{count} user(s) assigned to {department.name}',
                    messages.SUCCESS
                )
                return
        else:
            form = DepartmentForm()
        
        return render(
            request,
            'admin/assign_department.html',
            {
                'form': form,
                'users': queryset,
                'action': 'assign_to_department',
                'title': 'Assign Users to Department'
            }
        )
    
    assign_to_department.short_description = "Assign selected users to a department"
    
    def remove_from_department(self, request, queryset):
        """Remove users from their department"""
        count = queryset.update(department=None)
        self.message_user(
            request,
            f'{count} user(s) removed from their departments',
            self.message_user.WARNING
        )
    
    remove_from_department.short_description = "Remove selected users from department"


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'asset_type', 'serial_number', 'status', 'assigned_to', 'location']
    list_filter = ['asset_type', 'status', 'manufacturer']
    search_fields = ['name', 'serial_number', 'model_name']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Asset Information', {
            'fields': ('name', 'asset_type', 'serial_number', 'model_name', 'manufacturer')
        }),
        ('Assignment', {
            'fields': ('status', 'assigned_to', 'location')
        }),
        ('Financial', {
            'fields': ('purchase_date', 'purchase_cost', 'warranty_end_date'),
            'classes': ['collapse']
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ['collapse']
        }),
    )
    
    actions = ['mark_in_stock', 'mark_retired']
    
    def mark_in_stock(self, request, queryset):
        queryset.update(status='in_stock', assigned_to=None)
    mark_in_stock.short_description = "Mark selected assets as In Stock"
    
    def mark_retired(self, request, queryset):
        queryset.update(status='retired', assigned_to=None)
    mark_retired.short_description = "Mark selected assets as Retired"
