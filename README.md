---
**Student:** Parth Jain &nbsp;|&nbsp; **IITM ID:** 23f2003877 &nbsp;|&nbsp; **VIT ID:** 23bce10156  
**Programme:** IIT Madras BS in Data Science & Applications  
**Course:** Application Development II (MAD-II)

---

# 🎓 PPA — Placement Portal Application

> A full-stack **Campus Placement Management System** built for Application Development II.  
> Connects **students**, **companies (HR)**, and the **placement admin** in one unified platform.

---

## 📌 Project Overview

The **Placement Portal Application (PPA)** is a multi-role web application that digitises and streamlines the entire campus placement lifecycle — from company registration and drive creation to student applications, interview scheduling, and placement tracking.

**Three roles, one platform:**
- 🔵 **Admin** — Approves companies & drives, manages students, views analytics, generates reports
- 🟢 **Company / HR** — Registers, creates placement drives, manages applicants, schedules interviews
- 🟡 **Student** — Browses approved drives, applies, tracks status, checks ATS resume score, exports history

---

## ✨ Features

### 🔐 Authentication
- JWT token-based authentication (custom implementation using PyJWT)
- Role-based access control: `admin`, `company`, `student`
- Account deactivation and blacklisting by admin
- Secure password hashing with Werkzeug

> **Note on Flask-Security:** Flask-Security was evaluated during development. A custom JWT implementation (`auth.py`) was chosen instead to allow full control over token payload structure, role-based decorator logic, and user blacklist checks at the token-decode level — behaviours that required deeper integration than Flask-Security's out-of-the-box flow supports cleanly. The implementation follows the same security principles (token expiry, role enforcement, authenticated routes).

### 👩‍💼 Admin
- Dashboard with real-time stats and Chart.js visualisations (application breakdown, drive status)
- Approve / reject company registrations with notification
- Approve / reject / close placement drives
- Activate, deactivate, or blacklist students and companies
- Global search across students and companies
- View all applications with filters (by drive, by status)
- Trigger monthly placement reports (async via Celery)
- Download reports as HTML or PDF

### 🏢 Company / HR
- Self-registration (pending admin approval)
- Full company profile management
- Create, edit, and delete placement drives
- View applicants per drive with filtering
- Update application statuses: shortlisted → selected / rejected
- Schedule interviews (date, mode, venue)
- Record interview results (passed / failed)

### 🎓 Student
- Self-registration with profile (CGPA, department, graduation year, skills, bio)
- Resume upload (PDF, DOC, DOCX — max 5 MB)
- Browse and search approved placement drives
- Eligibility check before applying (CGPA, branch, graduation year)
- Apply with cover letter; withdraw if needed
- Track all applications and interview schedules
- **ATS Resume Checker** — AI-powered resume-vs-JD analysis (via Hugging Face Gradio)
- Export applications as CSV (async background job)
- Real-time in-app notifications

### ⚙️ Background Jobs (Celery + Redis)
| Task | Schedule | Description |
|---|---|---|
| `send_daily_reminders` | Every 24 hours | Emails students about drives with deadlines within 3 days |
| `generate_monthly_report` | Every 30 days | Generates HTML + PDF placement summary, emails admin |
| `export_applications_csv` | On-demand | Async CSV export of a student's application history |

### 🧠 Other
- Redis caching for dashboard stats and drive listings (reduces DB load)
- Google Chat webhook notifications for admin events
- Input validation for all user-submitted fields

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Flask 3.x, SQLAlchemy 2.x, Flask-CORS, Flask-Mail |
| **Auth** | PyJWT (custom JWT implementation — see note above) |
| **Frontend** | Vue 3 (CDN), Axios, Bootstrap 5, Chart.js |
| **Database** | SQLite (dev) — easily swappable to PostgreSQL |
| **Background Jobs** | Celery 5.x + Redis |
| **Caching** | Redis |
| **PDF Generation** | xhtml2pdf |
| **AI / ATS** | Hugging Face Gradio (`parthjain/ResumeAnalyser`) |

---

## 📁 Project Structure

