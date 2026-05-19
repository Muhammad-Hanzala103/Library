# Phase 3 Manual Test Checklist

Run after applying migrations and seed data.

## Commands

```powershell
cd d:\Project\Library\kicsitLibrarySystem
.\.venv\Scripts\Activate.ps1
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Login with `superadmin` or `librarian`.

## Students CRUD

1. Open `Students`.
2. Click `Add Student`.
3. Create a student with registration number, admission number, name, department, phone, page number, and register number.
4. Confirm the student profile opens.
5. Edit the student.
6. Change student status to `Blocked`.
7. Save and confirm profile shows the new status.
8. Change clearance status to `Cleared`, set clearance date and remarks.
9. Save and confirm clearance fields appear on the profile.
10. Try creating another student with the same registration number and confirm the database blocks it.

## Student Search

1. Search by registration number.
2. Search by admission number.
3. Search by name.
4. Search by phone.
5. Filter by student status.

## Employees CRUD

1. Open `Employees`.
2. Create a Permanent Faculty record with a P Number.
3. Create a Visiting Faculty record with a CNIC.
4. Create a Permanent Staff record with a P Number.
5. Create a Temporary Staff record with a CNIC.
6. Confirm each profile opens.
7. Edit employee department, designation, phone, and active status.
8. Confirm updated values appear on the profile.

## Employee Validation

1. Try Permanent Faculty without P Number and confirm validation blocks it.
2. Try Temporary Staff without CNIC and confirm validation blocks it.
3. Try duplicate P Number and confirm the database blocks it.
4. Try duplicate CNIC and confirm the database blocks it.

## Employee Search

1. Search by P Number.
2. Search by CNIC.
3. Search by name.
4. Search by phone.
5. Filter by employee type.

## Activity Logs

1. Add a student and confirm `ADD_STUDENT` appears in recent activity.
2. Edit a student and confirm `EDIT_STUDENT` appears.
3. Add an employee and confirm `ADD_EMPLOYEE` appears.
4. Edit an employee and confirm `EDIT_EMPLOYEE` appears.

