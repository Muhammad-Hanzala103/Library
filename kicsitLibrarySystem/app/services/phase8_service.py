import csv
import io
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.models import AuditRecord, Document, InventoryItem, NewArrival, User, VisitRecord


UPLOAD_DIR = Path("app/uploads/documents")
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".csv", ".jpg", ".jpeg", ".png"}
BLOCKED_EXTENSIONS = {".exe", ".bat", ".cmd", ".ps1", ".sh", ".js", ".vbs", ".msi", ".dll", ".com", ".scr"}

VISIT_ORGANIZATIONS = ["HEC", "PEC", "NCEAC", "QEC", "Internal Visit", "Other"]
DOCUMENT_TYPES = [
    "Library SOP",
    "National Library Rates",
    "Policies",
    "Circulars",
    "Notices",
    "Audit evidence",
    "Visit evidence",
    "Invoices",
    "General documents",
]
INVENTORY_TYPES = ["Chair", "Table", "Rack", "Cupboard", "Computer", "Printer", "Scanner", "UPS", "Battery", "Other"]
MATERIAL_TYPES = ["Book", "Journal", "Magazine", "Newspaper", "Report", "Project Report", "Thesis"]


@dataclass
class Phase8Report:
    title: str
    headers: list[str]
    rows: list[list]


def clean(value) -> str:
    return "" if value is None else str(value)


def parse_optional_date(value: str | None):
    value = (value or "").strip()
    return date.fromisoformat(value) if value else None


def parse_optional_int(value: str | None, default: int = 0) -> int:
    value = (value or "").strip()
    return int(value) if value else default


def parse_optional_decimal(value: str | None):
    value = (value or "").strip()
    return value or None


def safe_filename(filename: str) -> str:
    base = Path(filename).name
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", Path(base).stem).strip("._") or "document"
    ext = Path(base).suffix.lower()
    return f"{stem[:80]}-{uuid4().hex}{ext}"


def validate_upload(upload: UploadFile) -> int:
    filename = upload.filename or ""
    ext = Path(filename).suffix.lower()
    if ext in BLOCKED_EXTENSIONS or ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Only PDF, DOCX, XLSX, CSV, JPG, and PNG files are allowed.")
    upload.file.seek(0, 2)
    size = upload.file.tell()
    upload.file.seek(0)
    if size <= 0:
        raise ValueError("Uploaded file is empty.")
    if size > get_settings().max_upload_size_bytes:
        raise ValueError(f"File size must be {get_settings().max_upload_size_mb} MB or less.")
    return size


