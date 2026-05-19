# Database Planning

Project: KICSIT Library Management System  
Database: MySQL  
ORM: SQLAlchemy  
Migration tool: Alembic

## Database Design Principles

1. Use normalized relational tables because the system depends on strong relationships between books, copies, students, employees, issues, receives, reservations, fines, audits, and documents.
2. Use integer primary keys for internal joins.
3. Use business identifiers with unique constraints where required, such as accession number, registration number, admission number, P Number, CNIC, username, and email.
4. Keep book master data separate from physical accession copies.
5. Keep issue and receive records separate so history is never lost.
6. Use soft delete for important operational records.
7. Store uploaded file metadata in database and physical files in controlled local storage.
8. Record sensitive actions in activity logs.
9. Use Alembic migrations for every schema change after Phase 1.

## Final Database Entity List

1. `users`
2. `roles`
3. `permissions`
4. `userroles`
5. `rolepermissions`
6. `students`
7. `employees`
8. `authors`
9. `publishers`
10. `categories`
11. `departmentcategories`
12. `literaturecategories`
13. `bookmasters`
14. `bookauthors`
15. `bookcopies`
16. `issuerecords`
17. `receiverecords`
18. `reservations`
19. `fines`
20. `lostbooks`
21. `damagedbooks`
22. `notifications`
23. `visitrecords`
24. `auditrecords`
25. `inventoryitems`
26. `newarrivals`
27. `documents`
28. `importbatches`
29. `importerrors`
30. `settings`
31. `activitylogs`
32. `backups`

## Entity Planning

### `users`

Stores login accounts for administrators, librarians, assistant librarians, students, faculty, staff, auditors, and viewers.

Important fields:

- id
- username
- email
- password_hash
- full_name
- is_active
- last_login_at
- failed_login_count
- locked_until
- created_at
- updated_at

### `roles`

Stores system roles.

Important fields:

- id
- name
- description
- is_system_role
- created_at
- updated_at

### `permissions`

Stores granular permissions for pages and actions.

Important fields:

- id
- code
- name
- module
- description

### `userroles`

Many-to-many bridge between users and roles.

Important fields:

- id
- user_id
- role_id

### `rolepermissions`

Many-to-many bridge between roles and permissions.

Important fields:

- id
- role_id
- permission_id

### `students`

Stores library consumer records for students.

Important fields:

- id
- registration_number
- admission_number
- roll_number
- name
- father_name
- department
- program
- semester
- session
- batch
- phone
- email
- status
- clearance_status
- clearance_date
- clearance_remarks
- page_number
- register_number
- photo_document_id
- is_active
- created_at
- updated_at

### `employees`

Stores faculty and staff consumers.

Important fields:

- id
- p_number
- cnic
- name
- department
- designation
- phone
- email
- employee_type
- is_active
- joining_date
- leaving_date
- remarks
- created_at
- updated_at

### `authors`

Stores author records.

Important fields:

- id
- name
- description
- created_at
- updated_at

### `publishers`

Stores publisher records.

Important fields:

- id
- name
- city
- country
- contact
- created_at
- updated_at

### `categories`

Stores general categories such as Programming, Artificial Intelligence, Networking, and Database.

Important fields:

- id
- name
- code
- description
- is_active

### `departmentcategories`

Stores department categories such as CS and CE.

Important fields:

- id
- name
- code
- description
- is_active

### `literaturecategories`

Stores literature categories such as Urdu, English, History, and Islam.

Important fields:

- id
- name
- code
- description
- is_active

### `bookmasters`

Stores bibliographic and purchasing master data for a title.

Important fields:

- id
- title
- unique_title
- subtitle
- publisher_id
- isbn
- issn
- source
- department_category_id
- literature_category_id
- category_id
- edition
- publication_place
- publication_year
- copyright_year
- series
- language
- format
- binding_type
- physical_description
- keywords
- notes
- contents
- price
- quantity
- book_location
- rack
- shelf
- hall
- description
- book_image_document_id
- bill_number
- store_name
- purchase_date
- supplier
- invoice_document_id
- created_by_user_id
- updated_by_user_id
- created_at
- updated_at

### `bookauthors`

Many-to-many bridge between book masters and authors.

Important fields:

- id
- book_master_id
- author_id
- author_order

### `bookcopies`

Stores physical accession copies.

Important fields:

- id
- accession_number
- book_master_id
- copy_number
- barcode_value
- rack
- shelf
- location
- physical_condition
- status
- current_holder_type
- current_student_id
- current_employee_id
- last_issue_date
- last_receive_date
- deleted_reason
- deleted_by_user_id
- deleted_at
- created_at
- updated_at

### `issuerecords`

Stores issue transactions.

Important fields:

- id
- issue_number
- book_copy_id
- book_master_id
- consumer_type
- student_id
- employee_id
- issue_date
- due_date
- status
- remarks
- issued_by_user_id
- created_at
- closed_at

