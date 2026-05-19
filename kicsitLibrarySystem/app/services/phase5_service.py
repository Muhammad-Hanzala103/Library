import io
from datetime import date, datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    BookCopy,
    BookMaster,
    DamagedBook,
    Employee,
    Fine,
    IssueRecord,
    LostBook,
    Notification,
    Reservation,
    Student,
    User,
)
from app.schemas.phase5 import DAMAGE_LEVELS, RESERVATION_STATUSES, DamagedBookForm, LostBookForm, ReservationForm
from app.services.circulation_service import active_issue_for_copy, find_consumer, get_copy_by_accession, next_number


def clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def parse_date(value: str | None, fallback: date | None = None) -> date:
    value = clean_optional(value)
    if value:
        return date.fromisoformat(value)
    return fallback or date.today()


def consumer_name(record) -> str:
    if getattr(record, "student", None):
        return record.student.name
    if getattr(record, "employee", None):
        return record.employee.name
    return ""


def consumer_identifier(record) -> str:
    if getattr(record, "student", None):
        return record.student.registration_number
    if getattr(record, "employee", None):
        return record.employee.p_number or record.employee.cnic or ""
    return ""


def list_books_for_reservation(db: Session) -> list[BookMaster]:
    return db.scalars(select(BookMaster).where(BookMaster.is_deleted == False).order_by(BookMaster.title)).all()  # noqa: E712


