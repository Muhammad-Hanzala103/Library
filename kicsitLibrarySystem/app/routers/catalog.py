from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import BookCopy, BookMaster, Category, DepartmentCategory, LiteratureCategory, User
from app.permissions import require_permission
from app.schemas.catalog import BookCopyForm, BookMasterForm, PublisherCreate, ReferenceCreate
from app.services.activity_log_service import write_activity_log
from app.services.catalog_service import (
    catalog_import_template_csv,
    create_author,
    create_book,
    create_category,
    create_copy,
    create_publisher,
    get_book_or_404,
    get_copy_or_404,
    list_reference_data,
    parse_optional_int,
    search_books,
    search_copies,
    soft_delete_book,
    soft_delete_copy,
    update_book,
)


router = APIRouter(prefix="/catalog", tags=["Catalog"])
templates = Jinja2Templates(directory="app/templates")


def render(
    request: Request,
    template: str,
    context: dict,
    status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
    settings = get_settings()
    base = {"request": request, "app_name": settings.app_name, "active_nav": "catalog"}
    base.update(context)
    return templates.TemplateResponse(template, base, status_code=status_code)


def parse_date(value: str | None) -> date | None:
    value = value.strip() if value else ""
    return date.fromisoformat(value) if value else None


def book_form_from_request(
    *,
    title: str,
    unique_title: str | None,
    subtitle: str | None,
    publisher_id: str | None,
    author_ids: list[int],
    isbn: str | None,
    issn: str | None,
    source: str | None,
    department_category_id: str | None,
    literature_category_id: str | None,
    category_id: str | None,
    edition: str | None,
    publication_place: str | None,
    publication_year: str | None,
    language: str | None,
    format: str | None,
    keywords: str | None,
    notes: str | None,
    price: str | None,
    book_location: str | None,
    rack: str | None,
    shelf: str | None,
    hall: str | None,
    description: str | None,
    bill_number: str | None,
    store_name: str | None,
    purchase_date: str | None,
    supplier: str | None,
) -> BookMasterForm:
    return BookMasterForm(
        title=title.strip(),
        unique_title=unique_title.strip() if unique_title else None,
        subtitle=subtitle.strip() if subtitle else None,
        publisher_id=parse_optional_int(publisher_id),
        author_ids=author_ids,
        isbn=isbn.strip() if isbn else None,
        issn=issn.strip() if issn else None,
        source=source.strip() if source else None,
        department_category_id=parse_optional_int(department_category_id),
        literature_category_id=parse_optional_int(literature_category_id),
        category_id=parse_optional_int(category_id),
        edition=edition.strip() if edition else None,
        publication_place=publication_place.strip() if publication_place else None,
        publication_year=parse_optional_int(publication_year),
        language=language.strip() if language else None,
        format=format.strip() if format else None,
        keywords=keywords.strip() if keywords else None,
        notes=notes.strip() if notes else None,
        price=price.strip() if price else None,
        book_location=book_location.strip() if book_location else None,
        rack=rack.strip() if rack else None,
        shelf=shelf.strip() if shelf else None,
        hall=hall.strip() if hall else None,
        description=description.strip() if description else None,
        bill_number=bill_number.strip() if bill_number else None,
        store_name=store_name.strip() if store_name else None,
        purchase_date=parse_date(purchase_date),
        supplier=supplier.strip() if supplier else None,
    )


@router.get("", response_class=HTMLResponse)
def manage_books(
    request: Request,
    q: str | None = None,
    current_user: User = Depends(require_permission("catalog.manage")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    books = search_books(db, q)
    return render(
        request,
        "catalog/manage_books.html",
        {"current_user": current_user, "books": books, "q": q or ""},
    )


@router.get("/new", response_class=HTMLResponse)
def new_book_page(
    request: Request,
    current_user: User = Depends(require_permission("catalog.manage")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    return render(
        request,
        "catalog/book_form.html",
        {
            "current_user": current_user,
            "book": None,
            "references": list_reference_data(db),
            "error": None,
            "mode": "create",
        },
    )


@router.post("/new")
def create_book_action(
    request: Request,
    title: str = Form(...),
    unique_title: str | None = Form(None),
    subtitle: str | None = Form(None),
    publisher_id: str | None = Form(None),
    author_ids: list[int] = Form(default=[]),
    isbn: str | None = Form(None),
    issn: str | None = Form(None),
    source: str | None = Form(None),
    department_category_id: str | None = Form(None),
    literature_category_id: str | None = Form(None),
    category_id: str | None = Form(None),
    edition: str | None = Form(None),
    publication_place: str | None = Form(None),
    publication_year: str | None = Form(None),
    language: str | None = Form(None),
    format: str | None = Form(None),
    keywords: str | None = Form(None),
    notes: str | None = Form(None),
    price: str | None = Form(None),
    book_location: str | None = Form(None),
    rack: str | None = Form(None),
    shelf: str | None = Form(None),
    hall: str | None = Form(None),
    description: str | None = Form(None),
    bill_number: str | None = Form(None),
    store_name: str | None = Form(None),
    purchase_date: str | None = Form(None),
    supplier: str | None = Form(None),
    book_image: UploadFile | None = File(None),
    current_user: User = Depends(require_permission("catalog.manage")),
    db: Session = Depends(get_db),
):
    try:
        form = book_form_from_request(
            title=title,
            unique_title=unique_title,
            subtitle=subtitle,
            publisher_id=publisher_id,
            author_ids=author_ids,
            isbn=isbn,
            issn=issn,
            source=source,
            department_category_id=department_category_id,
            literature_category_id=literature_category_id,
            category_id=category_id,
            edition=edition,
            publication_place=publication_place,
            publication_year=publication_year,
            language=language,
            format=format,
            keywords=keywords,
            notes=notes,
            price=price,
            book_location=book_location,
            rack=rack,
            shelf=shelf,
            hall=hall,
            description=description,
            bill_number=bill_number,
            store_name=store_name,
            purchase_date=purchase_date,
            supplier=supplier,
        )
        book = create_book(db, form, current_user, book_image)
        write_activity_log(
            db,
            request=request,
            action="ADD_BOOK",
            module="Catalog",
            user=current_user,
            entity_name="BookMaster",
            entity_id=str(book.id),
            description=f"Added book: {book.title}",
        )
        return RedirectResponse(url=f"/catalog/{book.id}", status_code=status.HTTP_302_FOUND)
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        return render(
            request,
            "catalog/book_form.html",
            {
                "current_user": current_user,
                "book": None,
                "references": list_reference_data(db),
                "error": str(exc),
                "mode": "create",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/copies", response_class=HTMLResponse)
def copies_page(
    request: Request,
    q: str | None = None,
    current_user: User = Depends(require_permission("catalog.manage")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    return render(
        request,
        "catalog/book_copies.html",
        {
            "current_user": current_user,
            "copies": search_copies(db, q),
            "books": search_books(db),
            "q": q or "",
            "error": None,
            "active_nav": "copies",
        },
    )


@router.post("/copies")
def create_copy_action(
    request: Request,
    book_master_id: int = Form(...),
    accession_number: str = Form(...),
    copy_number: int = Form(...),
    barcode_value: str | None = Form(None),
    rack: str | None = Form(None),
    shelf: str | None = Form(None),
    location: str | None = Form(None),
    hall: str | None = Form(None),
    physical_condition: str = Form("Good"),
    status_value: str = Form("Available"),
    current_user: User = Depends(require_permission("catalog.manage")),
    db: Session = Depends(get_db),
):
    try:
        form = BookCopyForm(
            book_master_id=book_master_id,
            accession_number=accession_number.strip(),
            copy_number=copy_number,
            barcode_value=barcode_value.strip() if barcode_value else None,
            rack=rack.strip() if rack else None,
            shelf=shelf.strip() if shelf else None,
            location=location.strip() if location else None,
            hall=hall.strip() if hall else None,
            physical_condition=physical_condition.strip() or "Good",
            status=status_value,
        )
        copy = create_copy(db, form)
        write_activity_log(
            db,
            request=request,
            action="ADD_BOOK_COPY",
            module="Catalog",
            user=current_user,
            entity_name="BookCopy",
            entity_id=str(copy.id),
            description=f"Added accession copy: {copy.accession_number}",
        )
        return RedirectResponse(url="/catalog/copies", status_code=status.HTTP_302_FOUND)
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        return render(
            request,
            "catalog/book_copies.html",
            {
                "current_user": current_user,
                "copies": search_copies(db),
                "books": search_books(db),
                "q": "",
                "error": str(exc),
                "active_nav": "copies",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.post("/copies/{copy_id}/delete")
def delete_copy_action(
    request: Request,
    copy_id: int,
    reason: str = Form(...),
    current_user: User = Depends(require_permission("catalog.manage")),
    db: Session = Depends(get_db),
):
    copy = get_copy_or_404(db, copy_id)
    try:
        soft_delete_copy(db, copy, reason, current_user)
    except ValueError as exc:
        return render(
            request,
            "catalog/book_copies.html",
            {
                "current_user": current_user,
                "copies": search_copies(db),
                "books": search_books(db),
                "q": "",
                "error": str(exc),
                "active_nav": "copies",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    write_activity_log(
        db,
        request=request,
        action="DELETE_BOOK_COPY",
        module="Catalog",
        user=current_user,
        entity_name="BookCopy",
        entity_id=str(copy.id),
        description=f"Deleted accession copy {copy.accession_number}. Reason: {reason}",
    )
    return RedirectResponse(url="/catalog/copies", status_code=status.HTTP_302_FOUND)


@router.get("/setup", response_class=HTMLResponse)
def setup_page(
    request: Request,
    current_user: User = Depends(require_permission("catalog.manage")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    return render(
        request,
        "catalog/setup.html",
        {
            "current_user": current_user,
            "references": list_reference_data(db),
            "error": None,
            "active_nav": "catalog_setup",
        },
    )


@router.post("/setup/{kind}")
def create_reference_action(
    request: Request,
    kind: str,
    name: str = Form(...),
    code: str | None = Form(None),
    description: str | None = Form(None),
    city: str | None = Form(None),
    country: str | None = Form(None),
    contact: str | None = Form(None),
    current_user: User = Depends(require_permission("catalog.manage")),
    db: Session = Depends(get_db),
):
    try:
        if kind == "authors":
            record = create_author(db, ReferenceCreate(name=name, description=description))
        elif kind == "publishers":
            record = create_publisher(db, PublisherCreate(name=name, city=city, country=country, contact=contact))
        elif kind == "categories":
            record = create_category(db, Category, ReferenceCreate(name=name, code=code, description=description))
        elif kind == "department-categories":
            record = create_category(db, DepartmentCategory, ReferenceCreate(name=name, code=code, description=description))
        elif kind == "literature-categories":
            record = create_category(db, LiteratureCategory, ReferenceCreate(name=name, code=code, description=description))
        else:
            return RedirectResponse(url="/catalog/setup", status_code=status.HTTP_302_FOUND)
        write_activity_log(
            db,
            request=request,
            action="ADD_CATALOG_REFERENCE",
            module="Catalog",
            user=current_user,
            entity_name=kind,
            entity_id=str(record.id),
            description=f"Added {kind}: {name}",
        )
        return RedirectResponse(url="/catalog/setup", status_code=status.HTTP_302_FOUND)
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        return render(
            request,
            "catalog/setup.html",
            {
                "current_user": current_user,
                "references": list_reference_data(db),
                "error": str(exc),
                "active_nav": "catalog_setup",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/import-template")
def import_template(current_user: User = Depends(require_permission("catalog.manage"))) -> Response:
    csv_text = catalog_import_template_csv()
    return Response(
        csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="kicsit_catalog_import_template.csv"'},
    )


@router.get("/book-images/{filename}")
def book_image(filename: str, current_user: User = Depends(require_permission("catalog.manage"))) -> FileResponse:
    safe_name = Path(filename).name
    image_path = Path("app/uploads/book_images") / safe_name
    if not image_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book image not found")
    return FileResponse(image_path)


@router.get("/{book_id}", response_class=HTMLResponse)
def view_book(
    request: Request,
    book_id: int,
    current_user: User = Depends(require_permission("catalog.manage")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    book = get_book_or_404(db, book_id)
    return render(request, "catalog/view_book.html", {"current_user": current_user, "book": book})


@router.get("/{book_id}/edit", response_class=HTMLResponse)
def edit_book_page(
    request: Request,
    book_id: int,
    current_user: User = Depends(require_permission("catalog.manage")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    book = get_book_or_404(db, book_id)
    return render(
        request,
        "catalog/book_form.html",
        {
            "current_user": current_user,
            "book": book,
            "references": list_reference_data(db),
            "error": None,
            "mode": "edit",
        },
    )


@router.post("/{book_id}/edit")
def edit_book_action(
    request: Request,
    book_id: int,
    title: str = Form(...),
    unique_title: str | None = Form(None),
    subtitle: str | None = Form(None),
    publisher_id: str | None = Form(None),
    author_ids: list[int] = Form(default=[]),
    isbn: str | None = Form(None),
    issn: str | None = Form(None),
    source: str | None = Form(None),
    department_category_id: str | None = Form(None),
    literature_category_id: str | None = Form(None),
    category_id: str | None = Form(None),
    edition: str | None = Form(None),
    publication_place: str | None = Form(None),
    publication_year: str | None = Form(None),
    language: str | None = Form(None),
    format: str | None = Form(None),
    keywords: str | None = Form(None),
    notes: str | None = Form(None),
    price: str | None = Form(None),
    book_location: str | None = Form(None),
    rack: str | None = Form(None),
    shelf: str | None = Form(None),
    hall: str | None = Form(None),
    description: str | None = Form(None),
    bill_number: str | None = Form(None),
    store_name: str | None = Form(None),
    purchase_date: str | None = Form(None),
    supplier: str | None = Form(None),
    book_image: UploadFile | None = File(None),
    current_user: User = Depends(require_permission("catalog.manage")),
    db: Session = Depends(get_db),
):
    book = get_book_or_404(db, book_id)
    try:
        form = book_form_from_request(
            title=title,
            unique_title=unique_title,
            subtitle=subtitle,
            publisher_id=publisher_id,
            author_ids=author_ids,
            isbn=isbn,
            issn=issn,
            source=source,
            department_category_id=department_category_id,
            literature_category_id=literature_category_id,
            category_id=category_id,
            edition=edition,
            publication_place=publication_place,
            publication_year=publication_year,
            language=language,
            format=format,
            keywords=keywords,
            notes=notes,
            price=price,
            book_location=book_location,
            rack=rack,
            shelf=shelf,
            hall=hall,
            description=description,
            bill_number=bill_number,
            store_name=store_name,
            purchase_date=purchase_date,
            supplier=supplier,
        )
        update_book(db, book, form, current_user, book_image)
        write_activity_log(
            db,
            request=request,
            action="EDIT_BOOK",
            module="Catalog",
            user=current_user,
            entity_name="BookMaster",
            entity_id=str(book.id),
            description=f"Edited book: {book.title}",
        )
        return RedirectResponse(url=f"/catalog/{book.id}", status_code=status.HTTP_302_FOUND)
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        return render(
            request,
            "catalog/book_form.html",
            {
                "current_user": current_user,
                "book": book,
                "references": list_reference_data(db),
                "error": str(exc),
                "mode": "edit",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/{book_id}/delete", response_class=HTMLResponse)
def delete_book_page(
    request: Request,
    book_id: int,
    current_user: User = Depends(require_permission("catalog.manage")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    book = get_book_or_404(db, book_id)
    return render(request, "catalog/delete_book.html", {"current_user": current_user, "book": book, "error": None})


@router.post("/{book_id}/delete")
def delete_book_action(
    request: Request,
    book_id: int,
    reason: str = Form(...),
    current_user: User = Depends(require_permission("catalog.manage")),
    db: Session = Depends(get_db),
):
    book = get_book_or_404(db, book_id)
    try:
        soft_delete_book(db, book, reason, current_user)
        write_activity_log(
            db,
            request=request,
            action="DELETE_BOOK",
            module="Catalog",
            user=current_user,
            entity_name="BookMaster",
            entity_id=str(book.id),
            description=f"Deleted book {book.title}. Reason: {reason}",
        )
        return RedirectResponse(url="/catalog", status_code=status.HTTP_302_FOUND)
    except ValueError as exc:
        return render(
            request,
            "catalog/delete_book.html",
            {"current_user": current_user, "book": book, "error": str(exc)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
