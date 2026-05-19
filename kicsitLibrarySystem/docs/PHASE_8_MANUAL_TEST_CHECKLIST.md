# Phase 8 Manual Test Checklist

## Database and Startup

1. Run `alembic upgrade head` and confirm these tables exist in MySQL Workbench:
   - `documents`
   - `visitrecords`
   - `auditrecords`
   - `inventoryitems`
   - `newarrivals`
2. Start the app with `uvicorn app.main:app --reload`.
3. Login as Librarian or Super Admin.

## Documents

1. Open `/documents`.
2. Upload a Library SOP PDF with version `1.0`.
3. Upload a National Library Rates file with version `1.0`.
4. Upload Audit evidence and Visit evidence files.
5. Search by title, file name, category, and document type.
6. Download each uploaded document and confirm it opens.
7. Try uploading an `.exe` or `.bat` file and confirm the system rejects it.
8. Try uploading a file larger than the configured size and confirm it is rejected.

## Visit Records

1. Open `/visits`.
2. Add HEC, PEC, NCEAC, and QEC visit records.
3. Attach a Visit evidence document.
4. Search by organization, visit type, department, and status.
5. Confirm the attachment download link works.
6. Confirm `VISIT_ADDED` appears in activity logs.

## Audit Records

1. Open `/audits`.
2. Add an internal audit record with observations, findings, recommendations, and action required.
3. Attach an Audit evidence document.
4. Search by audit type, financial year, responsible person, and status.
5. Confirm `AUDIT_ADDED` appears in activity logs.

## Inventory

1. Open `/inventory`.
2. Add furniture items such as Chair, Table, Rack, and Cupboard.
3. Add equipment items such as Computer, Printer, Scanner, UPS, and Battery.
4. Confirm the system blocks negative quantities.
5. Confirm the system blocks available plus damaged quantity greater than total quantity.
6. Search by item name, type, location, and condition.
7. Confirm `INVENTORY_ADDED` appears in activity logs.

## New Arrivals, Journals, and Magazines

1. Open `/arrivals`.
2. Add a Book arrival with category and department.
3. Add Journal and Magazine records.
4. Attach an invoice document where available.
5. Try duplicate arrival number and confirm it is blocked.
6. Search by arrival number, title, material type, and invoice number.
7. Confirm `ARRIVAL_ADDED` appears in activity logs.

## Reports

1. Open `/phase8-reports`.
2. Run Visit Records report.
3. Run Audit Records report.
4. Run Furniture and Equipment report.
5. Run New Arrivals, Journals and Magazines report.
6. Run SOP and National Library Rates Documents report.
7. Export each report as PDF, Excel, and CSV.
8. Confirm exported files include header rows and database records.
9. Confirm `PHASE8_REPORT_EXPORTED` appears in activity logs.
