# Astra — Team Task Manager

A full-stack team task manager built with Python/Flask, featuring dark glassmorphism UI, role-based access control (RBAC), and real-time dashboard metrics.

---

## Features

| Feature | Details |
|---|---|
| 🔐 Authentication | Secure signup/login with bcrypt password hashing |
| 👥 RBAC | Admin and Member roles — Admins create projects & assign tasks |
| 📊 Dashboard | Total/pending/overdue metrics + Chart.js completion trend graph |
| 📁 Projects | Admin can create/delete projects; all users view progress |
| ✅ Tasks | Inline status updates (AJAX), overdue highlighting, red pulse indicators |
| 🎨 UI | Dark glassmorphism (#0a0a0a), orange accents (#f97316), animated modals |
| 🚀 Deployment | Railway/Heroku-ready with Procfile & gunicorn |

---

## Local Setup

### 1. Clone & enter directory
```bash
git clone <your-repo-url>
cd project-Astra
```

### 2. Create virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
copy .env.example .env     # Windows
# cp .env.example .env     # macOS/Linux
# Edit .env and set a strong SECRET_KEY
```

### 5. Run the app
```bash
flask run
# or
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## Demo Accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@astra.dev | admin123 |
| Member | member@astra.dev | member123 |

These are seeded automatically on first run.

---

## RBAC Summary

| Action | Admin | Member |
|---|---|---|
| View Dashboard | ✅ | ✅ |
| Create Project | ✅ | ❌ |
| Create & Assign Task | ✅ | ❌ |
| Change Task Status | ✅ (any) | ✅ (own only) |
| Delete Tasks/Projects | ✅ | ❌ |

---

## Railway Deployment

1. Push to GitHub
2. Connect repo to [Railway](https://railway.app)
3. Add environment variables:
   - `SECRET_KEY` — a long random string
   - `DATABASE_URL` — Railway PostgreSQL URL (auto-set if you add a PostgreSQL plugin)
4. Railway detects `Procfile` and runs `gunicorn app:app` automatically

---

## Project Structure

```
project-Astra/
├── app.py              # Routes, dashboard metrics, chart API
├── auth.py             # Login/signup/logout + RBAC decorators
├── models.py           # SQLAlchemy User, Project, Task models
├── requirements.txt
├── Procfile
├── .env.example
└── templates/
│   ├── base.html       # Sidebar layout
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── projects.html
│   └── tasks.html
└── static/
    ├── css/style.css   # Glassmorphism design system
    └── js/app.js       # Chart.js, AJAX, modals, validation
```
