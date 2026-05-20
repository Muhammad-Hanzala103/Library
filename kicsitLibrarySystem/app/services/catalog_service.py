import csv
import io
import re
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.models import (
    Author,
    BookCopy,
    BookMaster,
    Category,
    DepartmentCategory,
    IssueRecord,
    LiteratureCategory,
    Publisher,
    User,
)
from app.schemas.catalog import BookCopyForm, BookMasterForm, PublisherCreate, ReferenceCreate


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png"}
BOOK_STATUSES = {"Available", "Issued", "Reserved", "Overdue", "Lost", "Damaged", "Missing", "Repairing"}


def clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def parse_optional_int(value: str | None) -> int | None:
    value = clean_optional(value)
    return int(value) if value else None


def list_reference_data(db: Session) -> dict[str, list]:
    return {
        "authors": db.scalars(select(Author).where(Author.is_active == True).order_by(Author.name)).all(),  # noqa: E712
        "publishers": db.scalars(select(Publisher).where(Publisher.is_active == True).order_by(Publisher.name)).all(),  # noqa: E712
        "categories": db.scalars(select(Category).where(Category.is_active == True).order_by(Category.name)).all(),  # noqa: E712
        "department_categories": db.scalars(
            select(DepartmentCategory).where(DepartmentCategory.is_active == True).order_by(DepartmentCategory.name)  # noqa: E712
        ).all(),
        "literature_categories": db.scalars(
            select(LiteratureCategory).where(LiteratureCategory.is_active == True).order_by(LiteratureCategory.name)  # noqa: E712
        ).all(),
    }


def get_book_or_404(db: Session, book_id: int) -> BookMaster:
    book = db.scalar(
        select(BookMaster)
        .options(
            selectinload(BookMaster.authors),
            selectinload(BookMaster.publisher),
            selectinload(BookMaster.category),
            selectinload(BookMaster.department_category),
            selectinload(BookMaster.literature_category),
            selectinload(BookMaster.copies),
        )
        .where(BookMaster.id == book_id, BookMaster.is_deleted == False)  # noqa: E712
    )
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


def search_books(db: Session, query: str | None = None) -> list[BookMaster]:
    statement = (
        select(BookMaster)
        .options(
            selectinload(BookMaster.authors),
            selectinload(BookMaster.publisher),
            selectinload(BookMaster.category),
            selectinload(BookMaster.department_category),
            selectinload(BookMaster.literature_category),
            selectinload(BookMaster.copies),
        )
        .where(BookMaster.is_deleted == False)  # noqa: E712
        .order_by(BookMaster.created_at.desc())
    )
    query = clean_optional(query)
    if query:
        like = f"%{query}%"
        statement = statement.outerjoin(BookMaster.authors).outerjoin(BookMaster.copies).where(
            or_(
                BookMaster.title.ilike(like),
                BookMaster.unique_title.ilike(like),
                BookMaster.isbn.ilike(like),
                BookMaster.issn.ilike(like),
                BookMaster.keywords.ilike(like),
                Author.name.ilike(like),
                BookCopy.accession_number.ilike(like),
            )
        )
    return db.scalars(statement).unique().all()


def search_copies(db: Session, query: str | None = None) -> list[BookCopy]:
    statement = (
        select(BookCopy)
        .options(selectinload(BookCopy.book_master))
        .join(BookCopy.book_master)
        .where(BookCopy.is_deleted == False, BookMaster.is_deleted == False)  # noqa: E712
        .order_by(BookCopy.created_at.desc())
    )
    query = clean_optional(query)
    if query:
        like = f"%{query}%"
        statement = statement.where(
            or_(
                BookCopy.accession_number.ilike(like),
                BookCopy.barcode_value.ilike(like),
                BookCopy.rack.ilike(like),
                BookCopy.shelf.ilike(like),
                BookCopy.location.ilike(like),
                BookMaster.title.ilike(like),
                BookMaster.isbn.ilike(like),
                BookMaster.issn.ilike(like),
            )
        )
    return db.scalars(statement).unique().all()


def ensure_unique_accession(db: Session, accession_number: str, exclude_copy_id: int | None = None) -> None:
    statement = select(BookCopy).where(BookCopy.accession_number == accession_number)
    if exclude_copy_id:
        statement = statement.where(BookCopy.id != exclude_copy_id)
    if db.scalar(statement):
        raise ValueError("Accession number already exists.")


def copy_has_active_issue(db: Session, copy_id: int) -> bool:
    return db.scalar(
        select(IssueRecord.id).where(IssueRecord.book_copy_id == copy_id, IssueRecord.status == "Active")
    ) is not None


def save_book_image(upload: UploadFile | None) -> str | None:
    if upload is None or not upload.filename:
        return None
    settings = get_settings()
    original_name = Path(upload.filename).name
    extension = Path(original_name).suffix.lower()
    if extension not in IMAGE_EXTENSIONS or upload.content_type not in IMAGE_CONTENT_TYPES:
        raise ValueError("Only JPG and PNG book images are allowed.")

    upload.file.seek(0, 2)
    size = upload.file.tell()
    upload.file.seek(0)
    if size > settings.max_upload_size_bytes:
        raise ValueError(f"Book image must be {settings.max_upload_size_mb} MB or smaller.")

    safe_stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", Path(original_name).stem).strip("-")[:50] or "book"
    stored_filename = f"{uuid.uuid4().hex}_{safe_stem}{extension}"
    target_dir = Path("app/uploads/book_images")
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / stored_filename
    with target_path.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    return stored_filename