### `receiverecords`

Stores return transactions.

Important fields:

- id
- receive_number
- issue_record_id
- book_copy_id
- receive_date
- book_condition
- overdue_days
- calculated_fine_amount
- remarks
- received_by_user_id
- created_at

### `reservations`

Stores queue-based reservations.

Important fields:

- id
- reservation_number
- consumer_type
- student_id
- employee_id
- book_master_id
- book_copy_id
- reservation_date
- expiry_date
- queue_position
- status
- remarks
- cancelled_reason
- created_by_user_id
- updated_at

### `fines`

Stores overdue, lost, damaged, and manual fine records.

Important fields:

- id
- fine_number
- issue_record_id
- receive_record_id
- book_copy_id
- consumer_type
- student_id
- employee_id
- fine_type
- fine_amount
- paid_amount
- remaining_amount
- payment_status
- payment_date
- collected_by_user_id
- waived_by_user_id
- waiver_reason
- remarks
- created_at

### `lostbooks`

Stores lost book cases.

Important fields:

- id
- lost_date
- issue_record_id
- book_copy_id
- consumer_type
- student_id
- employee_id
- fine_amount
- payment_status
- remarks
- resolved_status
- resolved_at

### `damagedbooks`

Stores damaged book cases.

Important fields:

- id
- damage_date
- issue_record_id
- book_copy_id
- consumer_type
- student_id
- employee_id
- damage_level
- repair_cost
- remarks
- resolved_status
- resolved_at

### `notifications`

Stores email and future WhatsApp notification records.

Important fields:

- id
- consumer_type
- student_id
- employee_id
- notification_type
- channel
- subject
- message
- status
- sent_at
- failure_reason
- created_at

### `visitrecords`

Stores visit and accreditation records.

Important fields:

- id
- visit_date
- organization
- visit_type
- team_members
- department
- purpose
- observations
- suggestions
- findings
- action_taken
- follow_up_date
- status
- created_by_user_id
- created_at

### `auditrecords`

Stores audit observations, suggestions, findings, and actions.

Important fields:

- id
- audit_date
- audit_type
- financial_year
- observations
- suggestions
- findings
- recommendations
- action_required
- action_taken
- responsible_person
- status
- created_by_user_id
- created_at

### `inventoryitems`

Stores furniture and equipment inventory.

Important fields:

- id
- item_name
- item_type
- quantity
- available_quantity
- damaged_quantity
- condition
- location
- purchase_date
- price
- supplier
- remarks
- created_at
- updated_at

### `newarrivals`

Stores new arrival books, journals, magazines, newspapers, reports, project reports, and thesis records.

Important fields:

- id
- arrival_number
- material_type
- title
- category_id
- department_category_id
- quantity
- purchase_year
- purchase_month
- supplier
- invoice_number
- invoice_document_id
- received_date
- remarks
- created_at

### `documents`

Stores uploaded file metadata.

Important fields:

- id
- title
- document_type
- version
- original_filename
- stored_filename
- storage_key
- mime_type
- file_size
- uploaded_by_user_id
- upload_date
- description
- category
- is_active
- remarks

### `importbatches`

Stores import attempts.

Important fields:

- id
- import_type
- source_filename
- total_rows
- success_rows
- failed_rows
- status
- created_by_user_id
- created_at

### `importerrors`

Stores failed rows and validation messages from imports.

Important fields:

- id
- import_batch_id
- row_number
- row_data_json
- error_message

### `settings`

Stores configurable application settings.

Important fields:

- id
- key
- value
- value_type
- group_name
- updated_by_user_id
- updated_at

### `activitylogs`

Stores sensitive action logs.

Important fields:

- id
- user_id
- action
- module
- entity_name
- entity_id
- description
- ip_address
- user_agent
- created_at

### `backups`

Stores backup metadata.

Important fields:

- id
- backup_name
- backup_type
- file_name
- file_size
- status
- created_by_user_id
- created_at
- restore_performed_at
- restore_performed_by_user_id

## ERD Explanation in Text

### Identity and Access Area

`users`, `roles`, `permissions`, `userroles`, and `rolepermissions` form the access-control area. One user can have many roles through `userroles`. One role can have many permissions through `rolepermissions`. Permission codes will control both route access and button visibility.

### Consumer Area

`students` and `employees` are separate because their identifiers, statuses, and clearance rules are different. Issue, reservation, fine, lost, damaged, and notification records use `consumer_type` plus either `student_id` or `employee_id`. This keeps student-specific fields such as registration number, admission number, page number, register number, and clearance status separate from employee fields such as P Number, CNIC, designation, and employee type.

### Catalog Area

`bookmasters` stores title-level data, while `bookcopies` stores physical accession-level data. One book master has many book copies. One book master can have many authors through `bookauthors`. A book master can connect to one publisher, one general category, one department category, and one literature category.

