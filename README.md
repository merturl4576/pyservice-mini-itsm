# 🚀 PyService - Enterprise ITSM Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://djangoproject.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)](https://mysql.com)

A production-ready IT Service Management (ITSM) platform built with Django, inspired by ServiceNow. Features remote support sessions, real-time chat, staff performance leaderboards, SLA tracking, and enterprise-grade security.

---

## 🆕 What's New in v2.0

- **🖥️ Remote Support Sessions** - Real-time remote assistance with AnyDesk integration, chat, and voice-to-text
- **👥 Staff Performance Leaderboard** - Track and gamify IT support performance
- **📊 Enhanced Reports Dashboard** - Detailed analytics with remote session statistics
- **🔔 Real-time Notifications** - WebSocket-based instant notifications
- **📅 Interactive Calendar** - Visual calendar view for incidents and requests

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Incident Management** | ITIL-compliant workflow with priority matrix |
| **SLA Tracking** | Automatic SLA calculation with breach detection |
| **Service Requests** | Multi-step approval workflow |
| **Asset Management** | Complete CMDB for IT assets |
| **Knowledge Base** | Searchable FAQ articles |
| **Remote Support** | Live remote assistance sessions |
| **Staff Leaderboard** | Performance tracking with gamification |
| **Dashboard** | Real-time analytics with Chart.js |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MySQL (XAMPP or standalone)
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/merturl4576/pyservice-mini-itsm.git
cd pyservice-mini-itsm

# Create virtual environment
python -m venv env
env\Scripts\activate  # Windows

# Install dependencies
cd pyservice
pip install -r requirements.txt

# Create database 'pyservice_db' in phpMyAdmin

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start server
python manage.py runserver

# Open http://127.0.0.1:8000
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

## 👨‍💻 Author

**Mert Ural** - [@merturl4576](https://github.com/merturl4576)

---
⭐ Star this repo if you find it useful!
