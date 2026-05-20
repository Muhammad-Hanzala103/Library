from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.permissions import require_permission
from app.services import settings_service
from app.services.activity_log_service import write_activity_log

router = APIRouter(prefix="/settings", tags=["Settings"])
templates = Jinja2Templates(directory="app/templates")


def render(request: Request, template: str, context: dict, active_nav: str = "settings", status_code: int = status.HTTP_200_OK) -> HTMLResponse:
    settings = get_settings()
    base = {"request": request, "app_name": settings.app_name, "active_nav": active_nav}
    base.update(context)
    return templates.TemplateResponse(template, base, status_code=status_code)


@router.get("", response_class=HTMLResponse)
def view_settings(
    request: Request,
    current_user: User = Depends(require_permission("settings.manage")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    grouped = settings_service.settings_by_category(db)
    return render(
        request,
        "settings/index.html",
        {"current_user": current_user, "grouped_settings": grouped},
        active_nav="settings",
    )


@router.post("")
async def update_settings(
    request: Request,
    current_user: User = Depends(require_permission("settings.manage")),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    form_data = await request.form()
    for key, val in form_data.items():
        if "." in key:
            settings_service.save_setting_value(db, key, str(val))
    
    db.commit()
    write_activity_log(
        db,
        request=request,
        action="UPDATE_SETTINGS",
        module="Settings",
        user=current_user,
        entity_name="Setting",
        entity_id="bulk",
        description="Bulk updated system settings.",
    )
    return RedirectResponse(url="/settings?msg=Settings+updated+successfully", status_code=status.HTTP_303_SEE_OTHER)
