# Phase 0 Architecture Freeze

Project: KICSIT Library Management System  
Institute: Dr A Q Khan Institute of Computer Sciences and Information Technology, KICSIT  
Documentation student name: Muhammad Hanzala  
Phase: 0 only  
Status: Requirements, architecture, screens, folder structure, and database planning frozen for implementation phases.

## Architecture Summary

The system will be a browser-based university ERP module focused on library operations. It will replace the current EMIS Library workflows with one normalized MySQL-backed application that multiple authorized users can access from library computers and office systems on the same local network.

The first deployment target is a Windows local server PC in the library. The application will expose FastAPI routes through a local address such as a server IP or local hostname. All users will work on the same MySQL database.

## Architectural Layers

1. Presentation layer
   - Jinja templates for server-rendered pages.
   - HTML, CSS, and JavaScript for forms, filters, searchable tables, charts, print actions, and validation feedback.
   - Layout will use a professional ERP sidebar, top bar, dashboard cards, and clean data screens.

2. API and route layer
   - FastAPI routers grouped by module.
   - Protected routes will require authenticated user context.
   - Permission checks will be applied before showing pages and before executing actions.

3. Validation layer
   - Pydantic schemas for request validation and structured responses.
   - Server-side validation will be mandatory even when client-side validation exists.

4. Business service layer
   - Business rules will live in services, not in templates.
   - Issue, return, fine calculation, reservation queue, clearance, notification, upload, import, export, backup, and audit logic will be implemented here.

5. Data access layer
   - SQLAlchemy ORM models will represent normalized MySQL tables.
   - Alembic migrations will manage database schema changes.
   - ORM queries will be used to reduce SQL injection risk.

6. Infrastructure layer
   - Local file storage for approved uploads only.
   - Email service for notifications.
   - WhatsApp interface placeholder for future integration.
   - Report generators for PDF, Excel, and CSV.

## Security Architecture

1. Authentication
   - Login by username or email.
   - Passwords hashed with a modern password hashing algorithm.
   - JWT-based authenticated sessions.
   - Session timeout.
   - Logout.
   - Failed login tracking.

2. Authorization
   - Role-based page access.
   - Permission-based action and button access.
   - Access denied page for unauthorized users.
   - Every protected route checks current user and permission.

3. Data protection
   - Server-side input validation.
   - ORM-based database operations.
   - Template escaping to reduce XSS exposure.
   - Soft delete for important records.
   - Deletion reason required for sensitive records.
   - Fine waiver reason required.
   - Activity logs for sensitive actions.

4. File upload protection
   - Allow only PDF, DOCX, XLSX, CSV, JPG, and PNG.
   - Reject executable and unsafe extensions.
   - Enforce file size limit from settings.
   - Rename files safely.
   - Store metadata in database.
   - Do not expose physical server paths.

## Final Module List

1. Authentication and security
2. User management
3. Role and permission management
4. Dashboard
5. Student management
6. Employee management
7. Author management
8. Publisher management
9. Category management
10. Department category management
11. Literature category management
12. Book catalog management
13. Book copy and accession management
14. Library catalog search
15. Issue book
16. Return book
17. Issue receive history
18. Reservation system
19. Overdue management
20. Fine management
21. Manage unpaid fines
22. Lost books
23. Damaged books
24. Book history
25. Book status consistency checker
26. Student clearance
27. Student status
28. Notifications
29. Reports
30. Import and export
31. Audit and accreditation
32. Visit records
33. Audit records
34. Furniture and equipment inventory
35. New arrivals
36. Journals and magazines
37. SOP and documents
38. National Library Rates documents
39. Backup and restore
40. Global smart search
41. Activity logs
42. Settings

## Final Screen List

### Authentication Screens

1. Login
2. Logout action
3. Forgot password request
4. Password reset
5. Access denied
6. Session expired

### Dashboard Screens

1. Main librarian dashboard
2. Admin dashboard
3. Auditor dashboard
4. Student self-service dashboard
5. Faculty and staff self-service dashboard

### User and Security Screens

1. Users list
2. Create user
3. Edit user
4. User detail
5. Assign roles
6. Roles list
7. Create role
8. Edit role
9. Permission matrix
10. Login attempt history

### Consumer Screens

1. Students list
2. Student create
3. Student edit
4. Student profile
5. Student status management
6. Student clearance search
7. Student clearance detail
8. Student clearance letter
9. Employees list
10. Employee create
11. Employee edit
12. Employee profile
13. Faculty and staff issue history

