from datetime import date, datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import BookCopy, BookMaster, Employee, Fine, IssueRecord, ReceiveRecord, Student, User
from app.schemas.circulation import CONSUMER_TYPES, FINE_STATUSES, RETURN_CONDITIONS, IssueBookForm, ReturnBookForm


DEFAULT_FINE_PER_DAY = Decimal("10.00")
STUDENT_ISSUE_LIMIT = 3
FACULTY_ISSUE_LIMIT = 5
STAFF_ISSUE_LIMIT = 3


def clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def parse_date(value: str | None, fallback: date | None = None) -> date:
    value = clean_optional(value)
    if value:
        return date.fromisoformat(value)
    if fallback:
        return fallback
    return date.today()


def default_due_date(issue_date: date) -> date:
    return issue_date + timedelta(days=14)


def next_number(db: Session, model, field_name: str, prefix: str) -> str:
    count_value = db.scalar(select(func.count(model.id))) or 0
    return f"{prefix}-{count_value + 1:06d}"


def find_consumer(db: Session, consumer_type: str, query: str) -> Student | Employee:
    query = query.strip()
    if consumer_type == "Student":
        consumer = db.scalar(
            select(Student).where(
                or_(
                    Student.registration_number == query,
                    Student.admission_number == query,
                    Student.roll_number == query,
                    Student.name.ilike(f"%{query}%"),
                    Student.phone == query,
                )
            )
        )
    elif consumer_type == "Employee":
        consumer = db.scalar(
            select(Employee).where(
                or_(
                    Employee.p_number == query,
                    Employee.cnic == query,
                    Employee.name.ilike(f"%{query}%"),
                    Employee.phone == query,
                )
            )
        )
    else:
        raise ValueError("Invalid consumer type.")
    if consumer is None:
        raise ValueError("Consumer not found.")
    if not consumer.is_active:
        raise ValueError("Consumer is inactive.")
    return consumer


def get_copy_by_accession(db: Session, accession_number: str) -> BookCopy:
    copy = db.scalar(
        select(BookCopy)
        .options(selectinload(BookCopy.book_master))
        .where(BookCopy.accession_number == accession_number.strip(), BookCopy.is_deleted == False)  # noqa: E712
    )
    if copy is None:
        raise ValueError("Book copy not found.")
    return copy


def active_issue_for_copy(db: Session, copy_id: int) -> IssueRecord | None:
    return db.scalar(
        select(IssueRecord)
        .options(selectinload(IssueRecord.book_copy), selectinload(IssueRecord.book_master), selectinload(IssueRecord.student), selectinload(IssueRecord.employee))
        .where(IssueRecord.book_copy_id == copy_id, IssueRecord.status == "Active")
    )


def active_issues_for_consumer(db: Session, consumer_type: str, consumer_id: int) -> list[IssueRecord]:
    statement = select(IssueRecord).where(IssueRecord.status == "Active")
    if consumer_type == "Student":
        statement = statement.where(IssueRecord.student_id == consumer_id)
    else:
        statement = statement.where(IssueRecord.employee_id == consumer_id)
    return db.scalars(statement).all()


def unpaid_fines_for_consumer(db: Session, consumer_type: str, consumer_id: int) -> list[Fine]:
    statement = select(Fine).where(Fine.payment_status.in_(["Unpaid", "Partial"]))
    if consumer_type == "Student":
        statement = statement.where(Fine.student_id == consumer_id)
    else:
        statement = statement.where(Fine.employee_id == consumer_id)
    return db.scalars(statement).all()


def issue_limit_for_consumer(consumer_type: str, consumer: Student | Employee) -> int:
    if consumer_type == "Student":
        return STUDENT_ISSUE_LIMIT
    if consumer.employee_type in {"Permanent Faculty", "Visiting Faculty"}:
        return FACULTY_ISSUE_LIMIT
    return STAFF_ISSUE_LIMIT


def validate_issue(db: Session, form: IssueBookForm, consumer: Student | Employee, copy: BookCopy) -> None:
    if form.consumer_type not in CONSUMER_TYPES:
        raise ValueError("Invalid consumer type.")
    if form.due_date <= form.issue_date:
        raise ValueError("Due date must be after issue date.")
    if form.consumer_type == "Student":
        if consumer.clearance_status == "Cleared" or consumer.status == "Cleared":
            raise ValueError("Student is cleared and cannot issue books.")
        if consumer.status == "Blocked":
            raise ValueError("Student is blocked.")
    if copy.status != "Available":
        raise ValueError(f"Book copy is not available. Current status: {copy.status}.")
    if active_issue_for_copy(db, copy.id):
        raise ValueError("This accession number already has an active issue.")
    active_count = len(active_issues_for_consumer(db, form.consumer_type, consumer.id))
    limit = issue_limit_for_consumer(form.consumer_type, consumer)
    if active_count >= limit:
        raise ValueError(f"Issue limit reached. Limit is {limit}.")
    if unpaid_fines_for_consumer(db, form.consumer_type, consumer.id):
        raise ValueError("Pending unpaid fine blocks issue.")


