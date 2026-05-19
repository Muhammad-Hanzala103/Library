from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import ActivityLog, Permission, Role, User
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

