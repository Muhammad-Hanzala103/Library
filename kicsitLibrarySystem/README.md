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

## Phase 3 Consumers Commands

After Phase 2 is running, apply the consumers migration and refresh seed data:

```powershell
cd d:\Project\Library\kicsitLibrarySystem
.\.venv\Scripts\Activate.ps1
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Phase 3 adds:

- Student CRUD
- Employee CRUD
- Permanent Faculty
- Visiting Faculty
- Permanent Staff
- Temporary Staff
- Student status and clearance fields
- Page number and register number
- Search by registration number, admission number, P Number, CNIC, name, and phone
- Student and employee profile pages
- Activity logs for add and edit actions

## Phase 4 Circulation Commands

After Phase 3 is running, apply the circulation migration:

```powershell
cd d:\Project\Library\kicsitLibrarySystem
.\.venv\Scripts\Activate.ps1
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Phase 4 adds:

- Issue records
- Receive records
- Fines
- Issue Book screen
- Return Book screen
- Consumer and accession lookup before issue
- Issue limit checks
- Pending fine block
- Student clearance block
- Book status checks
- Book copy status updates on issue and return
- Overdue day and fine calculation
- Issue receive history
- Printable issue and return slips
- Activity logs for issue and return

## Phase 5 Reservation and Fine Commands

After Phase 4 is running:

```powershell
cd d:\Project\Library\kicsitLibrarySystem
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Phase 5 adds:

- Queue based reservations
- Reservation status flow
- Overdue dashboard
- Unpaid fines management
- Lost books
- Damaged books
- Reminder notification records
- WhatsApp placeholder notification records
- Overdue PDF export
- Overdue Excel export
- Activity logs for reservation, reminders, fine payment, lost, and damaged actions

## Phase 6 Clearance and History Commands

After Phase 5 is running:

```powershell
cd d:\Project\Library\kicsitLibrarySystem
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Phase 6 adds:

- Student clearance screen
- Clearance blocker checks for active issues, unpaid fines, unresolved lost cases, and unresolved damaged cases
- Clearance PDF
- Book history by accession number
- Issued and returned counts
- In-library check by selected date
- Status consistency checker
- Authorized status correction with reason

## Phase 7 Reports, Import, Export, and Search Commands

After Phase 6 is running:

```powershell
cd d:\Project\Library\kicsitLibrarySystem
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Phase 7 adds:

- Report engine
- PDF export
- Excel export
- CSV export
- Report filters
- Catalog reports
- Issue receive reports
- Overdue reports
- Fine reports
- Clearance reports
- Reservation reports
- Lost and damaged reports
- CSV import system
- Import preview and failed-row tracking
- Failed import error CSV download
- Global smart search

## Phase 8 Audit, Inventory, Documents, and Arrivals Commands

After Phase 7 is running:

```powershell
cd d:\Project\Library\kicsitLibrarySystem
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Phase 8 adds:

- HEC, PEC, NCEAC, QEC, internal, and other visit records
- Audit records with observations, suggestions, findings, recommendations, and action tracking
- Attachment documents for audit and visit evidence
- Furniture and equipment inventory
- New arrivals, journals, magazines, newspapers, reports, project reports, and thesis records
- SOP and National Library Rates upload with versioning
- Secure document validation and local document storage
- Document search and download
- PDF, Excel, and CSV reports for visits, audits, inventory, arrivals, and documents
- Activity logs for visit, audit, inventory, arrival, document upload, and report export actions

## Phase 9 Settings, Backup, Restore, and Documentation Commands

After Phase 8 is running:

```powershell
cd c:\Projects\Library\kicsitLibrarySystem
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Phase 9 adds:

- **Global ERP Configuration Console**: Settings page managing live database properties (circulation duration, borrow capacity, fines rate, reservation hold times, SMTP hosts, WhatsApp configurations, mysqldump locations, report headers).
- **Settings Service**: Dynamic parameter retrieval casting variables instantly (e.g. string to int, boolean, Decimal) without system restarts.
- **Automated Database Backup**: Super Admin dashboard capability to create one-click SQL dumps using native Windows binaries (`mysqldump`).
- **Disaster Recovery Restore**: Browser-based database restoration secured via strict permissions checking (`system.manage_all`) and two-factor text confirmation guardrails (`CONFIRM RESTORE`).
- **Enhanced Analytics Dashboard**: Integration of **Chart.js** canvases tracking 5 dynamic datasets, 22 granular administrative metrics, and a dynamic real-time system alerts panel.
- **Academic Thesis Documentation**:
  - `docs/INSTALLATION_GUIDE.md`: Local network hosting instructions, Windows Firewall rule creation, and environment setups.
  - `docs/FINAL_PROJECT_REPORT_OUTLINE.md`: 6-chapter graduation thesis blueprint for student **Muhammad Hanzala**.
  - `docs/PRESENTATION_POINTS.md`: Sequential slide sequence, defense outlines, and bullet points.
  - `docs/VIVA_PREPARATION.md`: Exhaustive 30-question prep manual covering web stacks, secure networking, and ORM mechanics.
  - `docs/MANUAL_TEST_CHECKLIST.md`: Operational test scenarios for system boundary testing.

