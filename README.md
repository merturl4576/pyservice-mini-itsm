# 🚀 PyService - Enterprise ITSM Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://djangoproject.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
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
| **Async Tasks** | Celery + Redis |
| **Real-time** | WebSocket (Django Channels) |
| **REST API** | Django REST Framework + JWT |
| **GraphQL** | Graphene-Django |
| **PDF Export** | ReportLab |
| **Monitoring** | Prometheus + Grafana |

---

## 🚀 Quick Start

### Prerequisites

Before you begin, make sure you have:
- **Python 3.11+** installed
- **MySQL** running (XAMPP, standalone MySQL, or Docker)
- **Git** installed

### Installation Steps

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

# 5. Run database migrations
python manage.py migrate

# 6. Create admin user
python manage.py createsuperuser

# 7. Start development server
python manage.py runserver

# 8. Open in browser
# http://127.0.0.1:8000
```

### Using Docker

```bash
# Clone repository
git clone https://github.com/merturl4576/pyservice-mini-itsm.git
cd pyservice-mini-itsm

# Configure environment
cp .env.docker .env.docker.local

# Start all services
docker-compose up -d

# Create superuser
docker-compose exec django python manage.py createsuperuser

# Access the application
# http://localhost:80
```

---

## 📂 Project Structure

```
pyservice-mini-itsm/
├── pyservice/
│   ├── api/                    # REST API
│   ├── cmdb/                   # Asset management
│   ├── incidents/              # Incident tracking
│   ├── service_requests/       # Request workflow
│   ├── remote_support/         # Remote support sessions
│   ├── notifications/          # WebSocket notifications
│   ├── graphql_api/            # GraphQL
│   ├── reports/                # PDF export
│   ├── templates/              # HTML templates
│   └── pyservice/              # Django settings
├── docker/                     # Docker configuration
├── Dockerfile
├── docker-compose.yml
├── LICENSE
└── README.md
```

---

## 👥 User Roles

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
```

---

## 🛠️ Troubleshooting

### Common Issues

**MySQL Connection Error**
```bash
# Make sure MySQL is running
# Check DB_HOST, DB_USER, DB_PASSWORD in .env
# For XAMPP: DB_HOST=localhost, DB_USER=root, DB_PASSWORD=
```

**Migrations Error**
```bash
python manage.py migrate --run-syncdb
```

**Static Files Not Loading**
```bash
python manage.py collectstatic
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

---

⭐ **Star this repo if you find it useful!**