```
P1- PPA/
├── run.py                      ← Top-level entry point
├── requirements.txt            ← Python dependencies
├── .env.example                ← Environment variable template
├── .gitignore
├── README.md
│
├── backend/
│   ├── app.py                  ← Flask application factory
│   ├── auth.py                 ← JWT auth helpers & decorators
│   ├── cache.py                ← Redis cache helpers
│   ├── celery_worker.py        ← Celery app + beat schedule
│   ├── config.py               ← App configuration (loads from .env)
│   ├── models.py               ← SQLAlchemy models
│   ├── tasks.py                ← Celery background tasks
│   ├── validators.py           ← Input validation helpers
│   └── routes/
│       ├── __init__.py
│       ├── admin.py            ← Admin API routes
│       ├── company.py          ← Company API routes
│       └── student.py          ← Student API routes
│
└── frontend/
    ├── static/
    │   ├── css/style.css       ← Custom stylesheet
    │   └── js/
    │       ├── app.js          ← Vue 3 main application
    │       └── pages.js        ← Vue page components
    └── templates/
        └── index.html          ← Single-page app entry point
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+
- Redis (running on `localhost:6379`)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ppa-placement-portal.git
cd ppa-placement-portal
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and fill in your actual values
# Required: SECRET_KEY, JWT_SECRET_KEY, ADMIN_EMAIL, ADMIN_PASSWORD
# Optional: MAIL_*, GCHAT_WEBHOOK_URL (for notifications)
```

Key variables in `.env`:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Flask session secret |
| `JWT_SECRET_KEY` | JWT signing secret |
| `ADMIN_EMAIL` | Admin account email (auto-created) |
| `ADMIN_PASSWORD` | Admin account password |
| `REDIS_URL` | Redis connection URL |
| `MAIL_USERNAME` | Gmail address for email notifications |
| `MAIL_PASSWORD` | Gmail App Password (not your account password) |

### 5. Run the Application

**Terminal 1 — Flask web server:**
```bash
python run.py
```
App runs at: http://localhost:5001

**Terminal 2 — Celery worker** (for background tasks):
```bash
cd backend
celery -A celery_worker.celery worker --loglevel=info
```

**Terminal 3 — Celery beat** (for scheduled tasks):
```bash
cd backend
celery -A celery_worker.celery beat --loglevel=info
```

### 6. First Login

The admin account is auto-created on first run using `ADMIN_EMAIL` and `ADMIN_PASSWORD` from your `.env`.

---

## 🔌 API Documentation

All endpoints use JSON. Protected endpoints require the `Authorization: Bearer <token>` header.

### Base URL
```
http://localhost:5001/api
```

---

### 🔐 Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/login` | ❌ | Login — returns JWT token |
| `POST` | `/auth/logout` | ✅ | Logout |
| `GET` | `/auth/me` | ✅ | Get current user + profile |

**Login Request:**
```json
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Login Response:**
```json
{
  "message": "Login successful",
  "token": "eyJ...",
  "user": { "id": 1, "email": "...", "role": "student" },
  "profile": { ... }
}
```

---

### 🎓 Student

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/students/register` | ❌ | Register new student |
| `GET` | `/students/profile` | ✅ Student | Get own profile |
| `PUT` | `/students/profile` | ✅ Student | Update profile & skills |
| `POST` | `/students/upload-resume` | ✅ Student | Upload resume (PDF/DOC/DOCX, max 5MB) |
| `GET` | `/student/drives` | ✅ Student | Browse approved drives (`?search=&branch=`) |
| `GET` | `/student/drives/<id>` | ✅ Student | Drive detail + applied status |
| `POST` | `/student/apply/<drive_id>` | ✅ Student | Apply for a drive |
| `GET` | `/student/applications` | ✅ Student | List all my applications |
| `PUT` | `/student/applications/<id>/withdraw` | ✅ Student | Withdraw application |
| `GET` | `/student/history` | ✅ Student | Placement history |
| `GET` | `/student/interviews` | ✅ Student | My scheduled interviews |
| `POST` | `/student/export-applications` | ✅ Student | Trigger async CSV export |
| `GET` | `/student/download-export/<job_id>` | ✅ Student | Download CSV when ready |
| `POST` | `/student/ats-check` | ✅ Student | ATS resume check against a drive's JD |

**Register Student:**
```json
POST /api/students/register
{
  "email": "student@college.edu",
  "password": "Pass@123",
  "full_name": "Parth Jain",
  "department": "Computer Science",
  "cgpa": 8.5,
  "graduation_year": 2025,
  "phone": "9876543210",
  "bio": "Passionate about software development",
  "skills": ["Python", "Vue.js", "SQL"]
}
```

