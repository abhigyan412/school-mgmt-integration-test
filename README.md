# School Management System — Skill Test Solution

## 👨‍💻 Candidate Submission

This document outlines all changes made to complete the skill test requirements.

---

## ✅ What Was Implemented

### Task 1 — Student CRUD Operations (Node.js Backend)

**File:** `backend/src/modules/students/students-controller.js`

All five missing controller handlers were implemented following the existing controller/service/repository pattern:

| Endpoint | Handler | Description |
|---|---|---|
| `GET /api/v1/students` | `handleGetAllStudents` | Returns filtered student list via query params |
| `POST /api/v1/students` | `handleAddStudent` | Creates student, sends verification email |
| `PUT /api/v1/students/:id` | `handleUpdateStudent` | Updates student details |
| `GET /api/v1/students/:id` | `handleGetStudentDetail` | Returns full student profile |
| `POST /api/v1/students/:id/status` | `handleStudentStatus` | Activates/deactivates student |
| `DELETE /api/v1/students/:id` | `handleDeleteStudent` | Deletes student record |

**Files changed:**
- `backend/src/modules/students/students-controller.js` — implemented all handlers
- `backend/src/modules/students/students-service.js` — added `deleteStudent` function
- `backend/src/modules/students/students-router.js` — added DELETE route

---

### Task 2 — Notice Description Bug Fix

**File:** `backend/src/modules/notices/notices-service.js`

**Problem:** The `description` field and `status` field were arriving as `undefined` in some flows, causing PostgreSQL to reject inserts since `description` is `NOT NULL`.

**Fix:** Added nullish coalescing defaults in `addNotice` and `updateNotice`:
```javascript
status: payload.status ?? 1,        // default to draft
description: payload.description ?? ""
```

---

### Task 3 — Python PDF Report Microservice

**Location:** `Python-service/`

A standalone FastAPI microservice that fetches student data from the Node.js backend and generates a downloadable PDF report.

#### Architecture

```
Python-service/
├── main.py              # FastAPI app, route definitions
├── api_client.py        # Node.js backend authentication & data fetching
├── report_generator.py  # PDF generation using ReportLab
├── schemas.py           # Pydantic models for type validation
├── config.py            # Settings via pydantic-settings + .env
├── requirements.txt     # Pinned dependencies
└── .env                 # Environment configuration
```

#### Endpoint

```
GET /api/v1/students/{student_id}/report
```

Returns a downloadable PDF file containing the student's full profile.

#### How It Works

1. Request hits FastAPI endpoint
2. `api_client.py` logs into Node.js backend (`POST /api/v1/auth/login`)
3. Extracts `accessToken`, `refreshToken`, `csrfToken` from `Set-Cookie` headers
4. Fetches student data (`GET /api/v1/students/:id`) with cookies + `x-csrf-token` header
5. `schemas.py` validates and maps the response to a `StudentProfile` model
6. `report_generator.py` generates a styled PDF with 4 sections
7. PDF is returned as a file download

#### PDF Report Sections
- **Personal Information** — name, email, DOB, gender, phone, admission date
- **Academic Information** — class, section, roll number, class teacher
- **Family Information** — father, mother, guardian details
- **Address Information** — current and permanent address

#### Security Handling
The Node.js backend uses a dual-token CSRF system:
- Login returns `accessToken` JWT (contains `csrf_hmac` claim) + `csrfToken` UUID cookie
- Every subsequent request must send the UUID as `x-csrf-token` header
- Backend verifies: `HMAC(header_token) === jwt.csrf_hmac`

This was implemented correctly in `api_client.py` with automatic re-authentication on token expiry.

#### Additional Changes
- `backend/src/config/cors.js` — updated to allow server-to-server requests with no `Origin` header

---

## 🚀 Running the Python Service

### Prerequisites
- Node.js backend running on `http://localhost:5007`
- Python 3.11+

### Setup
```bash
cd Python-service
pip install -r requirements.txt
python main.py
```

Service starts on **http://localhost:8000**

### API Docs
Open **http://localhost:8000/docs** for interactive Swagger UI

### Test
```bash
curl http://localhost:8000/api/v1/students/1/report --output report.pdf
```

---

## 🛠️ Tech Stack (Python Service)

| Library | Purpose |
|---|---|
| FastAPI | Web framework with auto Swagger docs |
| Uvicorn | ASGI server |
| ReportLab | PDF generation |
| Requests | HTTP client for Node.js API |
| Pydantic | Data validation and schemas |
| pydantic-settings | Environment config management |
| python-dotenv | `.env` file loading |

---

## 📸 Sample Output

See `samples/` folder for:
- Screenshot of Swagger UI with 200 OK response
- Sample generated PDF report

---

## 🔑 Demo Credentials

```
Email:    admin@school-admin.com
Password: 3OU4zn3q6Zh9
```
