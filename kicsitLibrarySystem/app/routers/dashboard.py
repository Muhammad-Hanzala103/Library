from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import ActivityLog, BookCopy, BookMaster, DamagedBook, Employee, Fine, IssueRecord, LostBook, Permission, Reservation, Role, Student, User
from app.permissions import require_permission
from app.services.auth_service import get_user_permission_codes


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def dashboard_home(
    request: Request,
    current_user: User = Depends(require_permission("dashboard.view")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    settings = get_settings()
    metrics = {
        "users": db.scalar(select(func.count(User.id))) or 0,
        "roles": db.scalar(select(func.count(Role.id))) or 0,
        "permissions": db.scalar(select(func.count(Permission.id))) or 0,
        "activity_logs": db.scalar(select(func.count(ActivityLog.id))) or 0,
        "books": db.scalar(select(func.count(BookMaster.id)).where(BookMaster.is_deleted == False)) or 0,  # noqa: E712
        "copies": db.scalar(select(func.count(BookCopy.id)).where(BookCopy.is_deleted == False)) or 0,  # noqa: E712
        "students": db.scalar(select(func.count(Student.id))) or 0,
        "employees": db.scalar(select(func.count(Employee.id))) or 0,
        "active_issues": db.scalar(select(func.count(IssueRecord.id)).where(IssueRecord.status == "Active")) or 0,
        "unpaid_fines": db.scalar(select(func.count(Fine.id)).where(Fine.payment_status.in_(["Unpaid", "Partial"]))) or 0,
        "reservations": db.scalar(select(func.count(Reservation.id)).where(Reservation.status.in_(["Waiting", "Ready for pickup"]))) or 0,
        "lost_books": db.scalar(select(func.count(LostBook.id)).where(LostBook.resolved_status == "Unresolved")) or 0,
        "damaged_books": db.scalar(select(func.count(DamagedBook.id)).where(DamagedBook.resolved_status == "Unresolved")) or 0,
    }
    recent_logs = db.scalars(select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(8)).all()
    permissions = get_user_permission_codes(current_user)
    return templates.TemplateResponse(
        "dashboard/index.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "current_user": current_user,
            "permissions": permissions,
            "metrics": metrics,
            "recent_logs": recent_logs,
        },
    )
