# Phase 6 Manual Test Checklist

Run after Phase 5 migrations are applied.

## Commands

```powershell
cd d:\Project\Library\kicsitLibrarySystem
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

## Student Clearance

1. Open `Student Clearance`.
2. Search student by registration number.
3. Confirm issue history appears.
4. Confirm return history appears.
5. Confirm overdue history appears.
6. Confirm unpaid fines appear.
7. Confirm lost and damaged cases appear.
8. Try clearing a student with an active issue and confirm it is blocked.
9. Try clearing a student with unpaid fine and confirm it is blocked.
10. Resolve blockers, enter clearance remarks, and clear student.
11. Confirm student status becomes `Cleared`.
12. Download clearance PDF.

## Book History

1. Open `Book History`.
2. Search by accession number.
3. Confirm current book status appears.
4. Confirm issued count appears.
5. Confirm returned count appears.
6. Select a date when the book was issued.
7. Confirm system shows whether the book was in library on that date.
8. Confirm issue, receive, reservation, fine, lost, and damaged history sections appear.

## Status Consistency Checker

1. Open `Status Checker`.
2. Create a mismatch manually in database if needed, such as copy status `Available` with active issue.
3. Confirm mismatch appears.
4. Enter correction reason.
5. Correct status.
6. Confirm mismatch is removed.
7. Confirm activity log `STATUS_CORRECTED` appears.

