# Abuyog Community College Health Consultation System

A scalable Flask + Jinja2 + SQLite web application with session-based authentication and RBAC for:

- Super Admin
- Medical Expert
- Student

## Main features

- Secure password hashing with Werkzeug
- Flask-Login authentication
- SQLAlchemy ORM
- Scalable Role model with many-to-many User/Role relationship
- Super Admin user management, role assignment, announcements, audit logs
- Medical Expert medical records, health requests, appointments, reports
- Student profile, health requests, personal medical history, announcements
- BEE-inspired yellow/orange responsive interface
- SQLite database
- Audit logging for important actions

## Default development accounts

These are created by `python init_db.py`:

- Super Admin: `admin@acc.edu` / `Admin@12345`
- Medical Expert: `medical@acc.edu` / `Medical@12345`
- Student: `student@acc.edu` / `Student@12345`

Change these passwords before real deployment.

## Run

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_db.py
python run.py
```

Open http://127.0.0.1:5000

For a production deployment, use a production WSGI server, HTTPS, a real secret key, stronger database infrastructure, CSRF protection, backups, and proper privacy controls.