def save_document_upload(
    db: Session,
    *,
    upload: UploadFile,
    title: str,
    document_type: str,
    version: str,
    current_user: User,
    description: str | None = None,
    category: str | None = None,
    remarks: str | None = None,
) -> Document:
    if not title.strip():
        raise ValueError("Document title is required.")
    if document_type not in DOCUMENT_TYPES:
        raise ValueError("Invalid document type.")
    size = validate_upload(upload)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored = safe_filename(upload.filename or "document")
    storage_key = f"documents/{stored}"
    target = UPLOAD_DIR / stored
    with target.open("wb") as buffer:
        buffer.write(upload.file.read())

    document = Document(
        title=title.strip(),
        document_type=document_type,
        version=(version or "1.0").strip() or "1.0",
        original_filename=Path(upload.filename or stored).name,
        stored_filename=stored,
        storage_key=storage_key,
        mime_type=upload.content_type,
        file_size=size,
        uploaded_by_user_id=current_user.id,
        description=(description or "").strip() or None,
        category=(category or "").strip() or None,
        remarks=(remarks or "").strip() or None,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def document_file_path(document: Document) -> Path:
    return UPLOAD_DIR / document.stored_filename


def list_documents(db: Session, q: str | None = None, document_type: str | None = None) -> list[Document]:
    statement = select(Document).options(selectinload(Document.uploaded_by)).order_by(Document.upload_date.desc())
    if q:
        like = f"%{q.strip()}%"
        statement = statement.where(or_(Document.title.ilike(like), Document.category.ilike(like), Document.original_filename.ilike(like)))
    if document_type:
        statement = statement.where(Document.document_type == document_type)
    return db.scalars(statement).all()


def create_visit(db: Session, data: dict, current_user: User) -> VisitRecord:
    if data["organization"] not in VISIT_ORGANIZATIONS:
        raise ValueError("Invalid visit organization.")
    visit = VisitRecord(**data, created_by_user_id=current_user.id)
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return visit


def create_audit(db: Session, data: dict, current_user: User) -> AuditRecord:
    audit = AuditRecord(**data, created_by_user_id=current_user.id)
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def create_inventory_item(db: Session, data: dict) -> InventoryItem:
    if data["item_type"] not in INVENTORY_TYPES:
        raise ValueError("Invalid inventory item type.")
    if data["quantity"] < 0 or data["available_quantity"] < 0 or data["damaged_quantity"] < 0:
        raise ValueError("Inventory quantities cannot be negative.")
    if data["available_quantity"] + data["damaged_quantity"] > data["quantity"]:
        raise ValueError("Available plus damaged quantity cannot exceed total quantity.")
    item = InventoryItem(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def create_arrival(db: Session, data: dict) -> NewArrival:
    if data["material_type"] not in MATERIAL_TYPES:
        raise ValueError("Invalid material type.")
    if db.scalar(select(NewArrival).where(NewArrival.arrival_number == data["arrival_number"])):
        raise ValueError("Arrival number already exists.")
    arrival = NewArrival(**data)
    db.add(arrival)
    db.commit()
    db.refresh(arrival)
    return arrival


def report_data(db: Session, report_type: str) -> Phase8Report:
    if report_type == "visits":
        records = db.scalars(select(VisitRecord).options(selectinload(VisitRecord.attachment)).order_by(VisitRecord.visit_date.desc())).all()
        rows = [[r.visit_date, r.organization, r.visit_type, r.department, r.status, r.follow_up_date, r.attachment.title if r.attachment else ""] for r in records]
        return Phase8Report("Visit Records Report", ["Date", "Organization", "Type", "Department", "Status", "Follow Up", "Attachment"], rows)
    if report_type == "audits":
        records = db.scalars(select(AuditRecord).options(selectinload(AuditRecord.attachment)).order_by(AuditRecord.audit_date.desc())).all()
        rows = [[r.audit_date, r.audit_type, r.financial_year, r.responsible_person, r.status, r.attachment.title if r.attachment else ""] for r in records]
        return Phase8Report("Audit Records Report", ["Date", "Type", "Year", "Responsible", "Status", "Attachment"], rows)
    if report_type == "inventory":
        records = db.scalars(select(InventoryItem).order_by(InventoryItem.item_type, InventoryItem.item_name)).all()
        rows = [[r.item_name, r.item_type, r.quantity, r.available_quantity, r.damaged_quantity, r.condition, r.location] for r in records]
        return Phase8Report("Furniture and Equipment Report", ["Item", "Type", "Qty", "Available", "Damaged", "Condition", "Location"], rows)
    if report_type == "arrivals":
        records = db.scalars(select(NewArrival).options(selectinload(NewArrival.category), selectinload(NewArrival.department_category)).order_by(NewArrival.received_date.desc())).all()
        rows = [[r.arrival_number, r.material_type, r.title, r.category.name if r.category else "", r.department_category.name if r.department_category else "", r.quantity, r.received_date] for r in records]
        return Phase8Report("New Arrivals, Journals and Magazines Report", ["No", "Type", "Title", "Category", "Department", "Qty", "Received"], rows)
    if report_type == "documents":
        records = db.scalars(select(Document).options(selectinload(Document.uploaded_by)).order_by(Document.upload_date.desc())).all()
        rows = [[r.title, r.document_type, r.version, r.category, r.uploaded_by.full_name if r.uploaded_by else "", r.upload_date.date(), r.original_filename] for r in records]
        return Phase8Report("SOP and National Library Rates Documents Report", ["Title", "Type", "Version", "Category", "Uploaded By", "Date", "File"], rows)
    raise ValueError("Invalid report type.")


def export_csv(result: Phase8Report) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(result.headers)
    writer.writerows(result.rows)
    return output.getvalue().encode("utf-8")


def export_excel(result: Phase8Report) -> bytes:
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


def export_pdf(result: Phase8Report) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 45
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(40, y, "Dr A Q Khan Institute of Computer Sciences and Information Technology")
    y -= 18
    pdf.drawString(40, y, "KICSIT Library Management System")
    y -= 18
    pdf.drawString(40, y, result.title)
    y -= 22
    pdf.setFont("Helvetica", 8)
    pdf.drawString(40, y, f"Generated: {date.today().isoformat()} | Total: {len(result.rows)}")
    y -= 18
    for row in result.rows:
        pdf.drawString(40, y, " | ".join(clean(v)[:24] for v in row[:7]))
        y -= 14
        if y < 55:
            pdf.showPage()
            y = height - 45
            pdf.setFont("Helvetica", 8)
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()
