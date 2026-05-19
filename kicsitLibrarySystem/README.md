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

## Next Phase

Phase 1 should create the runnable FastAPI foundation:

- Python package files
- configuration
- database connection
- dependency setup
- Alembic initialization
- base models setup
- authentication foundation
- seed plan
- first smoke tests

