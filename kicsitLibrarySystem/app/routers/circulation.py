from datetime import date

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import BookCopy, Employee, Fine, IssueRecord, Student, User
from app.permissions import require_permission
from app.schemas.circulation import IssueBookForm, ReturnBookForm
from app.services.activity_log_service import write_activity_log
from app.services.circulation_service import (
    active_issues_for_consumer,
    default_due_date,
    find_consumer,
    get_copy_by_accession,
    get_issue_or_404,
    get_receive_or_404,
    issue_book,
    issue_history,
    parse_date,
    return_book,
    unpaid_fines_for_consumer,
)


router = APIRouter(prefix="/circulation", tags=["Circulation"])
templates = Jinja2Templates(directory="app/templates")


def render(request: Request, template: str, context: dict, status_code: int = status.HTTP_200_OK) -> HTMLResponse:
    settings = get_settings()
    base = {"request": request, "app_name": settings.app_name, "active_nav": "circulation"}
    base.update(context)
    return templates.TemplateResponse(template, base, status_code=status_code)


@router.get("/issue", response_class=HTMLResponse)
def issue_page(
    request: Request,
    consumer_type: str = "Student",
    consumer_query: str | None = None,
    accession_number: str | None = None,
    current_user: User = Depends(require_permission("circulation.manage")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    issue_date = date.today()
    context = {
        "current_user": current_user,
        "consumer_type": consumer_type,
        "consumer_query": consumer_query or "",
        "accession_number": accession_number or "",
        "issue_date": issue_date,
        "due_date": default_due_date(db, issue_date),
        "consumer": None,
        "consumer_active_issues": [],
        "consumer_unpaid_fines": [],
        "copy": None,
        "error": None,
    }
    try:
        if consumer_query:
            consumer = find_consumer(db, consumer_type, consumer_query)
            context["consumer"] = consumer
            context["consumer_active_issues"] = active_issues_for_consumer(db, consumer_type, consumer.id)
            context["consumer_unpaid_fines"] = unpaid_fines_for_consumer(db, consumer_type, consumer.id)
        if accession_number:
            context["copy"] = get_copy_by_accession(db, accession_number)
    except ValueError as exc:
        context["error"] = str(exc)
    return render(request, "circulation/issue.html", context)


@router.post("/issue")
def issue_action(
    request: Request,
    consumer_type: str = Form(...),
    consumer_query: str = Form(...),
    accession_number: str = Form(...),
    issue_date: str = Form(...),
    due_date: str = Form(...),
    remarks: str | None = Form(None),
    current_user: User = Depends(require_permission("circulation.manage")),
    db: Session = Depends(get_db),
):
    try:
        form = IssueBookForm(
            consumer_type=consumer_type,
            consumer_query=consumer_query,
            accession_number=accession_number,
            issue_date=parse_date(issue_date),
            due_date=parse_date(due_date),
            remarks=remarks,
        )
        issue = issue_book(db, form, current_user)
        write_activity_log(
            db,
            request=request,
            action="ISSUE_BOOK",
            module="Circulation",
            user=current_user,
            entity_name="IssueRecord",
            entity_id=str(issue.id),
            description=f"Issued {issue.book_copy.accession_number} to {issue.consumer_type}.",
        )
        return RedirectResponse(url=f"/circulation/issue/{issue.id}/slip", status_code=status.HTTP_302_FOUND)
    except ValueError as exc:
        return render(
            request,
            "circulation/issue.html",
            {
                "current_user": current_user,
                "consumer_type": consumer_type,
                "consumer_query": consumer_query,
                "accession_number": accession_number,
                "issue_date": issue_date,
                "due_date": due_date,
                "consumer": None,
                "consumer_active_issues": [],
                "consumer_unpaid_fines": [],
                "copy": None,
                "error": str(exc),
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/return", response_class=HTMLResponse)
def return_page(
    request: Request,
    accession_number: str | None = None,
    current_user: User = Depends(require_permission("circulation.manage")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    active_issue = None
    error = None
    try:
        if accession_number:
            copy = get_copy_by_accession(db, accession_number)
            active_issue = db.scalar(select(IssueRecord).where(IssueRecord.book_copy_id == copy.id, IssueRecord.status == "Active"))
            if active_issue:
                active_issue = get_issue_or_404(db, active_issue.id)
            else:
                error = "No active issue found for this accession number."
    except ValueError as exc:
        error = str(exc)
    return render(
        request,
        "circulation/return.html",
        {
            "current_user": current_user,
            "accession_number": accession_number or "",
            "receive_date": date.today(),
            "active_issue": active_issue,
            "error": error,
        },
    )


@router.post("/return")
def return_action(
    request: Request,
    accession_number: str = Form(...),
    receive_date: str = Form(...),
    book_condition: str = Form("Normal"),
    fine_collected_status: str = Form("Unpaid"),
    remarks: str | None = Form(None),
    current_user: User = Depends(require_permission("circulation.manage")),
    db: Session = Depends(get_db),
):
    try:
        form = ReturnBookForm(
            accession_number=accession_number,
            receive_date=parse_date(receive_date),
            book_condition=book_condition,
            fine_collected_status=fine_collected_status,
            remarks=remarks,
        )
        receive = return_book(db, form, current_user)
        write_activity_log(
            db,
            request=request,
            action="RETURN_BOOK",
            module="Circulation",
            user=current_user,
            entity_name="ReceiveRecord",
            entity_id=str(receive.id),
            description=f"Returned {receive.book_copy.accession_number}. Fine: {receive.calculated_fine_amount}",
        )
        return RedirectResponse(url=f"/circulation/return/{receive.id}/slip", status_code=status.HTTP_302_FOUND)
    except ValueError as exc:
        return render(
            request,
            "circulation/return.html",
            {
                "current_user": current_user,
                "accession_number": accession_number,
                "receive_date": receive_date,
                "active_issue": None,
                "error": str(exc),
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/history", response_class=HTMLResponse)
def history_page(
    request: Request,
    q: str | None = None,
    current_user: User = Depends(require_permission("circulation.manage")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    records = issue_history(db, q)
    return render(request, "circulation/history.html", {"current_user": current_user, "records": records, "q": q or "", "active_nav": "history"})


@router.get("/issue/{issue_id}/slip", response_class=HTMLResponse)
def issue_slip(
    request: Request,
    issue_id: int,
    current_user: User = Depends(require_permission("circulation.manage")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    issue = get_issue_or_404(db, issue_id)
    return render(request, "circulation/issue_slip.html", {"current_user": current_user, "issue": issue})


@router.get("/return/{receive_id}/slip", response_class=HTMLResponse)
def return_slip(
    request: Request,
    receive_id: int,
    current_user: User = Depends(require_permission("circulation.manage")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    receive = get_receive_or_404(db, receive_id)
    issue = get_issue_or_404(db, receive.issue_record_id)
    fine = db.scalar(select(Fine).where(Fine.receive_record_id == receive.id))
    return render(request, "circulation/return_slip.html", {"current_user": current_user, "receive": receive, "issue": issue, "fine": fine})
