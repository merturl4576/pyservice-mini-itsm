# PyService - Mini-ITSM Platform

A simple IT Service Management (ITSM) platform built with Django, inspired by ServiceNow. This project helps organizations manage their IT assets, incidents, and service requests all in one place.

## 📋 What is This Project?

PyService is a web application that helps IT departments manage:
- **Computer Assets** (laptops, monitors, phones, etc.)
- **Incident Reports** (when something breaks or doesn't work)
- **Service Requests** (when employees need new software or equipment)

Think of it as a complete system for managing IT operations in a company.

## ✨ Key Features

### 1. CMDB (Asset Management)
- Keep track of all company computers and equipment
- See who is using which laptop or monitor
- Check if equipment is available, in use, or needs repair
- Automatically assign equipment to new employees

### 2. Incident Management
- Employees can report IT problems
- Support team can track and fix issues
- **Smart Priority System**: Combines impact and urgency to prioritize work
- **SLA Tracking**: Automatically calculates deadlines based on priority
  - Critical issues: 4 hours to respond
  - High priority: 24 hours
  - Medium priority: 48 hours
  - Low priority: 72 hours

### 3. Service Requests
- Request new software or equipment
- Automatic approval workflow
- Manager approval required
- Automatic assignment to IT team

### 4. REST API
- All data accessible via JSON API
- Easy integration with other systems
- Standard CRUD operations

## 🛠️ Technology Stack

- **Backend**: Python 3.x + Django 4.2
- **Database**: MySQL/MariaDB (XAMPP)
- **API**: Django REST Framework
- **Frontend**: Bootstrap 5 (clean, responsive design)
- **Authentication**: Django built-in user system

## 📦 Installation

### Prerequisites

Before you start, make sure you have:
- Python 3.8 or higher installed
- XAMPP (for MySQL database)
- Git (optional, for version control)

### Step 1: Download the Project

```bash
git clone https://github.com/merturl67/pyservice-mini-itsm.git
cd pyservice-mini-itsm
```

Or download the ZIP file and extract it.

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv env

# Activate it
# On Windows:
env\Scripts\activate
# On Mac/Linux:
source env/bin/activate
```

### Step 3: Install Dependencies

```bash
cd pyservice
pip install -r requirements.txt
```

### Step 4: Setup Database

1. Start XAMPP and make sure MySQL is running
2. Open phpMyAdmin (http://localhost/phpmyadmin)
3. Create a new database called `pyservice_db`

### Step 5: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Admin User

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### Step 7: Run the Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 in your browser!

## 📂 Project Structure

```
pyservice/
├── cmdb/                   # Asset management module
│   ├── models.py          # Department, User, Asset models
│   ├── views.py           # Asset management views
│   └── forms.py           # Asset forms
├── incidents/             # Incident management module
│   ├── models.py          # Incident model with SLA logic
│   ├── views.py           # Incident tracking views
│   └── forms.py           # Incident forms
├── service_requests/      # Service request module
│   ├── models.py          # Service request workflow
│   ├── views.py           # Request management views
│   └── forms.py           # Request forms
├── api/                   # REST API
│   ├── serializers.py     # JSON serializers
│   └── views.py           # API endpoints
├── templates/             # HTML templates
├── static/                # CSS, JavaScript, images
├── pyservice/             # Main project settings
│   ├── settings.py        # Configuration
│   ├── urls.py            # URL routing
│   └── dashboard.py       # Dashboard view
├── manage.py              # Django management script
└── requirements.txt       # Python dependencies
```

## 🎯 How to Use

### For Regular Users (Employees)

1. **Login** with your credentials
2. **Report an Incident** if something isn't working
3. **Request Equipment** or software through Service Requests
4. **View Your Assets** to see what equipment you have

### For IT Support Staff

1. **View Dashboard** to see pending incidents and requests
2. **Claim Incidents** to work on them
3. **Approve Service Requests** for employees
4. **Manage Assets** - assign, repair, or retire equipment

### For Administrators

1. **Access Admin Panel** at http://127.0.0.1:8000/admin
2. **Manage Users and Departments**
3. **View All Assets and Inventory**
4. **Configure System Settings**

## 🔑 Default User Roles

The system has 5 user roles:
- **Staff**: Regular employees who report issues and request services
- **IT Support**: Handles incidents and service requests
- **Technician**: Technical staff for repairs and maintenance
- **Manager**: Approves service requests and budgets
- **Administrator**: Full system access

## 🌐 API Endpoints

Access the API at http://127.0.0.1:8000/api/

- `GET /api/incidents/` - List all incidents
- `POST /api/incidents/` - Create new incident
- `GET /api/assets/` - List all assets
- `POST /api/assets/` - Create new asset

API requires authentication. Use your login credentials.

## 🤝 Contributing

This project was created as a portfolio demonstration of:
- Django web development
- Database design and ORM
- ITIL service management principles
- RESTful API design
- Bootstrap frontend integration

## 📝 License

This project is open source and available for educational purposes.

## 👨‍💻 Author

**Mert Ural**
- Email: merturl67@gmail.com
- GitHub: [@merturl4576](https://github.com/merturl4576)

## 🙏 Acknowledgments

This project was built following ITIL (Information Technology Infrastructure Library) best practices for IT service management. It demonstrates how to build a professional ITSM platform similar to enterprise solutions like ServiceNow.

---

**Note**: This is a demonstration project for educational purposes. For production use, please ensure proper security measures, including changing the SECRET_KEY in settings.py and using environment variables for sensitive data.
