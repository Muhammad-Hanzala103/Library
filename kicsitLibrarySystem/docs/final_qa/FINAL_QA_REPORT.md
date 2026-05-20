# Final QA Report

Project name: KICSIT Library Management System
Test date: 2026-05-20
Tested by: Codex final QA/security/database/API/UI/release audit
Environment: Windows, Python 3.13.13, clean `.qa-venv`, FastAPI TestClient, Uvicorn smoke server on `127.0.0.1:8011`
Database name: `kicsit_library` configured, live MySQL unavailable on `127.0.0.1:3306`
Backend version: FastAPI 0.115.6
Front end type: Jinja HTML templates, CSS, JavaScript

## Stack Detected

- FastAPI backend with 91 registered routes after startup fix.
- MySQL configured through SQLAlchemy and PyMySQL.
- Alembic migrations in `migrations/versions`.
- Jinja templates in `app/templates`.
- Static assets in `app/static`.
- JWT cookie authentication using `python-jose`.
- Role and permission checks through `require_permission`.
- Report export code for PDF, Excel, and CSV.
- File upload code for book images and documents.
- Backup/restore service through `mysqldump` and `mysql` binaries.

## File Inventory

| Folder | Purpose | Important files | Missing files | Risk |
|---|---|---|---|---|
| `app/models` | SQLAlchemy tables | `auth.py`, `catalog.py`, `circulation.py`, `consumers.py`, `phase5.py`, `phase7.py`, `phase8.py`, `settings.py` | None for required 32 table names | Medium |
| `app/routers` | Web/page endpoints | auth, dashboard, catalog, consumers, circulation, reports/imports, settings, backup | Dedicated JSON REST API routers are mostly absent | High |
| `app/schemas` | Pydantic form validation | auth, catalog, circulation, consumers, phase5 | Phase7/Phase8 schemas are missing | Medium |
| `app/services` | Business logic | auth, activity logs, catalog, circulation, reports, imports, backup | Some operations are shallow/partial | High |
| `app/templates` | UI screens | 41 templates | Users/roles/permissions management screens are missing | High |
| `app/static` | CSS/JS | `app.css`, `app.js` | No image assets folder | Low |
| `app/uploads` | Runtime uploads | Created at runtime by services | Not present initially | Medium |
| `migrations` | Alembic migrations | 0001-0008 | None detected | Medium |
| `tests` | Automated QA smoke tests | `test_final_qa_smoke.py` | Full database/browser/API tests still require MySQL | Medium |

## Phase A Fresh Installation Test

| Test | Command | Expected | Actual | Status | Fix applied | Retest |
|---|---|---|---|---|---|---|
| Create fresh venv | `python -m venv .qa-venv` | venv created | Created | Pass | None | Pass |
| Install requirements | `.qa-venv\Scripts\python -m pip install -r requirements.txt` | Dependencies install | Installed; initial bcrypt 5 broke hashing | Fail then Pass | Pinned `bcrypt==4.2.1` | Pass |
| Import app | `python -c "from app.main import app"` | Imports | Initially failed on route union return annotations | Fail then Pass | Removed invalid route union annotations | Pass |
| Start server | Uvicorn on 8011 plus HTTP checks | `/health` and `/login` load | `health=200`, `login=200` | Pass | Startup fix | Pass |
| Create MySQL DB | `mysql ...` / PyMySQL connect | DB reachable | MySQL client missing, server refused 3306 | Fail | Not fixable in code | Fail |
| Alembic upgrade | `alembic upgrade head` | Migrations apply | OperationalError, MySQL refused connection | Fail | Not fixable in code | Fail |
| Seed script | `python -m app.seed` | Seed users created | Not run because DB unavailable | Blocked | None | Blocked |
| Login seeded users | Browser/API login | Login succeeds | Blocked by DB | Blocked | None | Blocked |
| Data persistence | Restart and verify | Data persists | Blocked by DB | Blocked | None | Blocked |

