# Phase 7 Manual Test Checklist

Run after applying migrations and seed data.

## Commands

```powershell
cd d:\Project\Library\kicsitLibrarySystem
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

## Reports

1. Open `Reports`.
2. Run Full Library Catalog.
3. Run Issue Receive History.
4. Run Overdue Report.
5. Run Fine Report.
6. Run Student Clearance Report.
7. Run Reservation Report.
8. Run Lost and Damaged Books Report.
9. Use search and status filters where applicable.
10. Export each report as PDF.
11. Export each report as Excel.
12. Export each report as CSV.

## Import

1. Open `Imports`.
2. Upload a valid students CSV with `registration_number,name`.
3. Confirm batch status becomes `Imported`.
4. Upload a CSV missing required fields.
5. Confirm failed rows are recorded.
6. Download the failed import error CSV.
7. Import employees with `name,employee_type`.
8. Import books with `title`.

## Global Smart Search

1. Open `Smart Search`.
2. Search by book title.
3. Search by accession number.
4. Search by ISBN.
5. Search by student registration number.
6. Search by admission number.
7. Search by P Number.
8. Search by CNIC.
9. Search by phone.
10. Search by category name.
11. Confirm links open the related record pages.

