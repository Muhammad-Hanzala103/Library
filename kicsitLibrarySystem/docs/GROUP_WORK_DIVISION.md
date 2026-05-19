# Group Work Division for Three Students

Project: KICSIT Library Management System  
Documentation student name: Muhammad Hanzala

This division keeps ownership clear while allowing the three students to work in parallel without mixing responsibilities.

## Student 1: Backend, Security, and Database Lead

Primary responsibility:

Own the FastAPI backend foundation, MySQL database design, SQLAlchemy models, Alembic migrations, authentication, authorization, and security-sensitive services.

Modules:

1. FastAPI app setup.
2. Configuration and environment handling.
3. MySQL connection.
4. SQLAlchemy base and models.
5. Alembic migrations.
6. Authentication.
7. JWT handling.
8. Password hashing.
9. Roles and permissions.
10. Activity logs.
11. Settings backend.
12. Backup and restore backend.

Database ownership:

1. `users`
2. `roles`
3. `permissions`
4. `userroles`
5. `rolepermissions`
6. `settings`
7. `activitylogs`
8. `backups`

Quality responsibilities:

1. Enforce server-side validation.
2. Prevent duplicate active issues at database and service level.
3. Implement access checks on protected routes.
4. Review upload and backup security.
5. Write automated tests for authentication and permissions.

## Student 2: Library Operations and Consumer Lead

Primary responsibility:

Own all daily library workflows used by librarian and assistant librarian staff.

Modules:

1. Student management.
2. Employee management.
3. Author management.
4. Publisher management.
5. Category management.
6. Book master management.
7. Book copy and accession management.
8. Catalog search.
9. Issue book.
10. Return book.
11. Issue receive history.
12. Reservations.
13. Overdue.
14. Fines.
15. Lost books.
16. Damaged books.
17. Student clearance.
18. Book history.
19. Book status consistency checker.

Database ownership:

1. `students`
2. `employees`
3. `authors`
4. `publishers`
5. `categories`
6. `departmentcategories`
7. `literaturecategories`
8. `bookmasters`
9. `bookauthors`
10. `bookcopies`
11. `issuerecords`
12. `receiverecords`
13. `reservations`
14. `fines`
15. `lostbooks`
16. `damagedbooks`

Quality responsibilities:

1. Validate accession number uniqueness.
2. Ensure issue and return status consistency.
3. Enforce clearance block rules.
4. Implement fine calculation accurately.
5. Write tests for issue, return, fine, reservation, and clearance workflows.

## Student 3: UI, Reports, Documents, Audit, and Deployment Lead

Primary responsibility:

Own professional ERP UI design, reports, import export, document management, accreditation modules, inventory, notifications UI, and deployment documentation.

Modules:

1. Base layout.
2. Sidebar navigation.
3. Dashboard cards and charts.
4. Searchable tables.
5. Report screens.
6. PDF, Excel, and CSV export UI.
7. Import templates and import preview UI.
8. SOP documents.
9. National Library Rates documents.
10. Audit records.
11. Visit records.
12. Furniture and equipment inventory.
13. New arrivals.
14. Journals and magazines.
15. Notifications screens.
16. Final user documentation.
17. Presentation points.
18. Viva questions and answers.

Database ownership:

1. `notifications`
2. `visitrecords`
3. `auditrecords`
4. `inventoryitems`
5. `newarrivals`
6. `documents`
7. `importbatches`
8. `importerrors`

Quality responsibilities:

1. Keep UI professional and university-appropriate.
2. Avoid fake buttons.
3. Verify report headers and filters.
4. Verify file upload screens show clear validation errors.
5. Prepare manual testing checklist and deployment guide.

## Shared Responsibilities

1. Follow the folder structure.
2. Use meaningful branch or task names if version control is used.
3. Review each other's database changes before migration generation.
4. Keep business logic out of templates.
5. Keep route handlers thin.
6. Keep services testable.
7. Keep documentation updated at the end of every phase.
8. Run tests before final submission.
9. Use MySQL only for the final database.
10. Maintain a consistent professional UI style.

## Suggested Coordination Plan

1. Student 1 completes Phase 1 and Phase 2 foundation first.
2. Student 2 starts catalog and circulation once core models and auth are ready.
3. Student 3 starts base UI style and documentation during Phase 1, then connects UI to real routes as modules are completed.
4. All students test Phase 5 together because issue, return, fine, reservation, and clearance rules are business-critical.
5. All students participate in Phase 9 final testing and viva preparation.

