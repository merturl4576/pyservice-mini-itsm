# 🚀 PyService - Enterprise ITSM Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://djangoproject.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-brightgreen.svg)](https://github.com/features/actions)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)](https://mysql.com)

A production-ready IT Service Management (ITSM) platform built with Django, inspired by ServiceNow. Features remote support sessions, real-time chat, staff performance leaderboards, SLA tracking, and enterprise-grade security.

---

## 🆕 What's New in v2.0

- **🖥️ Remote Support Sessions** - Real-time remote assistance with AnyDesk integration, chat, and voice-to-text transcription 
- **👥 Staff Performance Leaderboard** - Track and gamify IT support performance with monthly rankings
- **📊 Enhanced Reports Dashboard** - Detailed analytics with remote session statistics
- **🔔 Real-time Notifications** - WebSocket-based instant notifications
- **📅 Interactive Calendar** - Visual calendar view for incidents and requests

---

## ✨ Key Features

### 🎯 Core ITSM Functionality
| Feature | Description |
|---------|-------------|
| **Incident Management** | ITIL-compliant workflow with priority matrix (Impact × Urgency) |
| **SLA Tracking** | Automatic SLA calculation with breach detection and warnings |
| **Service Requests** | Multi-step approval workflow with manager approvals |
| **Asset Management** | Complete CMDB for IT assets with assignment tracking |
| **Knowledge Base** | Searchable FAQ articles with categories |
| **Dashboard** | Real-time analytics with Chart.js visualizations |
| **Remote Support** | Live remote assistance sessions with chat and voice transcription |
| **Staff Leaderboard** | Performance tracking with gamification elements |

### 🖥️ Remote Support Features
| Feature | Description |
|---------|-------------|
| **Session Queue** | IT staff can see pending support requests |
| **Real-time Chat** | Built-in messaging during support sessions |
| **Voice-to-Text** | Transcribe voice communications automatically |
| **AnyDesk Integration** | Quick connection using AnyDesk IDs |
| **Session History** | Complete log of support sessions |
| **Priority Levels** | Low, Medium, High, Urgent prioritization |

### 🔧 Technical Features
| Feature | Technology |
|---------|------------|
| **Containerization** | Docker + Docker Compose |
| **CI/CD** | GitHub Actions |
| **Async Tasks** | Celery + Redis |
| **Real-time** | WebSocket (Django Channels) |
| **REST API** | Django REST Framework + JWT |
| **GraphQL** | Graphene-Django |
| **Search** | Elasticsearch (optional) |
| **PDF Export** | ReportLab |
| **Monitoring** | Prometheus + Grafana |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         NGINX (Reverse Proxy)                   │
├─────────────────────────────────────────────────────────────────┤
│                                │                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │  Django App      │  │  Celery Worker   │  │ Celery Beat   │ │
│  │  (Gunicorn)      │  │  (Async Tasks)   │  │ (Scheduler)   │ │
│  └────────┬─────────┘  └────────┬─────────┘  └───────┬───────┘ │
│           │                     │                     │         │
│  ┌────────┴─────────────────────┴─────────────────────┴───────┐ │
│  │                        Redis                               │ │
│  │  (Cache, Session, Celery Broker, WebSocket)                │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                │                                │
│  ┌─────────────────────────────┴───────────────────────────────┐ │
│  │                        MySQL                                │ │
│  │                     (Database)                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

Before you begin, make sure you have:
- **Python 3.11+** installed
- **MySQL** running (XAMPP, standalone MySQL, or Docker)
- **Git** installed

### Option 1: Local Development (Recommended for beginners)

```bash
# 1. Clone repository
git clone https://github.com/merturl4576/pyservice-mini-itsm.git
cd pyservice-mini-itsm

# 2. Create virtual environment
python -m venv env

# Windows:
env\Scripts\activate

# Linux/Mac:
source env/bin/activate

# 3. Install dependencies
cd pyservice
pip install -r requirements.txt

# 4. Set up MySQL database
# Option A: Using XAMPP
#   - Start XAMPP and enable MySQL
#   - Create database 'pyservice_db' in phpMyAdmin

# Option B: Using MySQL command line
#   mysql -u root -p
#   CREATE DATABASE pyservice_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 5. Configure environment
# Copy .env.example to .env and update database settings

# 6. Run database migrations
python manage.py migrate

# 7. Create admin user
python manage.py createsuperuser

# 8. Start development server
python manage.py runserver

# 9. Open in browser
# http://127.0.0.1:8000
```

