"""
Management command to populate test data for dashboard demo
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from cmdb.models import Department, Asset
from incidents.models import Incident
from service_requests.models import ServiceRequest

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate test data for dashboard demonstration'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')
        
        # Get or create departments
        it_dept, _ = Department.objects.get_or_create(
            name='IT Department',
            defaults={'description': 'IT support and infrastructure team'}
        )
        hr_dept, _ = Department.objects.get_or_create(
            name='HR Department',
            defaults={'description': 'Human Resources team'}
        )
        sales_dept, _ = Department.objects.get_or_create(
            name='Sales Department',
            defaults={'description': 'Sales and marketing team'}
        )
        
        # Create test users
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@pyservice.com',
                'role': 'admin',
                'department': it_dept,
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: admin/admin123'))
        
        # IT Support user
        henry, created = User.objects.get_or_create(
            username='dev_henry',
            defaults={
                'first_name': 'Henry',
                'last_name': 'Developer',
                'email': 'henry@pyservice.com',
                'role': 'it_support',
                'department': it_dept
            }
        )
        if created:
            henry.set_password('henry123')
            henry.save()
            self.stdout.write(self.style.SUCCESS(f'Created IT Support: dev_henry/henry123'))
        
        # Technician users
        tech1, created = User.objects.get_or_create(
            username='tech_mike',
            defaults={
                'first_name': 'Mike',
                'last_name': 'Technician',
                'email': 'mike@pyservice.com',
                'role': 'technician',
                'department': it_dept
            }
        )
        if created:
            tech1.set_password('mike123')
            tech1.save()
            self.stdout.write(self.style.SUCCESS(f'Created Technician: tech_mike/mike123'))
        
        tech2, created = User.objects.get_or_create(
            username='tech_sarah',
            defaults={
                'first_name': 'Sarah',
                'last_name': 'Tech',
                'email': 'sarah@pyservice.com',
                'role': 'technician',
                'department': it_dept
            }
        )
        if created:
            tech2.set_password('sarah123')
            tech2.save()
            self.stdout.write(self.style.SUCCESS(f'Created Technician: tech_sarah/sarah123'))
        
        # Staff users
        staff1, created = User.objects.get_or_create(
            username='staff_john',
            defaults={
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john@pyservice.com',
                'role': 'staff',
                'department': sales_dept
            }
        )
        if created:
            staff1.set_password('john123')
            staff1.save()
            self.stdout.write(self.style.SUCCESS(f'Created Staff: staff_john/john123'))
        
        staff2, created = User.objects.get_or_create(
            username='staff_emma',
            defaults={
                'first_name': 'Emma',
                'last_name': 'Wilson',
                'email': 'emma@pyservice.com',
                'role': 'staff',
                'department': hr_dept
            }
        )
        if created:
            staff2.set_password('emma123')
            staff2.save()
            self.stdout.write(self.style.SUCCESS(f'Created Staff: staff_emma/emma123'))
        
        # Create Incidents
        # Active incident assigned to Henry
        inc1, _ = Incident.objects.get_or_create(
            number='INC0001',
            defaults={
                'title': 'Server Performance Issue',
                'description': 'Production server running slow',
                'priority': 2,
                'state': 'in_progress',
                'caller': staff1,
                'assigned_to': henry,
                'sla_breached': False
            }
        )
        
        # Resolved incident by Henry
        inc2, _ = Incident.objects.get_or_create(
            number='INC0002',
            defaults={
                'title': 'Email System Down',
                'description': 'Email not working for sales team',
                'priority': 1,
                'state': 'resolved',
                'caller': staff1,
                'assigned_to': henry,
                'sla_breached': False
            }
        )
        
        # New unassigned incident for technicians
        inc3, _ = Incident.objects.get_or_create(
            number='INC0003',
            defaults={
                'title': 'Printer Not Working',
                'description': 'Office printer jammed',
                'priority': 3,
                'state': 'new',
                'caller': staff2,
                'assigned_to': None,
                'sla_breached': False
            }
        )
        
        # Active incident for tech_mike
        inc4, _ = Incident.objects.get_or_create(
            number='INC0004',
            defaults={
                'title': 'Wi-Fi Connection Issues',
                'description': 'Intermittent WiFi in meeting rooms',
                'priority': 3,
                'state': 'in_progress',
                'caller': staff1,
                'assigned_to': tech1,
                'sla_breached': False
            }
        )
        
        # Resolved incident by tech_mike
        inc5, _ = Incident.objects.get_or_create(
            number='INC0005',
            defaults={
                'title': 'Computer Not Booting',
                'description': 'Desktop computer hardware issue',
                'priority': 2,
                'state': 'resolved',
                'caller': staff2,
                'assigned_to': tech1,
                'sla_breached': False
            }
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created {Incident.objects.count()} incidents'))
        
        # Create Service Requests
        # Active request from staff1
        req1, _ = ServiceRequest.objects.get_or_create(
            number='REQ0001',
            defaults={
                'title': 'New Laptop Request',
                'description': 'Need new laptop for development work',
                'state': 'approved',
                'requester': staff1,
                'assigned_to': None
            }
        )
        
        # Closed request
        req2, _ = ServiceRequest.objects.get_or_create(
            number='REQ0002',
            defaults={
                'title': 'Software License',
                'description': 'Request for Adobe license',
                'state': 'fulfilled',
                'requester': staff1,
                'assigned_to': tech1
            }
        )
        
        # Active request from staff2
        req3, _ = ServiceRequest.objects.get_or_create(
            number='REQ0003',
            defaults={
                'title': 'Access to File Server',
                'description': 'Need access to shared files',
                'state': 'in_progress',
                'requester': staff2,
                'assigned_to': tech2
            }
        )
        
        # Awaiting approval
        req4, _ = ServiceRequest.objects.get_or_create(
            number='REQ0004',
            defaults={
                'title': 'VPN Access',
                'description': 'Request VPN for remote work',
                'state': 'awaiting_approval',
                'requester': staff2,
                'assigned_to': None
            }
        )
        
        # Unassigned request for technicians
        req5, _ = ServiceRequest.objects.get_or_create(
            number='REQ0005',
            defaults={
                'title': 'Install Accounting Software',
                'description': 'Install QuickBooks on new PC',
                'state': 'approved',
                'requester': staff1,
                'assigned_to': None
            }
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created {ServiceRequest.objects.count()} service requests'))
        
        # Create Assets
        # Assigned to staff1
        asset1, _ = Asset.objects.get_or_create(
            name='Dell Latitude 7420',
            defaults={
                'asset_type': 'laptop',
                'serial_number': 'DL74201234',
                'status': 'assigned',
                'assigned_to': staff1,
                'created_by': admin_user
            }
        )
        
        # Under review
        asset2, _ = Asset.objects.get_or_create(
            name='HP Monitor 27inch',
            defaults={
                'asset_type': 'monitor',
                'serial_number': 'HPM27001',
                'status': 'under_review',
                'assigned_to': None,
                'created_by': henry
            }
        )
        
        # In repair
        asset3, _ = Asset.objects.get_or_create(
            name='Lenovo ThinkPad',
            defaults={
                'asset_type': 'laptop',
                'serial_number': 'LTP5678',
                'status': 'in_repair',
                'assigned_to': staff2,
                'created_by': admin_user
            }
        )
        
        # Assigned to staff2
        asset4, _ = Asset.objects.get_or_create(
            name='iPhone 13',
            defaults={
                'asset_type': 'phone',
                'serial_number': 'IPH13001',
                'status': 'assigned',
                'assigned_to': staff2,
                'created_by': admin_user
            }
        )
        
        # In stock
        asset5, _ = Asset.objects.get_or_create(
            name='Canon Printer',
            defaults={
                'asset_type': 'printer',
                'serial_number': 'CAN9876',
                'status': 'in_stock',
                'assigned_to': None,
                'created_by': admin_user
            }
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created {Asset.objects.count()} assets'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Test Data Created Successfully! ==='))
        self.stdout.write('\nTest Users:')
        self.stdout.write('  admin/admin123 (Admin)')
        self.stdout.write('  dev_henry/henry123 (IT Support)')
        self.stdout.write('  tech_mike/mike123 (Technician)')
        self.stdout.write('  tech_sarah/sarah123 (Technician)')
        self.stdout.write('  staff_john/john123 (Staff)')
        self.stdout.write('  staff_emma/emma123 (Staff)')


