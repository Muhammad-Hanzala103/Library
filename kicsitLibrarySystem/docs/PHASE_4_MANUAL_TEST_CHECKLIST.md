# Phase 4 Manual Test Checklist

Run after applying migrations and seed data.

## Commands

```powershell
cd d:\Project\Library\kicsitLibrarySystem
.\.venv\Scripts\Activate.ps1
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Login with `superadmin`, `librarian`, or `assistant`.

## Precondition Data

1. Create at least one student with clearance status `Not Cleared`.
2. Create at least one employee.
3. Create at least one book and one accession copy with status `Available`.

## Issue Workflow

1. Open `Issue Return`.
2. Search student by registration number.
3. Search book by accession number.
4. Confirm consumer details, active issues, unpaid fines, and book status are shown.
5. Submit issue date and due date.
6. Confirm issue slip opens.
7. Confirm accession copy status becomes `Issued`.
8. Try issuing same accession number again and confirm it is blocked.

## Issue Validation

1. Change student clearance status to `Cleared`.
2. Try issuing a book to that student and confirm clearance block.
3. Create enough active issues to reach issue limit and confirm issue limit block.
4. Create an unpaid fine for a consumer through overdue return and confirm pending fine blocks future issue.

## Return Workflow

1. Open `Return Book`.
2. Search issued accession number.
3. Confirm active issue appears.
4. Return with receive date after due date.
5. Confirm return slip opens.
6. Confirm overdue days and fine amount are calculated.
7. Confirm accession copy status becomes `Available` for normal return.

## Fine Calculation

1. Issue a book with due date two days before receive date.
2. Return it.
3. Confirm overdue days equals `2`.
4. Confirm fine amount equals overdue days multiplied by default fine per day.
5. Return once with fine status `Paid` and confirm fine status is paid.
6. Return once with fine status `Unpaid` and confirm future issue is blocked for that consumer.

## History and Slips

1. Open `Issue History`.
2. Search by issue number.
3. Search by accession number.
4. Search by title.
5. Search by consumer name.
6. Open issue slip from history.
7. Open return slip from history.
8. Use the print button on both slips.

## Activity Logs

1. Confirm `ISSUE_BOOK` appears after issuing.
2. Confirm `RETURN_BOOK` appears after returning.