### 🔐 Demo Admin Account

After installation, you can use the following demo admin account to log in:

| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Password** | `admin123` |

> **Note:** For production use, please change these credentials immediately!

### Option 2: Using Docker (Production-ready)

```bash
# Clone repository
git clone https://github.com/merturl4576/pyservice-mini-itsm.git
cd pyservice-mini-itsm

# Configure environment
cp .env.docker .env.docker.local
# Edit .env.docker.local with your settings

# Start all services
docker-compose up -d

# Create superuser
docker-compose exec django python manage.py createsuperuser

# Access the application
# http://localhost:80
```

### Option 3: Windows Quick Start (START.bat)

```batch
# Double-click START.bat file
# This will automatically:
# 1. Activate virtual environment
# 2. Start Django development server
```

---

## 📂 Project Structure

```
pyservice-mini-itsm/
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI Pipeline
│       └── cd.yml              # CD Pipeline
├── docker/
│   ├── entrypoint.sh           # Container startup
│   ├── nginx/                  # Nginx config
│   ├── mysql/                  # MySQL init
│   └── prometheus/             # Prometheus config
├── pyservice/
│   ├── api/                    # REST API
│   │   ├── auth.py             # JWT + 2FA
│   │   ├── health.py           # Health checks
│   │   └── views.py            # ViewSets
│   ├── cmdb/                   # Asset management
│   ├── incidents/              # Incident tracking
│   │   └── tasks.py            # SLA monitoring
│   ├── service_requests/       # Request workflow
│   ├── remote_support/         # Remote support sessions
│   │   ├── models.py           # Session, Message, VoiceTranscript
│   │   ├── views.py            # Queue, session room, chat
│   │   └── urls.py             # URL routing
│   ├── notifications/
│   │   ├── consumers.py        # WebSocket
│   │   └── tasks.py            # Email tasks
│   ├── graphql_api/            # GraphQL
│   ├── search/                 # Elasticsearch
│   ├── reports/
│   │   ├── pdf_generator.py    # PDF export
│   │   └── tasks.py            # Report tasks
│   ├── core/
│   │   └── middleware.py       # Audit logging
│   ├── templates/              # HTML templates
│   │   ├── base.html           # Base template
│   │   ├── dashboard.html      # Main dashboard
│   │   ├── staff_leaderboard.html
│   │   ├── remote_support/     # Remote support templates
│   │   └── ...
│   └── pyservice/
│       ├── celery.py           # Celery config
│       ├── asgi.py             # WebSocket support
│       └── settings.py         # Configuration
├── Dockerfile                  # Multi-stage build
├── docker-compose.yml          # Service orchestration
├── setup.cfg                   # Linting config
├── LICENSE                     # MIT License
└── README.md
```

---

## 📡 API Endpoints

### REST API

```
Base URL: http://localhost:8000/api/

# Authentication
POST /api/auth/token/          # Get JWT token
POST /api/auth/token/refresh/  # Refresh token
POST /api/auth/logout/         # Logout (blacklist token)

# Incidents
GET  /api/incidents/           # List incidents
POST /api/incidents/           # Create incident
GET  /api/incidents/{id}/      # Get incident
POST /api/incidents/{id}/resolve/  # Resolve incident

# Assets
GET  /api/assets/              # List assets
POST /api/assets/              # Create asset
GET  /api/assets/available/    # Available assets
POST /api/assets/{id}/assign/  # Assign to user

# Service Requests
GET  /api/requests/            # List requests
POST /api/requests/            # Create request
POST /api/requests/{id}/submit/   # Submit for approval
POST /api/requests/{id}/approve/  # Approve request

# Search
GET  /api/search/?q=query      # Global search

# Health
GET  /api/health/              # Health check
GET  /api/health/detailed/     # Detailed status
```

### GraphQL

