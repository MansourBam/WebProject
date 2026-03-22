# 🎓 University Management System

Flask web app for managing students, teachers, and courses. Role-based access: Admin, Teacher, Student.

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/university_management.git
cd university_management
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # Windows
# source .venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5001**

> Configure SQL Server in `database_fallback.py` before running.

## Demo Logins

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@university.edu | admin123 |
| Student | student@university.edu | student123 |
| Teacher | teacher@university.edu | teacher123 |