### Catalog Screens

1. Book masters list
2. Add book master
3. Edit book master
4. Book master detail
5. Authors list
6. Publishers list
7. Categories list
8. Department categories list
9. Literature categories list
10. Book copies list
11. Add accession copy
12. Edit accession copy
13. Copy detail
14. Delete copy with reason
15. Restore deleted copy
16. Catalog advanced search
17. Book history by accession number
18. Book status consistency checker
19. Consistency correction form

### Circulation Screens

1. Issue book
2. Issue confirmation
3. Issue slip print
4. Return book
5. Return confirmation
6. Return slip print
7. Issue receive history
8. Active issues list
9. Consumer current issued books

### Reservation Screens

1. Reservations list
2. Create reservation
3. Reservation queue
4. Mark ready for pickup
5. Complete reservation
6. Cancel reservation with reason
7. Expired reservations

### Fine, Overdue, Lost, and Damaged Screens

1. Overdue dashboard
2. Overdue filtered list
3. Send reminder action
4. Fines list
5. Unpaid fines
6. Paid fines
7. Fine detail
8. Mark fine paid
9. Fine waiver with reason
10. Lost books list
11. Lost book detail
12. Resolve lost book
13. Damaged books list
14. Damage detail
15. Resolve damaged book

### Report Screens

1. Reports dashboard
2. Full library catalog report
3. Book category report
4. CS books report
5. CE books report
6. Urdu literature report
7. English literature report
8. History literature report
9. Islam literature report
10. Accession wise report
11. Available books report
12. Issued books report
13. Return report
14. Issue receive history report
15. Issue date report
16. Receive date report
17. Overdue of library holding report
18. Manage unpaid fines report
19. Paid fines report
20. Lost books report
21. Damaged books report
22. Student status report
23. Cleared students report
24. Not cleared students report
25. Student clearance report
26. Employee issue report
27. Faculty staff report
28. Reservation report
29. Book history report
30. Status inconsistency report
31. Visit records report
32. Audit records report
33. Furniture equipment report
34. New arrivals report
35. Journals report
36. Magazines report
37. SOP documents report
38. National Library Rates report
39. Activity logs report
40. Backup report

### Import and Export Screens

1. Import dashboard
2. Book import
3. Book copy import
4. Student import
5. Employee import
6. Author import
7. Publisher import
8. Inventory import
9. New arrivals import
10. Import preview
11. Import error list
12. Import batch history
13. Template download actions

### Audit and Accreditation Screens

1. Visit records list
2. Add visit record
3. Edit visit record
4. Visit detail
5. Audit records list
6. Add audit record
7. Edit audit record
8. Audit detail
9. Audit evidence upload
10. Visit evidence upload

### Inventory and Arrival Screens

1. Furniture and equipment list
2. Add inventory item
3. Edit inventory item
4. Inventory item detail
5. New arrivals list
6. Add new arrival
7. Journals list
8. Magazines list
9. Newspapers list

### Document Screens

1. Documents list
2. Upload document
3. Document detail
4. SOP documents
5. National Library Rates documents
6. Policies
7. Circulars
8. Notices
9. Delete document with reason

### Notification Screens

1. Notifications list
2. Notification detail
3. Due tomorrow notifications
4. Overdue notifications
5. Reservation ready notifications
6. Fine notifications
7. Clearance update notifications
8. Email settings test
9. WhatsApp placeholder settings

### Administration Screens

1. Settings
2. Fine and issue settings
3. Email settings
4. WhatsApp placeholder settings
5. Category settings
6. Department settings
7. Literature settings
8. Report header settings
9. Backup settings
10. Backup list
11. Create backup
12. Restore backup
13. Activity logs
14. Global smart search results

## Role Model

Final roles:

1. Super Admin
2. Admin
3. Librarian
4. Assistant Librarian
5. Student
6. Permanent Faculty
7. Visiting Faculty
8. Permanent Staff
9. Temporary Staff
10. Auditor
11. Read Only Viewer

Each role will be mapped to permissions. Screens and actions will not rely on role names alone. Role names provide defaults, while permissions enforce exact access.

## Folder Structure

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

## Phase 0 Exit Criteria

Phase 0 is complete when:

1. Module list is frozen.
2. Screen list is frozen.
3. Database entity list is frozen.
4. ERD explanation is documented.
5. Folder structure exists.
6. README exists.
7. Development roadmap exists.
8. Three-student work division exists.
9. No full module code has been written.