```
Endpoint: http://localhost:8000/graphql/

# Example Query
query {
  allIncidents(first: 10) {
    edges {
      node {
        number
        title
        priority
        slaStatus
      }
    }
  }
  dashboardStats {
    openIncidents
    slaCompliance
  }
}
```

### API Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

---

## ⚡ Celery Tasks

### Scheduled Tasks (Celery Beat)

| Task | Schedule | Description |
|------|----------|-------------|
| `check_sla_breaches` | Every 5 min | Mark incidents as SLA breached |
| `send_sla_warnings` | Every 15 min | Email warnings for at-risk incidents |
| `generate_daily_summary` | 6:00 AM | Daily statistics report |
| `generate_weekly_report` | Monday 7:00 AM | Weekly performance report |
| `cleanup_notifications` | Midnight | Remove old notifications |

### Running Celery (Optional - for async features)

```bash
# Start Redis first (required for Celery)
# Windows: Use Redis for Windows or Docker
# Mac/Linux: redis-server

# Start Celery worker
celery -A pyservice worker -l info

# Start Celery Beat scheduler
celery -A pyservice beat -l info
```

---

## 👥 User Roles & Permissions

| Role | Permissions |
|------|-------------|
| **Staff** | Create incidents, submit service requests, request remote support |
| **IT Support** | Claim/resolve incidents, provide remote support, manage queue |
| **Technician** | Technical repairs, asset management, complete support sessions |
| **Manager** | Approve requests, view reports, access leaderboard |
| **Administrator** | Full system access, user management, all features |

---

## 🔐 Security Features

- **JWT Authentication** - Token-based API authentication
- **Two-Factor Authentication** - TOTP-based 2FA
- **Rate Limiting** - API request throttling
- **Audit Logging** - Complete request logging
- **CORS** - Configurable cross-origin requests
- **Security Headers** - XSS, CSRF, Clickjacking protection

---

## 🔧 Configuration

### Environment Variables

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=pyservice_db
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306

# Redis (optional - for Celery)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password
```

---

## 📊 Monitoring

### Prometheus Metrics

```
Endpoint: http://localhost:8000/metrics

# Available metrics
- django_http_requests_total
- django_http_request_duration_seconds
- celery_task_runtime_seconds
```

### Grafana Dashboard

```bash
# Start with monitoring profile
docker-compose --profile monitoring up -d

# Access Grafana
# http://localhost:3000
# Default: admin / admin
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest api/tests.py -v

# Run with markers
pytest -m django_db
```

---

## 🛠️ Troubleshooting

### Common Issues

**1. MySQL Connection Error**
```bash
# Make sure MySQL is running
# Check DB_HOST, DB_USER, DB_PASSWORD in .env
# For XAMPP: DB_HOST=localhost, DB_USER=root, DB_PASSWORD=
```

**2. Migrations Error**
```bash
# Reset migrations if needed
python manage.py migrate --run-syncdb
```

**3. Static Files Not Loading**
```bash
python manage.py collectstatic
```

**4. Permission Denied**
```bash
# Make sure virtual environment is activated
# Windows: env\Scripts\activate
# Linux/Mac: source env/bin/activate
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Mert Ural**
- GitHub: [@merturl4576](https://github.com/merturl4576)

---

## 🙏 Technologies

Built with:
- [Django](https://djangoproject.com) - Web framework
- [Django REST Framework](https://www.django-rest-framework.org) - REST API
- [Celery](https://celeryq.dev) - Async task queue
- [Redis](https://redis.io) - Cache & message broker
- [MySQL](https://mysql.com) - Database
- [Docker](https://docker.com) - Containerization
- [Bootstrap 5](https://getbootstrap.com) - UI framework
- [Chart.js](https://chartjs.org) - Data visualization
- [Graphene](https://graphene-python.org) - GraphQL

---

## 📸 Screenshots

### Dashboard
The main dashboard provides real-time overview of:
- Open incidents count and SLA compliance
- Service request status
- Recent activity feed
- Quick action buttons

### Remote Support
- Session queue for IT staff
- Real-time chat during support
- Voice-to-text transcription
- AnyDesk integration

### Staff Leaderboard
- Monthly performance rankings
- Points system for completed tasks
- Historical performance tracking

---

⭐ **Star this repo if you find it useful!**