def issue_book(db: Session, form: IssueBookForm, current_user: User) -> IssueRecord:
    consumer = find_consumer(db, form.consumer_type, form.consumer_query)
    copy = get_copy_by_accession(db, form.accession_number)
    validate_issue(db, form, consumer, copy)
    issue = IssueRecord(
        issue_number=next_number(db, IssueRecord, "issue_number", "ISS"),
        book_copy_id=copy.id,
        book_master_id=copy.book_master_id,
        consumer_type=form.consumer_type,
        student_id=consumer.id if form.consumer_type == "Student" else None,
        employee_id=consumer.id if form.consumer_type == "Employee" else None,
        issue_date=form.issue_date,
        due_date=form.due_date,
        status="Active",
        remarks=clean_optional(form.remarks),
        issued_by_user_id=current_user.id,
    )
    copy.status = "Issued"
    copy.current_holder_type = form.consumer_type
    copy.current_holder_reference = getattr(consumer, "registration_number", None) or getattr(consumer, "p_number", None) or getattr(consumer, "cnic", None)
    copy.last_issue_date = form.issue_date
    db.add(issue)
    db.add(copy)
    db.commit()
    db.refresh(issue)
    return get_issue_or_404(db, issue.id)


def get_issue_or_404(db: Session, issue_id: int) -> IssueRecord:
    issue = db.scalar(
        select(IssueRecord)
        .options(
            selectinload(IssueRecord.book_copy),
            selectinload(IssueRecord.book_master),
            selectinload(IssueRecord.student),
            selectinload(IssueRecord.employee),
            selectinload(IssueRecord.receive_record),
            selectinload(IssueRecord.fines),
        )
        .where(IssueRecord.id == issue_id)
    )
    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue record not found")
    return issue


def get_receive_or_404(db: Session, receive_id: int) -> ReceiveRecord:
    receive = db.scalar(
        select(ReceiveRecord)
        .options(selectinload(ReceiveRecord.issue_record), selectinload(ReceiveRecord.book_copy))
        .where(ReceiveRecord.id == receive_id)
    )
    if receive is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receive record not found")
    return receive


def calculate_overdue_days(due_date: date, receive_date: date) -> int:
    if receive_date <= due_date:
        return 0
    return (receive_date - due_date).days


def return_book(db: Session, form: ReturnBookForm, current_user: User) -> ReceiveRecord:
    if form.book_condition not in RETURN_CONDITIONS:
        raise ValueError("Invalid book condition.")
    if form.fine_collected_status not in FINE_STATUSES:
        raise ValueError("Invalid fine collection status.")
    copy = get_copy_by_accession(db, form.accession_number)
    issue = active_issue_for_copy(db, copy.id)
    if issue is None:
        raise ValueError("No active issue found for this accession number.")
    if form.receive_date < issue.issue_date:
        raise ValueError("Receive date cannot be before issue date.")

    overdue_days = calculate_overdue_days(issue.due_date, form.receive_date)
    fine_amount = DEFAULT_FINE_PER_DAY * Decimal(overdue_days)
    receive = ReceiveRecord(
        receive_number=next_number(db, ReceiveRecord, "receive_number", "RCV"),
        issue_record_id=issue.id,
        book_copy_id=copy.id,
        receive_date=form.receive_date,
        book_condition=form.book_condition,
        overdue_days=overdue_days,
        calculated_fine_amount=fine_amount,
        fine_collected_status=form.fine_collected_status if fine_amount > 0 else "Paid",
        remarks=clean_optional(form.remarks),
        received_by_user_id=current_user.id,
    )
    issue.status = "Returned" if form.book_condition == "Normal" else form.book_condition
    issue.closed_at = datetime.utcnow()
    copy.status = "Available" if form.book_condition == "Normal" else form.book_condition
    copy.current_holder_type = None
    copy.current_holder_reference = None
    copy.last_receive_date = form.receive_date

    db.add(receive)
    db.flush()
    if fine_amount > 0:
        paid_amount = fine_amount if form.fine_collected_status == "Paid" else Decimal("0.00")
        fine = Fine(
            fine_number=next_number(db, Fine, "fine_number", "FIN"),
            issue_record_id=issue.id,
            receive_record_id=receive.id,
            book_copy_id=copy.id,
            consumer_type=issue.consumer_type,
            student_id=issue.student_id,
            employee_id=issue.employee_id,
            fine_type="Overdue",
            fine_amount=fine_amount,
            paid_amount=paid_amount,
            remaining_amount=fine_amount - paid_amount,
            payment_status=form.fine_collected_status,
            payment_date=form.receive_date if form.fine_collected_status == "Paid" else None,
            collected_by_user_id=current_user.id if form.fine_collected_status == "Paid" else None,
        )
        db.add(fine)
    db.add(issue)
    db.add(copy)
    db.commit()
    db.refresh(receive)
    return get_receive_or_404(db, receive.id)


def issue_history(db: Session, query: str | None = None) -> list[IssueRecord]:
    statement = (
        select(IssueRecord)
        .options(selectinload(IssueRecord.book_copy), selectinload(IssueRecord.book_master), selectinload(IssueRecord.student), selectinload(IssueRecord.employee), selectinload(IssueRecord.receive_record))
        .join(IssueRecord.book_copy)
        .join(IssueRecord.book_master)
        .outerjoin(IssueRecord.student)
        .outerjoin(IssueRecord.employee)
        .order_by(IssueRecord.created_at.desc())
    )
    query = clean_optional(query)
    if query:
        like = f"%{query}%"
        statement = statement.where(
            or_(
                IssueRecord.issue_number.ilike(like),
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

