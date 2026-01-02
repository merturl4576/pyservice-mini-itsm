"""
Script to populate sample Knowledge Base articles
Run: python populate_kb.py
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyservice.settings')

import django
django.setup()

from knowledge.models import Category, Article
from cmdb.models import User

# Get admin user as author
try:
    admin = User.objects.get(username='admin')
except:
    admin = User.objects.first()

print("Creating Knowledge Base categories...")

# Create categories
categories_data = [
    {'name': 'Getting Started', 'icon': 'bi-rocket-takeoff', 'order': 1, 'description': 'Quick start guides and basics'},
    {'name': 'Hardware Support', 'icon': 'bi-laptop', 'order': 2, 'description': 'Laptops, desktops, and peripherals'},
    {'name': 'Software & Applications', 'icon': 'bi-app-indicator', 'order': 3, 'description': 'Office, email, and business apps'},
    {'name': 'Network & Connectivity', 'icon': 'bi-wifi', 'order': 4, 'description': 'VPN, WiFi, and network issues'},
    {'name': 'Security & Passwords', 'icon': 'bi-shield-lock', 'order': 5, 'description': 'Account security and password help'},
]

for cat_data in categories_data:
    cat, created = Category.objects.get_or_create(name=cat_data['name'], defaults=cat_data)
    status = "Created" if created else "Exists"
    print(f"  [{status}] {cat.name}")

print("\nCreating Knowledge Base articles...")

# Create sample articles
articles_data = [
    {
        'title': 'How to Reset Your Password',
        'slug': 'password-reset',
        'category_name': 'Security & Passwords',
        'summary': 'Step-by-step guide to reset your company account password using the self-service portal.',
        'content': """## Password Reset Guide

### Option 1: Self-Service Reset
1. Go to the login page
2. Click "Forgot Password"
3. Enter your email address
4. Check your email for the reset link
5. Follow the link and set a new password

### Option 2: Contact IT Support
If you cannot access your email, please contact IT support to verify your identity and reset your password manually.

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one number
- At least one special character""",
        'is_published': True,
        'is_featured': True,
        'view_count': 156
    },
    {
        'title': 'VPN Setup Guide for Remote Work',
        'slug': 'vpn-setup-guide',
        'category_name': 'Network & Connectivity',
        'summary': 'Complete instructions for installing and configuring the company VPN on your device.',
        'content': """## VPN Setup Instructions

### Windows
1. Download the VPN client from the company portal
2. Install the application
3. Launch and enter your credentials
4. Select the nearest server location
5. Click Connect

### macOS
1. Open System Preferences > Network
2. Click + to add a new connection
3. Select VPN and configure with company settings
4. Enter your username and password

**Troubleshooting:**
- Ensure you have internet access before connecting
- Try a different server if connection is slow
- Contact IT if you receive certificate errors""",
        'is_published': True,
        'is_featured': True,
        'view_count': 89
    },
    {
        'title': 'Microsoft Office 365 Quick Start',
        'slug': 'office-365-quickstart',
        'category_name': 'Software & Applications',
        'summary': 'Learn how to access and use Microsoft Office 365 applications including Outlook, Teams, and Word.',
        'content': """## Office 365 Quick Start Guide

### Accessing Office 365
1. Go to office.com
2. Sign in with your company email
3. Access apps from the dashboard

### Key Applications:
- **Outlook**: Email and calendar
- **Teams**: Chat and video meetings
- **OneDrive**: File storage and sharing
- **Word/Excel/PowerPoint**: Document creation

### Tips:
- Install desktop apps for offline access
- Use Teams for internal communication
- Save files to OneDrive for automatic backup""",
        'is_published': True,
        'is_featured': False,
        'view_count': 67
    },
    {
        'title': 'Requesting New Hardware',
        'slug': 'hardware-request-process',
        'category_name': 'Hardware Support',
        'summary': 'How to request a new laptop, monitor, keyboard, or other IT equipment.',
        'content': """## Hardware Request Process

### Step 1: Submit a Service Request
1. Go to the Self-Service Portal
2. Click "Request New Laptop" or create a new request
3. Fill in the required details
4. Submit for approval

### Step 2: Manager Approval
Your manager will review and approve the request based on business need.

### Step 3: IT Processing
Once approved, IT will:
- Order the equipment
- Configure it with required software
- Schedule delivery or pickup

### Timeline
- Standard requests: 5-7 business days
- Urgent requests: 2-3 business days (requires justification)""",
        'is_published': True,
        'is_featured': False,
        'view_count': 45
    },
    {
        'title': 'New Employee IT Onboarding',
        'slug': 'new-employee-onboarding',
        'category_name': 'Getting Started',
        'summary': 'Everything new employees need to know about IT systems, accounts, and tools.',
        'content': """## Welcome to the Team!

### Your IT Accounts
You will receive:
- Email account (firstname.lastname@company.com)
- Network login credentials
- Access to relevant systems based on your role

### First Day Checklist
- [ ] Receive your laptop and accessories
- [ ] Log in to your email
- [ ] Set up multi-factor authentication
- [ ] Install required software
- [ ] Join your team channels in Teams
- [ ] Complete security awareness training

### Getting Help
- Use the Self-Service Portal for common issues
- Submit an incident for urgent problems
- Email helpdesk@company.com for questions""",
        'is_published': True,
        'is_featured': True,
        'view_count': 123
    },
    {
        'title': 'WiFi Troubleshooting Guide',
        'slug': 'wifi-troubleshooting',
        'category_name': 'Network & Connectivity',
        'summary': 'Common WiFi problems and how to fix them quickly.',
        'content': """## WiFi Troubleshooting

### Quick Fixes
1. **Restart your device** - Solves 80% of issues
2. **Forget and reconnect** to the network
3. **Move closer** to the access point
4. **Check if others are affected** - may be a building-wide issue

### Office WiFi Networks
- **Corporate**: For company devices (auto-connect)
- **Guest**: For visitors and personal devices

### Still Not Working?
Submit an incident with:
- Your location in the building
- Device type
- Error message (if any)""",
        'is_published': True,
        'is_featured': False,
        'view_count': 78
    },
]

for art_data in articles_data:
    category_name = art_data.pop('category_name')
    try:
        category = Category.objects.get(name=category_name)
    except Category.DoesNotExist:
        print(f"  [Error] Category not found: {category_name}")
        continue
    
    art, created = Article.objects.get_or_create(
        slug=art_data['slug'],
        defaults={**art_data, 'category': category, 'author': admin}
    )
    status = "Created" if created else "Exists"
    print(f"  [{status}] {art.title}")

print("\n✅ Knowledge Base populated successfully!")
print(f"   Categories: {Category.objects.count()}")
print(f"   Articles: {Article.objects.filter(is_published=True).count()}")
