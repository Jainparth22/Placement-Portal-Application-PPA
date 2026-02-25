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