def create_book(db: Session, form: BookMasterForm, current_user: User, image: UploadFile | None) -> BookMaster:
    book = BookMaster(**form.model_dump(exclude={"author_ids"}))
    book.created_by_user_id = current_user.id
    book.updated_by_user_id = current_user.id
    image_filename = save_book_image(image)
    if image_filename:
        book.book_image_filename = image_filename
    if form.author_ids:
        book.authors = db.scalars(select(Author).where(Author.id.in_(form.author_ids))).all()
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def update_book(db: Session, book: BookMaster, form: BookMasterForm, current_user: User, image: UploadFile | None) -> BookMaster:
    for key, value in form.model_dump(exclude={"author_ids"}).items():
        setattr(book, key, value)
    book.updated_by_user_id = current_user.id
    image_filename = save_book_image(image)
    if image_filename:
        book.book_image_filename = image_filename
    book.authors = db.scalars(select(Author).where(Author.id.in_(form.author_ids))).all() if form.author_ids else []
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def soft_delete_book(db: Session, book: BookMaster, reason: str, current_user: User) -> None:
    reason = clean_optional(reason)
    if not reason:
        raise ValueError("Deletion reason is required.")
    active_copies = [copy for copy in book.copies if not copy.is_deleted]
    issued_copies = [copy.accession_number for copy in active_copies if copy_has_active_issue(db, copy.id)]
    if issued_copies:
        raise ValueError(
            "Cannot delete a book while active issues exist for accession number(s): "
            + ", ".join(issued_copies)
        )
    for copy in active_copies:
        copy.is_deleted = True
        copy.deleted_reason = reason
        copy.deleted_by_user_id = current_user.id
        copy.deleted_at = datetime.utcnow()
    book.is_deleted = True
    book.deleted_reason = reason
    book.deleted_by_user_id = current_user.id
    book.deleted_at = datetime.utcnow()
    book.quantity = 0
    db.add(book)
    db.commit()


def create_copy(db: Session, form: BookCopyForm) -> BookCopy:
    ensure_unique_accession(db, form.accession_number)
    if form.status not in BOOK_STATUSES:
        raise ValueError("Invalid book copy status.")
    book = db.scalar(select(BookMaster).where(BookMaster.id == form.book_master_id, BookMaster.is_deleted == False))  # noqa: E712
    if book is None:
        raise ValueError("Selected book does not exist.")
    copy = BookCopy(**form.model_dump())
    db.add(copy)
    db.flush()
    db.commit()
    book.quantity = db.scalar(
        select(func.count(BookCopy.id)).where(BookCopy.book_master_id == book.id, BookCopy.is_deleted == False)  # noqa: E712
    ) or 0
    db.add(book)
    db.commit()
    db.refresh(copy)
    return copy


def update_copy(db: Session, copy: BookCopy, form: BookCopyForm) -> BookCopy:
    ensure_unique_accession(db, form.accession_number, exclude_copy_id=copy.id)
    if form.status not in BOOK_STATUSES:
        raise ValueError("Invalid book copy status.")
    for key, value in form.model_dump().items():
        setattr(copy, key, value)
    db.add(copy)
    db.commit()
    db.refresh(copy)
    return copy


def soft_delete_copy(db: Session, copy: BookCopy, reason: str, current_user: User) -> None:
    reason = clean_optional(reason)
    if not reason:
        raise ValueError("Deletion reason is required.")
    if copy_has_active_issue(db, copy.id):
        raise ValueError("Cannot delete an accession copy while it has an active issue.")
    copy.is_deleted = True
    copy.deleted_reason = reason
    copy.deleted_by_user_id = current_user.id
    copy.deleted_at = datetime.utcnow()
    db.add(copy)
    db.flush()
    book = copy.book_master or db.get(BookMaster, copy.book_master_id)
    if book:
        book.quantity = db.scalar(
            select(func.count(BookCopy.id)).where(BookCopy.book_master_id == book.id, BookCopy.is_deleted == False)  # noqa: E712
        ) or 0
        db.add(book)
    db.commit()


def get_copy_or_404(db: Session, copy_id: int) -> BookCopy:
    copy = db.scalar(
        select(BookCopy)
        .options(selectinload(BookCopy.book_master))
        .where(BookCopy.id == copy_id, BookCopy.is_deleted == False)  # noqa: E712
    )
    if copy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book copy not found")
    return copy


def create_author(db: Session, payload: ReferenceCreate) -> Author:
    author = Author(name=payload.name.strip(), description=clean_optional(payload.description))
    db.add(author)
    db.commit()
    db.refresh(author)
    return author


def create_publisher(db: Session, payload: PublisherCreate) -> Publisher:
    publisher = Publisher(
        name=payload.name.strip(),
        city=clean_optional(payload.city),
        country=clean_optional(payload.country),
        contact=clean_optional(payload.contact),
    )
    db.add(publisher)
    db.commit()
    db.refresh(publisher)
    return publisher


def create_category(db: Session, model, payload: ReferenceCreate):
    record = model(
        name=payload.name.strip(),
        code=clean_optional(payload.code),
        description=clean_optional(payload.description),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def catalog_import_template_csv() -> str:
    headers = [
        "title",
        "unique_title",
        "author_names",
        "publisher_name",
        "isbn",
        "issn",
        "department_category",
        "literature_category",
        "category",
        "accession_number",
        "copy_number",
        "location",
        "rack",
        "shelf",
        "hall",
        "price",
        "purchase_date",
        "supplier",
    ]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerow(
        [
            "Introduction to Algorithms",
            "CS Introduction to Algorithms",
            "Thomas H. Cormen; Charles E. Leiserson",
            "MIT Press",
            "9780262046305",
            "",
            "CS",
            "",
            "Programming",
            "KICSIT-0001",
            "1",
            "Main Library",
            "R1",
            "S2",
            "Hall A",
            "4500",
            "2026-05-19",
            "Approved Supplier",
        ]
    )
    return output.getvalue()
