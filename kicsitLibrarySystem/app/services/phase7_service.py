import csv
import io
import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    BookCopy,
    BookMaster,
    Category,
    Category,
    DamagedBook,
    Employee,
    Fine,
    ImportBatch,
    ImportErrorRow,
    IssueRecord,
    LostBook,
    Publisher,
    ReceiveRecord,
    Reservation,
    Student,
    User,
)
from app.services import settings_service


@dataclass
class ReportResult:
    title: str
    headers: list[str]
    rows: list[list]
    filters: dict


REPORT_TITLES = {
    "catalog": "Full Library Catalog",
    "issues": "Issue Receive History",
    "overdue": "Overdue Report",
    "fines": "Fine Report",
    "clearance": "Student Clearance Report",
    "reservations": "Reservation Report",
    "lost-damaged": "Lost and Damaged Books Report",
}


def clean(value):
    if value is None:
        return ""
    return str(value)


def build_report(db: Session, report_type: str, q: str | None = None, status_filter: str | None = None) -> ReportResult:
    q = (q or "").strip()
    filters = {"q": q, "status": status_filter or ""}
    if report_type == "catalog":
        statement = select(BookMaster).options(selectinload(BookMaster.copies), selectinload(BookMaster.publisher), selectinload(BookMaster.category)).where(BookMaster.is_deleted == False)  # noqa: E712
        if q:
            like = f"%{q}%"
            statement = statement.where(or_(BookMaster.title.ilike(like), BookMaster.isbn.ilike(like), BookMaster.issn.ilike(like)))
        rows = [[b.title, b.isbn, b.issn, b.publisher.name if b.publisher else "", b.category.name if b.category else "", len([c for c in b.copies if not c.is_deleted])] for b in db.scalars(statement).unique().all()]
        return ReportResult(REPORT_TITLES[report_type], ["Title", "ISBN", "ISSN", "Publisher", "Category", "Copies"], rows, filters)
    if report_type == "issues":
        statement = select(IssueRecord).options(selectinload(IssueRecord.book_copy), selectinload(IssueRecord.book_master), selectinload(IssueRecord.student), selectinload(IssueRecord.employee), selectinload(IssueRecord.receive_record)).order_by(IssueRecord.created_at.desc())
        if status_filter:
            statement = statement.where(IssueRecord.status == status_filter)
        rows = [[i.issue_number, i.book_copy.accession_number, i.book_master.title, i.student.name if i.student else i.employee.name, i.issue_date, i.due_date, i.status, i.receive_record.receive_date if i.receive_record else ""] for i in db.scalars(statement).unique().all()]
        return ReportResult(REPORT_TITLES[report_type], ["Issue No", "Accession", "Book", "Consumer", "Issue Date", "Due Date", "Status", "Receive Date"], rows, filters)
    if report_type == "overdue":
        today = date.today()
        fine_per_day = settings_service.get_setting_decimal(db, "circulation.fine_per_day", Decimal("10.00"))
        records = db.scalars(select(IssueRecord).options(selectinload(IssueRecord.book_copy), selectinload(IssueRecord.book_master), selectinload(IssueRecord.student), selectinload(IssueRecord.employee)).where(IssueRecord.status == "Active", IssueRecord.due_date < today)).all()
        rows = [[i.book_copy.accession_number, i.book_master.title, i.student.name if i.student else i.employee.name, i.issue_date, i.due_date, (today - i.due_date).days, Decimal((today - i.due_date).days) * fine_per_day] for i in records]
        return ReportResult(REPORT_TITLES[report_type], ["Accession", "Book", "Consumer", "Issue Date", "Due Date", "Days", "Fine"], rows, filters)
    if report_type == "fines":
        statement = select(Fine).options(selectinload(Fine.student), selectinload(Fine.employee), selectinload(Fine.book_copy)).order_by(Fine.created_at.desc())
        if status_filter:
            statement = statement.where(Fine.payment_status == status_filter)
        rows = [[f.fine_number, f.student.name if f.student else f.employee.name, f.book_copy.accession_number if f.book_copy else "", f.fine_type, f.fine_amount, f.remaining_amount, f.payment_status] for f in db.scalars(statement).all()]
        return ReportResult(REPORT_TITLES[report_type], ["Fine No", "Consumer", "Accession", "Type", "Amount", "Remaining", "Status"], rows, filters)
    if report_type == "clearance":
        statement = select(Student).order_by(Student.name)
        if status_filter:
            statement = statement.where(Student.clearance_status == status_filter)
        rows = [[s.registration_number, s.admission_number, s.name, s.department, s.status, s.clearance_status, s.clearance_date] for s in db.scalars(statement).all()]
        return ReportResult(REPORT_TITLES[report_type], ["Registration", "Admission", "Name", "Department", "Status", "Clearance", "Clearance Date"], rows, filters)
    if report_type == "reservations":
        statement = select(Reservation).options(selectinload(Reservation.student), selectinload(Reservation.employee), selectinload(Reservation.book_master)).order_by(Reservation.created_at.desc())
        if status_filter:
            statement = statement.where(Reservation.status == status_filter)
        rows = [[r.reservation_number, r.book_master.title, r.student.name if r.student else r.employee.name, r.queue_position, r.status, r.reservation_date, r.expiry_date] for r in db.scalars(statement).all()]
        return ReportResult(REPORT_TITLES[report_type], ["Reservation No", "Book", "Consumer", "Queue", "Status", "Date", "Expiry"], rows, filters)
    if report_type == "lost-damaged":
        rows = []
        for item in db.scalars(select(LostBook).options(selectinload(LostBook.book_copy), selectinload(LostBook.student), selectinload(LostBook.employee))).all():
            rows.append(["Lost", item.book_copy.accession_number, item.student.name if item.student else item.employee.name, item.lost_date, item.fine_amount, item.payment_status, item.resolved_status])
        for item in db.scalars(select(DamagedBook).options(selectinload(DamagedBook.book_copy), selectinload(DamagedBook.student), selectinload(DamagedBook.employee))).all():
            rows.append(["Damaged", item.book_copy.accession_number, item.student.name if item.student else item.employee.name, item.damage_date, item.repair_cost, "", item.resolved_status])
        return ReportResult(REPORT_TITLES[report_type], ["Type", "Accession", "Consumer", "Date", "Amount", "Payment", "Resolved"], rows, filters)
    raise ValueError("Invalid report type.")


