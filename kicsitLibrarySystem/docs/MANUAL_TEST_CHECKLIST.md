# KICSIT Library Management System - Manual Test Checklist

This manual test manual provides rigorous, step-by-step test cases to verify the entire system lifecycle, security boundaries, dynamic settings updates, and disaster recovery processes.

---

## 1. Authentication & Security Boundaries

### TC-1.1: Standard JWT Login Verification
1. Navigate to the login page (`http://localhost:8000/login`).
2. Input valid credentials: Username `superadmin`, Password `ChangeMe@123`. Click **Login**.
3. **Expected Result**: Successfully redirected to the main dashboard. The browser holds the dynamic HTTP-only session cookie containing the JWT payload.

### TC-1.2: Invalid Login Prevention
1. Navigate to the login page.
2. Input username `superadmin` but type an incorrect password. Click **Login**.
3. **Expected Result**: Remains on login page. Renders standard "Invalid username or password" validation banner. Access is blocked.

### TC-1.3: Permission Boundary (403 Forbidden Guard)
1. Log in as user `assistant` (Password: `ChangeMe@123`).
2. Direct your browser URL manually to the settings endpoint: `http://localhost:8000/settings`.
3. **Expected Result**: Access is intercepted by the router security decorator. The server throws a secure HTTP 403 Forbidden page, explaining the role lacks `settings.manage` credentials.

---

## 2. Dynamic Cataloging & Inventory Tracking

### TC-2.1: Add New Book to Catalog
1. Log in as a `librarian`. Navigate to **Library Catalog** and click **Add New Book**.
2. Fill out details:
   * Title: *Introduction to Algorithms*
   * Authors: *Thomas H. Cormen*
   * ISBN: *9780262033848*
   * Category: *Computer Science*
3. Click **Save Book**.
4. **Expected Result**: The record is saved in the `books` table. A success message is displayed, and the catalog table increments by 1.

### TC-2.2: Add Physical Copy Inventory (Barcode Scans)
1. Search for *Introduction to Algorithms* in the catalog list and click **Manage Copies**.
2. Click **Register Copy**.
3. Fill out the unique copy Barcode (e.g., `ALG-COPY-01`), set condition to `New`, and set status to `Available`.
4. Click **Save Copy**.
5. **Expected Result**: A row is added in `book_copies` pointing to the book's primary key. Status displays as `Available` with a clean green badge.

---

## 3. Student & Employee Management

### TC-3.1: Consumer Account Registration
1. Navigate to **Students** and click **Add Student**.
2. Input credentials:
   * Roll Number: *KICSIT-2022-09*
   * Full Name: *Muhammad Hanzala*
   * Email: *hanzala@kicsit.edu.pk*
   * Max Borrowing Capacity: *5*
3. Click **Register Student**.
4. **Expected Result**: User consumer record created. Profile displays under active student list.

---

## 4. Dynamic Circulation & Fines Engine

### TC-4.1: Book Issue (Borrow Limit Check)
1. Navigate to **Issue Return** and select **Issue Book**.
2. Select Student *Muhammad Hanzala* and scan copy barcode `ALG-COPY-01`.
3. Click **Process Checkout**.
4. **Expected Result**: An issue record is written to `issues`. The copy status transitions from `Available` to `Issued`. The student's active borrow count increments.

### TC-4.2: Borrow Capacity Validation
1. Set the global **Student Borrowing Limit** to `1` in **System Settings** (Admin console).
2. Attempt to issue a second copy (e.g., barcode `CS-COPY-02`) to student *Muhammad Hanzala*.
3. Click **Process Checkout**.
4. **Expected Result**: The checkout service blocks the transaction, rendering a validation warning: *"Student has reached their dynamic borrowing limit of 1 book copy simultaneously."*

### TC-4.3: Return & Overdue Fine Accrual
1. Set **Daily Fine Amount (PKR)** to `50.00` in **System Settings**.
2. Locate the active issue of *Muhammad Hanzala* in the issue tracker.
3. Manually adjust the database issue record's due date to 3 days in the past (to simulate overdue).
4. Return the copy via the **Return Book** action in the UI.
5. **Expected Result**: The copy returns to `Available` status. The system dynamically computes the penalty: $3\text{ days} \times 50.00\text{ PKR} = 150.00\text{ PKR}$. A pending balance of 150.00 PKR is automatically registered under **Unpaid Fines**.

---

## 5. System Settings Management

### TC-5.1: Dynamic Settings Update
1. Log in as `admin`. Navigate to **System Settings**.
2. Change **Default Issue Duration (Days)** from `14` to `7`.
3. Click **Save Settings Configurations**.
4. **Expected Result**: Displays success banner: *"Settings updated successfully."*
5. Initiate a new checkout sequence. Verify that the calculated return due date is exactly 7 days from today instead of 14, proving dynamic configuration retrieval is active.

---

## 6. Disaster Recovery & Backups

### TC-6.1: Snapshot Generation
1. Log in as `superadmin`. Navigate to **Backup & Restore**.
2. Click the **⚡ Create Instant Backup** button.
3. **Expected Result**: A green success alert appears: *"Backup created successfully."* A new `.sql` file is written to the backup folder and logged in the backups history table with size, status `Success`, and creator `@superadmin`.

### TC-6.2: Double-Confirmation Recovery Guardrail
1. Locate your target backup row in the backups ledger table.
2. Click the **🔄 Restore** button.
3. **Expected Result (Phase A)**: A browser window confirmation prompt appears asking to verify the operation. Click **Cancel**. The restoration aborts cleanly.
4. Click **🔄 Restore** again. Click **OK** on the first prompt.
5. **Expected Result (Phase B)**: A text prompt appears asking to type the authorized code phrase.
6. Type an incorrect phrase (e.g., `restore`). Click **OK**.
7. **Expected Result (Phase C)**: Restoration aborts; system safety is maintained.
8. Click **🔄 Restore** once more, click **OK**, and type exactly **`CONFIRM RESTORE`** (all caps). Click **OK**.
9. **Expected Result (Phase D)**: The backend triggers a subprocess command execution of `mysql.exe`, successfully restores the database, logs the event to audit records, and displays: *"Database restored successfully."*