**Apply for Drive:**
```json
POST /api/student/apply/3
{
  "cover_letter": "I am a strong fit for this role because..."
}
```

---

### 🏢 Company

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/companies/register` | ❌ | Register company |
| `GET` | `/companies/profile` | ✅ Company | Get company profile |
| `PUT` | `/companies/profile` | ✅ Company | Update profile |
| `GET` | `/company/dashboard` | ✅ Company | Dashboard stats |
| `GET` | `/company/drives` | ✅ Company | List my drives |
| `POST` | `/company/drives` | ✅ Company | Create drive |
| `PUT` | `/company/drives/<id>` | ✅ Company | Update drive |
| `DELETE` | `/company/drives/<id>` | ✅ Company | Delete drive |
| `GET` | `/company/drives/<id>/applications` | ✅ Company | View applicants |
| `PUT` | `/company/applications/<id>/status` | ✅ Company | Update status |
| `POST` | `/company/applications/<id>/schedule-interview` | ✅ Company | Schedule interview |
| `PUT` | `/company/applications/<id>/interview-result` | ✅ Company | Record result |
| `GET` | `/company/drives/<id>/interviews` | ✅ Company | List interviews for drive |

**Create Drive:**
```json
POST /api/company/drives
{
  "drive_name": "SDE Campus Drive 2025",
  "job_title": "Software Development Engineer",
  "job_description": "Backend development role...",
  "eligibility_branch": "Computer Science, Information Technology",
  "min_cgpa": 7.0,
  "eligible_year": 2025,
  "application_deadline": "2025-08-31T23:59:00",
  "location": "Bangalore",
  "salary": "12 LPA",
  "job_type": "Full-time"
}
```

---

### 👩‍💼 Admin

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/admin/dashboard` | ✅ Admin | Stats + chart data |
| `GET` | `/admin/search?q=&type=` | ✅ Admin | Search students/companies |
| `GET` | `/admin/companies` | ✅ Admin | All companies (`?status=pending`) |
| `GET` | `/admin/companies/pending` | ✅ Admin | Pending companies |
| `PUT` | `/admin/companies/<id>/approve` | ✅ Admin | Approve company |
| `PUT` | `/admin/companies/<id>/reject` | ✅ Admin | Reject company |
| `PUT` | `/admin/companies/<id>/blacklist` | ✅ Admin | Blacklist / un-blacklist |
| `GET` | `/admin/drives` | ✅ Admin | All drives (`?status=pending`) |
| `GET` | `/admin/drives/pending` | ✅ Admin | Pending drives |
| `PUT` | `/admin/drives/<id>/approve` | ✅ Admin | Approve drive |
| `PUT` | `/admin/drives/<id>/reject` | ✅ Admin | Reject drive |
| `PUT` | `/admin/drives/<id>/close` | ✅ Admin | Close drive |
| `GET` | `/admin/students` | ✅ Admin | All students |
| `PUT` | `/admin/students/<id>/deactivate` | ✅ Admin | Activate/deactivate |
| `PUT` | `/admin/students/<id>/blacklist` | ✅ Admin | Blacklist / un-blacklist |
| `GET` | `/admin/applications` | ✅ Admin | All applications (`?drive_id=&status=`) |
| `GET` | `/admin/reports/monthly` | ✅ Admin | List monthly reports |
| `POST` | `/admin/reports/generate` | ✅ Admin | Trigger async report |
| `GET` | `/admin/reports/download/<id>?format=pdf` | ✅ Admin | Download report |

---

### 🔔 Notifications & Jobs

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/notifications` | ✅ | Get notifications (last 50) |
| `PUT` | `/notifications/<id>/read` | ✅ | Mark one as read |
| `PUT` | `/notifications/read-all` | ✅ | Mark all as read |
| `GET` | `/jobs/<job_id>` | ✅ | Poll async job status |

**Job Status Response:**
```json
{
  "id": 5,
  "job_type": "export_applications_csv",
  "status": "completed",
  "file_path": "...",
  "created_at": "2025-07-01T10:00:00",
  "completed_at": "2025-07-01T10:00:05"
}
```

---

### ⚠️ Error Responses