def report_csv(result: ReportResult) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(result.headers)
    writer.writerows(result.rows)
    return output.getvalue().encode("utf-8")


def report_excel(result: ReportResult) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Report"
    ws.append([result.title])
    ws.append(result.headers)
    for row in result.rows:
        ws.append([clean(v) for v in row])
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def report_pdf(result: ReportResult) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 45
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(40, y, "KICSIT Library Management System")
    y -= 18
    pdf.drawString(40, y, result.title)
    y -= 22
    pdf.setFont("Helvetica", 8)
    pdf.drawString(40, y, f"Generated: {date.today().isoformat()} | Total: {len(result.rows)}")
    y -= 20
    for row in result.rows:
        pdf.drawString(40, y, " | ".join(clean(v)[:24] for v in row[:6]))
        y -= 14
        if y < 55:
            pdf.showPage()
            y = height - 45
            pdf.setFont("Helvetica", 8)
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def parse_csv_upload(file_bytes: bytes) -> list[dict]:
    text = file_bytes.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def import_preview(db: Session, import_type: str, filename: str, rows: list[dict], current_user: User) -> ImportBatch:
    batch = ImportBatch(import_type=import_type, source_filename=filename, total_rows=len(rows), success_rows=0, failed_rows=0, status="Previewed", created_by_user_id=current_user.id)
    db.add(batch)
    db.flush()
    failed = 0
    for idx, row in enumerate(rows, start=2):
        error = validate_import_row(db, import_type, row)
        if error:
            failed += 1
            db.add(ImportErrorRow(import_batch_id=batch.id, row_number=idx, row_data_json=json.dumps(row), error_message=error))
    batch.failed_rows = failed
    batch.success_rows = len(rows) - failed
    db.commit()
    db.refresh(batch)
    return batch


def validate_import_row(db: Session, import_type: str, row: dict) -> str | None:
    if import_type == "students":
        if not row.get("registration_number") or not row.get("name"):
            return "registration_number and name are required."
        if db.scalar(select(Student).where(Student.registration_number == row.get("registration_number"))):
            return "Duplicate registration number."
    elif import_type == "employees":
        if not row.get("name") or not row.get("employee_type"):
            return "name and employee_type are required."
    elif import_type == "books":
        if not row.get("title"):
            return "title is required."
    else:
        return "Unsupported import type."
    return None


def commit_import(db: Session, batch: ImportBatch, rows: list[dict]) -> None:
    if batch.failed_rows:
        raise ValueError("Cannot commit import while failed rows exist.")
    if batch.import_type == "students":
        for row in rows:
            db.add(Student(registration_number=row["registration_number"], admission_number=row.get("admission_number") or None, name=row["name"], department=row.get("department") or None, phone=row.get("phone") or None, status=row.get("status") or "Active", clearance_status=row.get("clearance_status") or "Not Cleared", is_active=True))
    elif batch.import_type == "employees":
        for row in rows:
            db.add(Employee(p_number=row.get("p_number") or None, cnic=row.get("cnic") or None, name=row["name"], department=row.get("department") or None, designation=row.get("designation") or None, phone=row.get("phone") or None, employee_type=row["employee_type"], is_active=True))
    elif batch.import_type == "books":
        for row in rows:
            db.add(BookMaster(title=row["title"], isbn=row.get("isbn") or None, issn=row.get("issn") or None, source=row.get("source") or None, book_location=row.get("book_location") or None, quantity=0))
    batch.status = "Imported"
    db.add(batch)
    db.commit()


def import_error_csv(batch: ImportBatch) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["row_number", "error_message", "row_data"])
    for error in batch.errors:
        writer.writerow([error.row_number, error.error_message, error.row_data_json])
    return output.getvalue().encode("utf-8")


def global_search(db: Session, q: str) -> dict[str, list]:
    q = q.strip()
    if not q:
        return {"books": [], "copies": [], "students": [], "employees": [], "categories": []}
    like = f"%{q}%"
    return {
        "books": db.scalars(select(BookMaster).where(or_(BookMaster.title.ilike(like), BookMaster.isbn.ilike(like), BookMaster.issn.ilike(like))).limit(20)).all(),
        "copies": db.scalars(select(BookCopy).options(selectinload(BookCopy.book_master)).where(BookCopy.accession_number.ilike(like)).limit(20)).all(),
        "students": db.scalars(select(Student).where(or_(Student.registration_number.ilike(like), Student.admission_number.ilike(like), Student.name.ilike(like), Student.phone.ilike(like))).limit(20)).all(),
        "employees": db.scalars(select(Employee).where(or_(Employee.p_number.ilike(like), Employee.cnic.ilike(like), Employee.name.ilike(like), Employee.phone.ilike(like))).limit(20)).all(),
        "categories": db.scalars(select(Category).where(Category.name.ilike(like)).limit(20)).all(),
    }
