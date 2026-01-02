# 🚀 PyService - Mini-ITSM Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://djangoproject.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com)

A modern IT Service Management (ITSM) platform built with Django, inspired by ServiceNow. Manage IT assets, incidents, and service requests all in one place.

## 📋 What is PyService?

PyService is a web application that helps IT departments manage:

- **🖥️ Assets** - Track laptops, monitors, phones and equipment
- **🔧 Incidents** - Report and fix IT problems with SLA tracking
- **📝 Service Requests** - Request new software or equipment
- **📚 Knowledge Base** - Self-service FAQ articles
- **📅 Calendar** - View SLA deadlines and due dates
- **📊 Dashboard** - Real-time charts and statistics

## ✨ Key Features

### Dashboard with Analytics
- Real-time incident and request statistics
- Interactive Chart.js visualizations (pie, line, doughnut charts)
- SLA compliance tracking
- Staff performance leaderboard

### Incident Management
- Smart Priority System (Impact × Urgency = Priority)
- Automatic SLA calculation:
  - Critical: 4 hours
  - High: 24 hours
  - Medium: 48 hours
  - Low: 72 hours
- Claim, escalate, and resolve workflow

### Service Request Workflow
- Multi-step approval process
- Manager approval required
- Automatic asset assignment
- Status tracking (Draft → Approval → Assigned → Completed)

### Knowledge Base
- Searchable FAQ articles
- Categories with icons
- Featured and popular articles
- View count tracking

### ITSM Calendar
- Visual SLA deadline tracking
- Color-coded priority display
- Incident and request timeline

### REST API
- Full CRUD operations
- JSON responses
- Token authentication
- Easy integration with other systems

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.8+ / Django 4.2 |
| Database | MySQL / MariaDB |
| API | Django REST Framework |
| Frontend | Bootstrap 5, Chart.js, FullCalendar |
| Icons | Bootstrap Icons |

## 📦 Quick Start

### Prerequisites

- Python 3.8 or higher
- XAMPP (MySQL database)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/merturl4576/pyservice-mini-itsm.git
cd pyservice-mini-itsm

# Create virtual environment
python -m venv env
env\Scripts\activate  # Windows
source env/bin/activate  # Mac/Linux

# Install dependencies
cd pyservice
pip install -r requirements.txt

# Setup database (start XAMPP MySQL first)
# Create database 'pyservice_db' in phpMyAdmin

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start server
python manage.py runserver
```

Visit **http://127.0.0.1:8000** in your browser!

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| Staff | Report incidents, request services |
| IT Support | Handle incidents, approve requests |
| Technician | Technical repairs, maintenance |
| Manager | Approve requests, view reports |
| Administrator | Full system access |

## 📂 Project Structure

```
pyservice/
├── cmdb/                   # Asset management
├── incidents/              # Incident tracking
├── service_requests/       # Service request workflow
├── knowledge/              # Knowledge base articles
├── notifications/          # User notifications
├── api/                    # REST API endpoints
├── templates/              # HTML templates
│   ├── dashboard.html      # Main dashboard
│   ├── calendar.html       # ITSM calendar
│   └── knowledge/          # KB templates
├── pyservice/
│   ├── settings.py         # Configuration
│   ├── dashboard.py        # Dashboard view
│   ├── calendar_view.py    # Calendar view
│   └── selfservice.py      # Self-service portal
└── requirements.txt
```

## 🌐 API Endpoints

```
GET  /api/incidents/     - List incidents
POST /api/incidents/     - Create incident
GET  /api/assets/        - List assets
POST /api/assets/        - Create asset
GET  /api/requests/      - List service requests
POST /api/requests/      - Create request
```

## 🎯 Demo Credentials

Use these after running `python manage.py createsuperuser`:

- **Admin Panel**: http://127.0.0.1:8000/admin
- **Dashboard**: http://127.0.0.1:8000/dashboard
- **Knowledge Base**: http://127.0.0.1:8000/knowledge

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=pyservice_db
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Mert Ural**
- GitHub: [@merturl4576](https://github.com/merturl4576)

## 🙏 Acknowledgments

- Built following ITIL best practices
- Inspired by ServiceNow platform
- Uses Django, Bootstrap, and Chart.js

---

⭐ **Star this repo if you find it useful!**