This separation solves the EMIS status inconsistency problem because each physical copy has its own accession number and status.

### Circulation Area

`issuerecords` stores issue transactions. One book copy can have many issue records over time, but only one active issue at a time. `receiverecords` closes an issue record. One issue record can have one receive record.

The issue workflow updates `bookcopies.status` to Issued. The return workflow creates a receive record and then updates copy status to Available, Damaged, or Lost depending on condition.

### Fine Area

`fines` can be linked to issue and receive records. Overdue fine is calculated during return. Lost and damaged cases can also create related fine records. Waivers require permission and waiver reason.

### Reservation Area

`reservations` belongs to a consumer and a book master. It may optionally target a specific copy. Waiting reservations are ordered by queue position and reservation date. When a copy is returned, the first waiting reservation becomes Ready for pickup and a notification is created.

### Lost and Damaged Area

`lostbooks` and `damagedbooks` preserve incident history. They link to issue records and book copies so the system can block clearance and future issues when unresolved cases exist.

### Document, Audit, and Accreditation Area

`documents` stores metadata for uploaded files such as SOP files, National Library Rates, policies, circulars, invoices, audit evidence, and visit evidence. Audit and visit records can attach documents through future linking tables if multiple attachments per record are required. In Phase 0 planning, document metadata is centralized to keep uploads secure and searchable.

### Inventory and Arrival Area

`inventoryitems` handles furniture and equipment. `newarrivals` handles books, journals, magazines, newspapers, reports, project reports, and thesis arrivals. New arrival records may reference document invoices.

### Import, Reporting, and Administration Area

`importbatches` and `importerrors` track bulk imports. `settings` stores application configuration. `activitylogs` records sensitive actions. `backups` tracks database backup and restore metadata.

## Important Relationships

1. One `bookmasters` record has many `bookcopies`.
2. One `bookmasters` record has many `authors` through `bookauthors`.
3. One `bookcopies` record has many `issuerecords`.
4. One active `issuerecords` record belongs to one `bookcopies` record.
5. One `issuerecords` record can have one `receiverecords` record.
6. One `issuerecords` record can have one or more related `fines` depending on fine type.
7. One `students` record can have many `issuerecords`, `reservations`, `fines`, `notifications`, `lostbooks`, and `damagedbooks`.
8. One `employees` record can have many `issuerecords`, `reservations`, `fines`, `notifications`, `lostbooks`, and `damagedbooks`.
9. One `reservations` record belongs to one consumer and one book master.
10. One `lostbooks` record belongs to one issue record and one book copy.
11. One `damagedbooks` record belongs to one issue record and one book copy.
12. One `documents` record belongs to one uploading user.
13. One `activitylogs` record belongs to one user when the action is authenticated.

## Planned Status Values

### Book Copy Status

- Available
- Issued
- Reserved
- Overdue
- Lost
- Damaged
- Missing
- Repairing
- Deleted

### Issue Status

- Active
- Returned
- Lost
- Damaged
- Cancelled

### Reservation Status

- Waiting
- Ready for pickup
- Completed
- Cancelled
- Expired

### Student Status

- Active
- Blocked
- Graduated
- Cleared
- Not Cleared

### Fine Payment Status

- Unpaid
- Partial
- Paid
- Waived

### Notification Status

- Pending
- Sent
- Failed

## Planned Constraints and Indexes

1. Unique username in `users`.
2. Unique email in `users` when provided.
3. Unique registration number in `students`.
4. Unique admission number in `students` when provided.
5. Unique P Number in `employees` when provided.
6. Unique CNIC in `employees` when provided.
7. Unique accession number in `bookcopies`.
8. Unique barcode value in `bookcopies` when provided.
9. Index book title in `bookmasters`.
10. Index ISBN and ISSN in `bookmasters`.
11. Index issue date and due date in `issuerecords`.
12. Index receive date in `receiverecords`.
13. Index reservation date and status in `reservations`.
14. Index payment status in `fines`.
15. Index action and created date in `activitylogs`.

## Consistency Rules

1. A book copy cannot be issued unless `bookcopies.status` is Available.
2. A book copy cannot have two active issue records.
3. A book copy cannot be deleted when an active issue exists.
4. Deleting a book copy requires a reason and uses soft delete.
5. Returning a book must close the active issue record.
6. Returning an overdue book creates a fine when calculated amount is greater than zero.
7. Fine waiver requires permission and reason.
8. Student clearance is blocked by active issues, unpaid fines, unresolved lost cases, and unresolved damaged cases.
9. Reservation queue order must be preserved.
10. Duplicate accession numbers must be rejected during manual entry and import.

## Backup Planning

Backup and restore will be implemented in a later phase. Planning rules:

1. Backup metadata is stored in `backups`.
2. Backup file generation requires admin permission.
3. Restore requires admin permission and explicit confirmation.
4. Restore action must be logged.
5. Backup files must not be publicly served from static routes.