## Phase B Database Audit

Static SQLAlchemy metadata contains all 32 required table names. Live table, PK, FK, constraint, index, and consistency-query execution is blocked until MySQL is running.

Required table metadata status: Partial Pass.

Missing or partial audit findings:
- `settings` and category tables do not consistently include `created_at` and `updated_at`.
- `newarrivals` model has no `updated_at` despite migration output indicating one should exist.
- Several logical operations rely on application checks rather than database-level constraints.
- Live duplicate accession and status consistency SQL counts could not be run.

## Phase C Authentication and Authorization

Executed:
- Password hashing and verification smoke test.
- JWT valid/tampered token smoke test.
- Protected routes redirect to `/login` without session.
- Static permission dependency review across routers.

Status: Partial.

Critical seed role gap:
- Seed users include Super Admin, Admin, Librarian, Assistant Librarian only.
- Student, Faculty, Staff, Auditor, and Read Only Viewer test users are missing.
- Permission model contains only broad permissions, not fine-grained CRUD/delete/waive/export permissions.

## Phase D API Testing

Implemented application is primarily server-rendered HTML routes, not a full JSON REST API. Automated smoke tests were added and passed:

- App startup and public pages.
- Required SQLAlchemy table metadata.
- Password hash and JWT security utility.
- Protected-route redirects.
- File upload validation.

Result: 10 passed, 0 failed, 3 warnings.

Status: Partial because database-backed endpoints could not be executed without MySQL.

## Phase E UI and Browser Testing

Executed:
- Uvicorn smoke server.
- HTTP GET `/health` and `/login`.
- Login page content check.

Blocked:
- Authenticated pages, forms, reports, exports, role UI, and full browser automation require seeded MySQL data.

Status: Partial.

## Core Workflow Status

| Workflow | Status | Reason |
|---|---|---|
| Add book and copies | Partial | Code exists; DB/UI workflow blocked |
| Issue book to student | Partial | Code exists; DB/UI workflow blocked |
| Return on time | Partial | Code exists; DB/UI workflow blocked |
| Return late/fine | Partial | Fine calculation code exists and static fix verified |
| Reservation | Partial | Code exists; DB/UI workflow blocked |
| Student clearance | Partial | Code exists; DB/UI workflow blocked |
| Lost/damaged | Partial | Code exists; DB/UI workflow blocked |
| Book history | Partial | Code exists; DB/UI workflow blocked |
| Status checker | Partial | Code exists; DB/UI workflow blocked |

## Reports Status

Implemented report groups are far fewer than the requested 39 detailed reports. General catalog/issues/overdue/fines/clearance/reservations/lost-damaged and Phase 8 reports exist. Many named reports are missing as distinct report types.

Status: Partial.

## Security Status

Fixed during QA:
- App startup DoS from invalid FastAPI route return annotations.
- Password hashing dependency break from bcrypt 5.
- Active issue deletion guard present in catalog service.
- Backup restore confirmation is server-side enforced.
- Backup password is passed through environment instead of command line.
- CSV import validates extension, empty file, and file size.
- Sidebar links are permission-gated.

Remaining risks:
- MySQL unavailable, so live authorization and activity log checks could not be completed.
- Roles are too broad for strict university production permissions.
- Backup restore still needs full live restore test.
- Error handling for DB-down state still returns stack traces in CLI; browser behavior not fully tested.

## Final Counts

Total modules inspected: 29
Executable test cases run: 17
Passed executable cases: 13
Failed executable cases: 4
Blocked cases: all MySQL-backed workflows
Critical bugs found: 3
Major bugs found: 8
Minor bugs found: 3
Fixed bugs: 6
Pending limitations: 12+

## Final Decision

Ready for demo: No
Ready for deployment: No

Reason: The app now starts and smoke tests pass, but MySQL fresh setup fails in the current environment, seeded login and data workflows could not be executed, and several required roles/reports/API groups are missing or partial.
