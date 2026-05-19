from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.permissions import require_permission
from app.schemas.phase5 import DamagedBookForm, LostBookForm, ReservationForm
from app.services.activity_log_service import write_activity_log
from app.services.phase5_service import (
    calculated_overdue_fine,
    create_damaged_book,
    create_lost_book,
    create_notification_record,
    create_reservation,
    list_books_for_reservation,
    list_damaged_books,
    list_lost_books,
    list_reservations,
    mark_fine_paid,
    overdue_excel_bytes,
    overdue_pdf_bytes,
    overdue_records,
    parse_date,
    reservation_ready_notification,
    set_reservation_status,
    unpaid_fines,
    get_reservation_or_404,
)


router = APIRouter(tags=["Phase 5"])
templates = Jinja2Templates(directory="app/templates")


def render(request: Request, template: str, context: dict, active_nav: str, status_code: int = status.HTTP_200_OK) -> HTMLResponse:
    settings = get_settings()
    base = {"request": request, "app_name": settings.app_name, "active_nav": active_nav}
    base.update(context)
    return templates.TemplateResponse(template, base, status_code=status_code)


@router.get("/reservations", response_class=HTMLResponse)
def reservations_page(request: Request, status_filter: str | None = None, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    return render(request, "phase5/reservations.html", {"current_user": current_user, "reservations": list_reservations(db, status_filter), "books": list_books_for_reservation(db), "today": date.today(), "default_expiry": date.today() + timedelta(days=3), "status_filter": status_filter or "", "error": None}, "reservations")


@router.post("/reservations")
def create_reservation_action(request: Request, consumer_type: str = Form(...), consumer_query: str = Form(...), book_master_id: int = Form(...), book_copy_id: str | None = Form(None), reservation_date: str = Form(...), expiry_date: str = Form(...), remarks: str | None = Form(None), current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    try:
        form = ReservationForm(consumer_type=consumer_type, consumer_query=consumer_query, book_master_id=book_master_id, book_copy_id=int(book_copy_id) if book_copy_id else None, reservation_date=parse_date(reservation_date), expiry_date=parse_date(expiry_date), remarks=remarks)
        reservation = create_reservation(db, form, current_user)
        write_activity_log(db, request=request, action="RESERVATION_CREATED", module="Reservations", user=current_user, entity_name="Reservation", entity_id=str(reservation.id), description=f"Created reservation {reservation.reservation_number}.")
        return RedirectResponse(url="/reservations", status_code=status.HTTP_302_FOUND)
    except ValueError as exc:
        return render(request, "phase5/reservations.html", {"current_user": current_user, "reservations": list_reservations(db), "books": list_books_for_reservation(db), "today": date.today(), "default_expiry": date.today() + timedelta(days=3), "status_filter": "", "error": str(exc)}, "reservations", status.HTTP_400_BAD_REQUEST)


@router.post("/reservations/{reservation_id}/ready")
def reservation_ready(request: Request, reservation_id: int, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    reservation = get_reservation_or_404(db, reservation_id)
    set_reservation_status(db, reservation, "Ready for pickup")
    reservation_ready_notification(db, reservation)
    write_activity_log(db, request=request, action="RESERVATION_READY", module="Reservations", user=current_user, entity_name="Reservation", entity_id=str(reservation.id), description=f"Reservation ready: {reservation.reservation_number}")
    return RedirectResponse(url="/reservations", status_code=status.HTTP_302_FOUND)


@router.post("/reservations/{reservation_id}/complete")
def reservation_complete(request: Request, reservation_id: int, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    reservation = get_reservation_or_404(db, reservation_id)
    set_reservation_status(db, reservation, "Completed")
    write_activity_log(db, request=request, action="RESERVATION_COMPLETED", module="Reservations", user=current_user, entity_name="Reservation", entity_id=str(reservation.id), description=f"Reservation completed: {reservation.reservation_number}")
    return RedirectResponse(url="/reservations", status_code=status.HTTP_302_FOUND)


@router.post("/reservations/{reservation_id}/cancel")
def reservation_cancel(request: Request, reservation_id: int, reason: str = Form(...), current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    reservation = get_reservation_or_404(db, reservation_id)
    set_reservation_status(db, reservation, "Cancelled", reason)
    write_activity_log(db, request=request, action="RESERVATION_CANCELLED", module="Reservations", user=current_user, entity_name="Reservation", entity_id=str(reservation.id), description=f"Reservation cancelled: {reason}")
    return RedirectResponse(url="/reservations", status_code=status.HTTP_302_FOUND)


@router.get("/overdue", response_class=HTMLResponse)
def overdue_page(request: Request, q: str | None = None, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    as_of = date.today()
    records = overdue_records(db, as_of, q)
    return render(request, "phase5/overdue.html", {"current_user": current_user, "records": records, "q": q or "", "as_of": as_of, "fine_func": calculated_overdue_fine}, "overdue")


@router.post("/overdue/{issue_id}/reminder")
def send_overdue_reminder(request: Request, issue_id: int, channel: str = Form("Email"), current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    from app.services.circulation_service import get_issue_or_404
    issue = get_issue_or_404(db, issue_id)
    create_notification_record(db, consumer_type=issue.consumer_type, student_id=issue.student_id, employee_id=issue.employee_id, notification_type="Overdue", channel=channel, subject="Library book overdue reminder", message=f"Book '{issue.book_master.title}' with accession {issue.book_copy.accession_number} is overdue since {issue.due_date}.")
    write_activity_log(db, request=request, action="SEND_OVERDUE_REMINDER", module="Overdue", user=current_user, entity_name="IssueRecord", entity_id=str(issue.id), description=f"Created {channel} reminder record.")
    return RedirectResponse(url="/overdue", status_code=status.HTTP_302_FOUND)


@router.get("/overdue/export/pdf")
def overdue_pdf(q: str | None = None, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    as_of = date.today()
    data = overdue_pdf_bytes(overdue_records(db, as_of, q), as_of)
    return Response(data, media_type="application/pdf", headers={"Content-Disposition": 'attachment; filename="overdue-report.pdf"'})


@router.get("/overdue/export/excel")
def overdue_excel(q: str | None = None, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    as_of = date.today()
    data = overdue_excel_bytes(overdue_records(db, as_of, q), as_of)
    return Response(data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": 'attachment; filename="overdue-report.xlsx"'})


@router.get("/fines/unpaid", response_class=HTMLResponse)
def unpaid_fines_page(request: Request, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    return render(request, "phase5/unpaid_fines.html", {"current_user": current_user, "fines": unpaid_fines(db)}, "fines")


@router.post("/fines/{fine_id}/paid")
def fine_paid(request: Request, fine_id: int, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    fine = mark_fine_paid(db, fine_id, current_user)
    write_activity_log(db, request=request, action="FINE_PAID", module="Fines", user=current_user, entity_name="Fine", entity_id=str(fine.id), description=f"Marked fine paid: {fine.fine_number}")
    return RedirectResponse(url="/fines/unpaid", status_code=status.HTTP_302_FOUND)


@router.get("/lost-books", response_class=HTMLResponse)
def lost_books_page(request: Request, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    return render(request, "phase5/lost_books.html", {"current_user": current_user, "records": list_lost_books(db), "today": date.today(), "error": None}, "lost")


@router.post("/lost-books")
def create_lost_action(request: Request, accession_number: str = Form(...), lost_date: str = Form(...), fine_amount: str = Form("0"), payment_status: str = Form("Unpaid"), remarks: str | None = Form(None), current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    try:
        record = create_lost_book(db, LostBookForm(accession_number=accession_number, lost_date=parse_date(lost_date), fine_amount=Decimal(fine_amount or "0"), payment_status=payment_status, remarks=remarks))
        write_activity_log(db, request=request, action="MARK_LOST", module="Lost Books", user=current_user, entity_name="LostBook", entity_id=str(record.id), description=f"Marked lost: {accession_number}")
        return RedirectResponse(url="/lost-books", status_code=status.HTTP_302_FOUND)
    except ValueError as exc:
        return render(request, "phase5/lost_books.html", {"current_user": current_user, "records": list_lost_books(db), "today": date.today(), "error": str(exc)}, "lost", status.HTTP_400_BAD_REQUEST)


@router.get("/damaged-books", response_class=HTMLResponse)
def damaged_books_page(request: Request, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    return render(request, "phase5/damaged_books.html", {"current_user": current_user, "records": list_damaged_books(db), "today": date.today(), "error": None}, "damaged")


@router.post("/damaged-books")
def create_damaged_action(request: Request, accession_number: str = Form(...), damage_date: str = Form(...), damage_level: str = Form(...), repair_cost: str = Form("0"), remarks: str | None = Form(None), current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    try:
        record = create_damaged_book(db, DamagedBookForm(accession_number=accession_number, damage_date=parse_date(damage_date), damage_level=damage_level, repair_cost=Decimal(repair_cost or "0"), remarks=remarks))
        write_activity_log(db, request=request, action="MARK_DAMAGED", module="Damaged Books", user=current_user, entity_name="DamagedBook", entity_id=str(record.id), description=f"Marked damaged: {accession_number}")
        return RedirectResponse(url="/damaged-books", status_code=status.HTTP_302_FOUND)
    except ValueError as exc:
        return render(request, "phase5/damaged_books.html", {"current_user": current_user, "records": list_damaged_books(db), "today": date.today(), "error": str(exc)}, "damaged", status.HTTP_400_BAD_REQUEST)

