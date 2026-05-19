# Development Roadmap

Project: KICSIT Library Management System  
Roadmap scope: Phase 0 through Phase 9

## Phase 0: Requirements and Architecture Freeze

Goal:

Freeze final requirements, architecture, folder structure, screen list, module list, database entity list, ERD explanation, roadmap, and team division.

Deliverables:

1. README overview.
2. Architecture summary.
3. Final module list.
4. Final screen list.
5. Final database entity list.
6. ERD explanation.
7. Folder structure.
8. Phase-wise roadmap.
9. Three-student work division.

No application code is implemented in this phase.

## Phase 1: FastAPI Foundation and Database Base

Goal:

Create the runnable application foundation.

Planned deliverables:

1. `main.py`
2. `config.py`
3. `database.py`
4. Python package initialization.
5. Requirements file.
6. Environment example file.
7. SQLAlchemy base setup.
8. Alembic setup.
9. Health check route.
10. Base layout template.
11. Initial smoke test.

## Phase 2: Authentication, Roles, Permissions, and Activity Logs

Goal:

Implement secure login and access control.

Planned deliverables:

1. User, role, permission models.
2. Password hashing.
3. JWT authentication.
4. Session timeout.
5. Login and logout.
6. Failed login tracking.
7. Role and permission seed data.
8. Access denied page.
9. Activity log service.
10. Admin, librarian, assistant librarian seed accounts.

## Phase 3: Catalog Foundation

Goal:

Implement the book master, authors, publishers, categories, and accession copy system.

Planned deliverables:

1. Author management.
2. Publisher management.
3. Category management.
4. Department categories.
5. Literature categories.
6. Book master create, edit, detail, list.
7. Book copy create, edit, detail, list.
8. Accession number uniqueness validation.
9. Book image and invoice upload validation.
10. Catalog search basics.

## Phase 4: Consumers and Circulation

Goal:

Implement students, employees, issue workflow, return workflow, and issue receive history.

Planned deliverables:

1. Student management.
2. Employee management.
3. Issue book screen.
4. Return book screen.
5. Issue limit checks.
6. Clearance block checks.
7. Active issue duplicate prevention.
8. Fine calculation during return.
9. Issue slip and return slip.
10. Issue receive history filters.

## Phase 5: Reservations, Overdue, Fines, Lost, Damaged, and Clearance

Goal:

Implement circulation control modules that solve daily librarian problems.

Planned deliverables:

1. Queue-based reservation system.
2. Reservation ready for pickup.
3. Reservation expiry logic.
4. Overdue dashboard.
5. Manage unpaid fines.
6. Paid fine records.
7. Fine waiver with reason.
8. Lost book cases.
9. Damaged book cases.
10. Student clearance workflow.
11. Clearance letter PDF.
12. Book history by accession number.
13. Book status consistency checker.

## Phase 6: Reports, Import, Export, and Documents

Goal:

Implement professional report generation and secure document management.

Planned deliverables:

1. Report dashboard.
2. Catalog reports.
3. Issue and return reports.
4. Overdue and fine reports.
5. Student status and clearance reports.
6. Audit, visit, inventory, and document reports.
7. PDF export.
8. Excel export.
9. CSV export.
10. Import templates.
11. Import preview.
12. Import batch records.
13. Import error records and error file download.
14. SOP document uploads.
15. National Library Rates uploads.
16. Invoice uploads.

## Phase 7: Audit, Accreditation, Inventory, New Arrivals, and Notifications

Goal:

Implement institutional record modules and communication features.

Planned deliverables:

1. HEC, PEC, NCEAC, QEC, internal, and other visit records.
2. Audit records.
3. Audit evidence uploads.
4. Visit evidence uploads.
5. Furniture and equipment inventory.
6. New arrivals.
7. Journals and magazines records.
8. Email notification service.
9. Due tomorrow email reminders.
10. Overdue email reminders.
11. Reservation ready email reminders.
12. Fine email reminders.
13. Clearance update email reminders.
14. WhatsApp service interface placeholder.

## Phase 8: Dashboard, Global Search, Settings, Backup, and Polish

Goal:

Complete ERP-level administration, analytics, and usability.

Planned deliverables:

1. Dashboard metric cards.
2. Monthly issue trend chart.
3. Department-wise books chart.
4. CS versus CE chart.
5. Overdue trend chart.
6. Most issued books chart.
7. Quick alerts.
8. Recent activity feed.
9. Global smart search.
10. Settings pages.
11. Report header settings.
12. Email settings.
13. Backup creation.
14. Restore workflow with admin permission.
15. UI polish.
16. Responsive laptop and desktop layout verification.

## Phase 9: Testing, Documentation, Deployment, and Final Submission

Goal:

Prepare the system for demonstration, viva, and local Windows deployment.

Planned deliverables:

1. Automated tests for core services.
2. Manual test checklist.
3. Security checklist.
4. Windows local server deployment guide.
5. MySQL Workbench setup guide.
6. Admin user guide.
7. Librarian user guide.
8. Final project report outline.
9. Presentation points.
10. Viva questions and answers.
11. Known limitations.
12. Future enhancement list.

## Phase Control Rules

1. At the start of every phase, list files that will be created or modified.
2. At the end of every phase, list completed work, commands to run, and manual test steps.
3. Do not write unrelated modules early.
4. Do not create fake buttons.
5. Do not create placeholder pages unless explicitly allowed and connected to planned backend behavior.
6. Keep business logic in services.
7. Keep database models separate from schemas.
8. Keep validation schemas separate from templates.
9. Keep reports filterable and exportable.
10. Log sensitive actions.

