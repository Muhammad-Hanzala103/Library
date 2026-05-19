from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.permissions import require_permission
from app.services.activity_log_service import write_activity_log
from app.services.phase6_service import (
    book_history_by_accession,
    clearance_pdf_bytes,
    clear_student,
    consistency_mismatches,
    correct_copy_status,
    find_student_for_clearance,
    parse_date,
    student_clearance_context,
)


router = APIRouter(tags=["Phase 6"])
templates = Jinja2Templates(directory="app/templates")


def render(request: Request, template: str, context: dict, active_nav: str, status_code: int = status.HTTP_200_OK) -> HTMLResponse:
    settings = get_settings()
    base = {"request": request, "app_name": settings.app_name, "active_nav": active_nav}
    base.update(context)
    return templates.TemplateResponse(template, base, status_code=status_code)


@router.get("/clearance", response_class=HTMLResponse)
def clearance_page(request: Request, q: str | None = None, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    student = find_student_for_clearance(db, q) if q else None
    context = student_clearance_context(db, student) if student else None
    return render(request, "phase6/clearance.html", {"current_user": current_user, "q": q or "", "student": student, "context": context, "error": None}, "clearance")


@router.post("/clearance/{student_id}/clear")
def clear_student_action(request: Request, student_id: int, remarks: str = Form(...), current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    from app.services.consumer_service import get_student_or_404
    student = get_student_or_404(db, student_id)
    try:
        clear_student(db, student, remarks, current_user)
        write_activity_log(db, request=request, action="STUDENT_CLEARED", module="Clearance", user=current_user, entity_name="Student", entity_id=str(student.id), description=f"Student cleared: {student.registration_number}")
        return RedirectResponse(url=f"/clearance?q={student.registration_number}", status_code=status.HTTP_302_FOUND)
    except ValueError as exc:
        context = student_clearance_context(db, student)
        return render(request, "phase6/clearance.html", {"current_user": current_user, "q": student.registration_number, "student": student, "context": context, "error": str(exc)}, "clearance", status.HTTP_400_BAD_REQUEST)


@router.get("/clearance/{student_id}/pdf")
def clearance_pdf(student_id: int, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    from app.services.consumer_service import get_student_or_404
    student = get_student_or_404(db, student_id)
    context = student_clearance_context(db, student)
    data = clearance_pdf_bytes(student, context, current_user)
    return Response(data, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="clearance-{student.registration_number}.pdf"'})


@router.get("/book-history", response_class=HTMLResponse)
def book_history_page(request: Request, accession_number: str | None = None, selected_date: str | None = None, current_user: User = Depends(require_permission("catalog.manage")), db: Session = Depends(get_db)):
    history = None
    error = None
    if accession_number:
        try:
            history = book_history_by_accession(db, accession_number, parse_date(selected_date) if selected_date else None)
        except ValueError as exc:
            error = str(exc)
    return render(request, "phase6/book_history.html", {"current_user": current_user, "accession_number": accession_number or "", "selected_date": selected_date or "", "history": history, "error": error}, "book_history")


@router.get("/status-checker", response_class=HTMLResponse)
def status_checker_page(request: Request, current_user: User = Depends(require_permission("catalog.manage")), db: Session = Depends(get_db)):
    return render(request, "phase6/status_checker.html", {"current_user": current_user, "mismatches": consistency_mismatches(db), "error": None}, "status_checker")


@router.post("/status-checker/{copy_id}/correct")
def correct_status_action(request: Request, copy_id: int, new_status: str = Form(...), reason: str = Form(...), current_user: User = Depends(require_permission("catalog.manage")), db: Session = Depends(get_db)):
    try:
        copy = correct_copy_status(db, copy_id, new_status, reason, current_user)
        write_activity_log(db, request=request, action="STATUS_CORRECTED", module="Status Checker", user=current_user, entity_name="BookCopy", entity_id=str(copy.id), description=f"Corrected status to {new_status}. Reason: {reason}")
        return RedirectResponse(url="/status-checker", status_code=status.HTTP_302_FOUND)
    except ValueError as exc:
        return render(request, "phase6/status_checker.html", {"current_user": current_user, "mismatches": consistency_mismatches(db), "error": str(exc)}, "status_checker", status.HTTP_400_BAD_REQUEST)