def create_reservation(db: Session, form: ReservationForm, current_user: User) -> Reservation:
    if form.expiry_date <= form.reservation_date:
        raise ValueError("Expiry date must be after reservation date.")
    consumer = find_consumer(db, form.consumer_type, form.consumer_query)
    book = db.get(BookMaster, form.book_master_id)
    if book is None or book.is_deleted:
        raise ValueError("Book not found.")
    max_position = db.scalar(
        select(func.max(Reservation.queue_position)).where(
            Reservation.book_master_id == book.id,
            Reservation.status.in_(["Waiting", "Ready for pickup"]),
        )
    ) or 0
    reservation = Reservation(
        reservation_number=next_number(db, Reservation, "reservation_number", "RSV"),
        consumer_type=form.consumer_type,
        student_id=consumer.id if form.consumer_type == "Student" else None,
        employee_id=consumer.id if form.consumer_type == "Employee" else None,
        book_master_id=book.id,
        book_copy_id=form.book_copy_id,
        reservation_date=form.reservation_date,
        expiry_date=form.expiry_date,
        queue_position=max_position + 1,
        status="Waiting",
        remarks=clean_optional(form.remarks),
        created_by_user_id=current_user.id,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def list_reservations(db: Session, status_filter: str | None = None) -> list[Reservation]:
    statement = (
        select(Reservation)
        .options(selectinload(Reservation.student), selectinload(Reservation.employee), selectinload(Reservation.book_master), selectinload(Reservation.book_copy))
        .order_by(Reservation.book_master_id, Reservation.queue_position)
    )
    if status_filter:
        statement = statement.where(Reservation.status == status_filter)
    return db.scalars(statement).all()


def get_reservation_or_404(db: Session, reservation_id: int) -> Reservation:
    reservation = db.scalar(
        select(Reservation)
        .options(selectinload(Reservation.student), selectinload(Reservation.employee), selectinload(Reservation.book_master), selectinload(Reservation.book_copy))
        .where(Reservation.id == reservation_id)
    )
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    return reservation


def set_reservation_status(db: Session, reservation: Reservation, new_status: str, reason: str | None = None) -> Reservation:
    if new_status not in RESERVATION_STATUSES:
        raise ValueError("Invalid reservation status.")
    if new_status == "Cancelled" and not clean_optional(reason):
        raise ValueError("Cancellation reason is required.")
    reservation.status = new_status
    reservation.cancelled_reason = clean_optional(reason)
    reservation.updated_at = datetime.utcnow()
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def create_notification_record(
    db: Session,
    *,
    consumer_type: str,
    student_id: int | None,
    employee_id: int | None,
    notification_type: str,
    channel: str,
    subject: str,
    message: str,
    status_value: str = "Pending",
    failure_reason: str | None = None,
) -> Notification:
    notification = Notification(
        consumer_type=consumer_type,
        student_id=student_id,
        employee_id=employee_id,
        notification_type=notification_type,
        channel=channel,
        subject=subject,
        message=message,
        status=status_value,
        failure_reason=failure_reason,
        whatsapp_placeholder="Future WhatsApp API integration" if channel == "WhatsApp" else None,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def reservation_ready_notification(db: Session, reservation: Reservation) -> Notification:
    return create_notification_record(
        db,
        consumer_type=reservation.consumer_type,
        student_id=reservation.student_id,
        employee_id=reservation.employee_id,
        notification_type="Reservation Ready",
        channel="Email",
        subject="Reserved book ready for pickup",
        message=f"Your reserved book '{reservation.book_master.title}' is ready for pickup.",
    )


def overdue_records(db: Session, as_of: date | None = None, query: str | None = None) -> list[IssueRecord]:
    as_of = as_of or date.today()
    statement = (
        select(IssueRecord)
        .options(selectinload(IssueRecord.book_copy), selectinload(IssueRecord.book_master), selectinload(IssueRecord.student), selectinload(IssueRecord.employee))
        .join(IssueRecord.book_copy)
        .join(IssueRecord.book_master)
        .outerjoin(IssueRecord.student)
        .outerjoin(IssueRecord.employee)
        .where(IssueRecord.status == "Active", IssueRecord.due_date < as_of)
        .order_by(IssueRecord.due_date)
    )
    query = clean_optional(query)
    if query:
        like = f"%{query}%"
        statement = statement.where(
            or_(
                BookCopy.accession_number.ilike(like),
                BookMaster.title.ilike(like),
                Student.registration_number.ilike(like),
                Student.name.ilike(like),
                Employee.p_number.ilike(like),
                Employee.cnic.ilike(like),
                Employee.name.ilike(like),
            )
        )
    return db.scalars(statement).unique().all()


def calculated_overdue_fine(issue: IssueRecord, as_of: date | None = None) -> Decimal:
    as_of = as_of or date.today()
    days = max((as_of - issue.due_date).days, 0)
    return Decimal(days) * Decimal("10.00")


def unpaid_fines(db: Session) -> list[Fine]:
    return db.scalars(
        select(Fine)
        .options(selectinload(Fine.student), selectinload(Fine.employee), selectinload(Fine.book_copy))
        .where(Fine.payment_status.in_(["Unpaid", "Partial"]))
        .order_by(Fine.created_at.desc())
    ).all()


def mark_fine_paid(db: Session, fine_id: int, current_user: User) -> Fine:
    fine = db.get(Fine, fine_id)
    if fine is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fine not found")
    fine.paid_amount = fine.fine_amount
    fine.remaining_amount = Decimal("0.00")
    fine.payment_status = "Paid"
    fine.payment_date = date.today()
    fine.collected_by_user_id = current_user.id
    db.add(fine)
    db.commit()
    db.refresh(fine)
    return fine


def create_lost_book(db: Session, form: LostBookForm) -> LostBook:
    copy = get_copy_by_accession(db, form.accession_number)
    issue = active_issue_for_copy(db, copy.id)
    if issue is None:
        raise ValueError("Lost book requires an active issue.")
    issue.status = "Lost"
    issue.closed_at = datetime.utcnow()
    copy.status = "Lost"
    copy.current_holder_type = None
    copy.current_holder_reference = None
    record = LostBook(
        lost_date=form.lost_date,
        issue_record_id=issue.id,
        book_copy_id=copy.id,
        consumer_type=issue.consumer_type,
        student_id=issue.student_id,
        employee_id=issue.employee_id,
        fine_amount=form.fine_amount,
        payment_status=form.payment_status,
        remarks=clean_optional(form.remarks),
        resolved_status="Unresolved",
    )
    db.add(record)
    if form.fine_amount > 0:
        db.add(
            Fine(
                fine_number=next_number(db, Fine, "fine_number", "FIN"),
                issue_record_id=issue.id,
                book_copy_id=copy.id,
                consumer_type=issue.consumer_type,
                student_id=issue.student_id,
                employee_id=issue.employee_id,
                fine_type="Lost",
                fine_amount=form.fine_amount,
                paid_amount=form.fine_amount if form.payment_status == "Paid" else Decimal("0.00"),
                remaining_amount=Decimal("0.00") if form.payment_status == "Paid" else form.fine_amount,
                payment_status=form.payment_status,
                payment_date=form.lost_date if form.payment_status == "Paid" else None,
            )
        )
    db.commit()
    db.refresh(record)
    return record


def create_damaged_book(db: Session, form: DamagedBookForm) -> DamagedBook:
    if form.damage_level not in DAMAGE_LEVELS:
        raise ValueError("Invalid damage level.")
    copy = get_copy_by_accession(db, form.accession_number)
    issue = active_issue_for_copy(db, copy.id)
    if issue is None:
        raise ValueError("Damaged book requires an active issue.")
    issue.status = "Damaged"
    issue.closed_at = datetime.utcnow()
    copy.status = "Damaged"
    copy.current_holder_type = None
    copy.current_holder_reference = None
    record = DamagedBook(
        damage_date=form.damage_date,
        issue_record_id=issue.id,
        book_copy_id=copy.id,
        consumer_type=issue.consumer_type,
        student_id=issue.student_id,
        employee_id=issue.employee_id,
        damage_level=form.damage_level,
        repair_cost=form.repair_cost,
        remarks=clean_optional(form.remarks),
        resolved_status="Unresolved",
    )
    db.add(record)
    if form.repair_cost > 0:
        db.add(
            Fine(
                fine_number=next_number(db, Fine, "fine_number", "FIN"),
                issue_record_id=issue.id,
                book_copy_id=copy.id,
                consumer_type=issue.consumer_type,
                student_id=issue.student_id,
                employee_id=issue.employee_id,
                fine_type="Damaged",
                fine_amount=form.repair_cost,
                paid_amount=Decimal("0.00"),
                remaining_amount=form.repair_cost,
                payment_status="Unpaid",
            )
        )
    db.commit()
    db.refresh(record)
    return record


def list_lost_books(db: Session) -> list[LostBook]:
    return db.scalars(select(LostBook).options(selectinload(LostBook.book_copy), selectinload(LostBook.student), selectinload(LostBook.employee)).order_by(LostBook.created_at.desc())).all()


def list_damaged_books(db: Session) -> list[DamagedBook]:
    return db.scalars(select(DamagedBook).options(selectinload(DamagedBook.book_copy), selectinload(DamagedBook.student), selectinload(DamagedBook.employee)).order_by(DamagedBook.created_at.desc())).all()


def overdue_pdf_bytes(records: list[IssueRecord], as_of: date) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "KICSIT Library - Overdue Report")
    y -= 25
    pdf.setFont("Helvetica", 9)
    pdf.drawString(40, y, f"Generated date: {as_of.isoformat()} | Total: {len(records)}")
    y -= 25
    for item in records:
        days = max((as_of - item.due_date).days, 0)
        line = f"{item.book_copy.accession_number} | {item.book_master.title[:35]} | {consumer_name(item)} | Due {item.due_date} | {days} days | Fine {calculated_overdue_fine(item, as_of)}"
        pdf.drawString(40, y, line)
        y -= 16
        if y < 60:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 9)
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def overdue_excel_bytes(records: list[IssueRecord], as_of: date) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Overdue"
    sheet.append(["Accession", "Title", "Consumer", "Identifier", "Issue Date", "Due Date", "Overdue Days", "Fine"])
    for item in records:
        days = max((as_of - item.due_date).days, 0)
        sheet.append([
            item.book_copy.accession_number,
            item.book_master.title,
            consumer_name(item),
            consumer_identifier(item),
            item.issue_date.isoformat(),
            item.due_date.isoformat(),
            days,
            float(calculated_overdue_fine(item, as_of)),
        ])
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

