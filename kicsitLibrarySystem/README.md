# KICSIT Library Management System

Advanced University Library Management System for Dr A Q Khan Institute of Computer Sciences and Information Technology, KICSIT.

Official student name for documentation: Muhammad Hanzala

## Project Purpose

This system is planned as a production-style replacement for the existing EMIS Library module. It will provide a secure, browser-based, multi-user library system for library staff, HOD office, director office, auditors, students, faculty, and staff on the local KICSIT library network.

The application will run first on a Windows server PC in the library and use one shared MySQL database accessed from browser clients on the local network.

## Frozen Technology Stack

- Backend: Python FastAPI
- Database: MySQL
- ORM: SQLAlchemy
- Migration tool: Alembic
- Front end: HTML, CSS, JavaScript, Jinja templates
- Authentication: JWT login with hashed passwords
- Reports: PDF, Excel, CSV
- File storage: Local secure storage with database metadata
- Email notifications: Required
- WhatsApp notifications: Future service placeholder only
- Deployment target: Windows local server first
- Database tool: MySQL Workbench

## Phase 0 Scope

Phase 0 freezes the requirements, architecture, folder structure, and database planning only. It does not implement FastAPI routers, SQLAlchemy models, Alembic migrations, templates, authentication, or business logic.

Created Phase 0 documentation:

- `docs/PHASE_0_ARCHITECTURE.md`
- `docs/DATABASE_PLANNING.md`
- `docs/DEVELOPMENT_ROADMAP.md`
- `docs/GROUP_WORK_DIVISION.md`

## Architecture Summary

The system will follow a layered FastAPI architecture:

- `routers`: HTTP endpoints and page routes
- `schemas`: Pydantic validation and response contracts
- `models`: SQLAlchemy ORM models
- `services`: business rules such as issue, return, fine, reservation, clearance, notification, import, and report logic
- `templates`: Jinja UI screens
- `static`: CSS, JavaScript, and images
- `uploads`: local secure uploaded files
- `reports`: generated report files
- `utils`: reusable helpers for security, files, dates, exports, email, and audit logs

## High-Level Modules

The final system is planned around authentication, user management, role and permission control, dashboard, catalog, book copies, consumers, issue return workflow, reservations, overdue management, fines, lost and damaged books, student clearance, reports, import export, audit and accreditation, inventory, documents, notifications, backup restore, global search, activity logs, and settings.

## Current Folder Structure

```text
kicsitLibrarySystem/
  app/
    models/
    reports/
    routers/
    schemas/
    services/
    static/
      css/
      img/
      js/
    templates/
      audit/
      auth/
      catalog/
      circulation/
      consumers/
      copies/
      dashboard/
      documents/
      errors/
      fines/
      inventory/
      reports/
      reservations/
      settings/
      users/
    uploads/
      book_images/
      documents/
      invoices/
    utils/
  docs/
  migrations/
  tests/
```

## Phase 1 Run Commands

Create and activate a virtual environment from the project folder:

```powershell
cd d:\Project\Library\kicsitLibrarySystem
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `.env` from `.env.example`, then create the MySQL database in MySQL Workbench:

```sql
CREATE DATABASE kicsit_library CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Apply migrations and seed users:

```powershell
alembic upgrade head
python -m app.seed
```

Run the application:

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/login
```

Seed users:

| Role | Username | Email | Password |
| --- | --- | --- | --- |
| Super Admin | `superadmin` | `superadmin@kicsit.local` | `ChangeMe@123` |
| Admin | `admin` | `admin@kicsit.local` | `ChangeMe@123` |
| Librarian | `librarian` | `librarian@kicsit.local` | `ChangeMe@123` |
| Assistant Librarian | `assistant` | `assistant@kicsit.local` | `ChangeMe@123` |

Change these passwords before production use.

## Phase 2 Catalog Commands

After Phase 1 is running, apply the catalog migration and refresh seed data:

```powershell
cd d:\Project\Library\kicsitLibrarySystem
.\.venv\Scripts\Activate.ps1
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Phase 2 adds:

- Authors
- Publishers
- General categories
- Department categories
- Literature categories
- Book master records
- Accession copies
- Unique accession number validation
- JPG and PNG book image upload
- Location, rack, shelf, and hall fields
- Basic catalog search
- CSV import template download
- Activity logs for add, edit, and delete actions
