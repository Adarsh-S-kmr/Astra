# ☄️ Astra — Intelligent Task Velocity Engine

Astra is a high-performance, full-stack task management platform designed with a **premium dark-mode glassmorphism** aesthetic. It provides teams with a streamlined "Mission Control" to track projects, manage task velocity, and maintain production standards through an intuitive, high-density dashboard.

![Astra Banner](https://raw.githubusercontent.com/Adarsh-S-kmr/Astra/main/static/js/logo.png)

## 💎 Design Philosophy
Astra is built to look and feel like a modern financial terminal or aerospace control system. It utilizes:
*   **Glassmorphism**: Layered transparency with real-time backdrop-blur.
*   **Cyber-Orange Accents**: High-contrast indicators for critical task status.
*   **Micro-Animations**: Smooth transitions and status "pulses" for live feedback.

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **📊 Mission Control** | Real-time analytics dashboard with 14-day velocity tracking via Chart.js. |
| **🛡️ RBAC Security** | Role-Based Access Control distinguishing Administrative and Member permissions. |
| **📁 Pipeline Management** | Multi-project tracking with progress bars and automated completion percentages. |
| **⚡ Instant Actions** | AJAX-powered status updates (Todo → In Progress → Done) without page reloads. |
| **⏰ Velocity Alerts** | Visual pulse indicators for overdue tasks and upcoming deadlines. |
| **⌨️ Command Palette** | Power-user shortcuts (`Ctrl+K`) for rapid navigation across the workspace. |

## 🛠️ Tech Stack
*   **Backend**: Python / Flask
*   **Database**: PostgreSQL (Production) / SQLite (Development)
*   **Frontend**: Vanilla JS (ES6+), HTML5, CSS3 (Custom Design System)
*   **Charts**: Chart.js v4.4
*   **Security**: Bcrypt Hashing, Session-based RBAC
*   **Deployment**: Railway.app / Gunicorn

## 🚥 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Adarsh-S-kmr/Astra.git
cd Astra
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Environment
Create a `.env` file in the root directory:
```env
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///astra.db
```

### 4. Launch Application
```bash
python app.py
```

## 🧪 Demo Access
If you are visiting the live deployment, use these credentials to explore the workspace:

| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@gmail.com` | `admin123` |
| **Member** | `member@gmail.com` | `member123` |

---
*Created with ❤️ by Adarsh S Kumar*
