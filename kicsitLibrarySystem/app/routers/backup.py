from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.permissions import require_permission
from app.services import backup_service
from app.services.activity_log_service import write_activity_log

router = APIRouter(prefix="/backups", tags=["Backups"])
templates = Jinja2Templates(directory="app/templates")


def render(request: Request, template: str, context: dict, active_nav: str = "backups", status_code: int = status.HTTP_200_OK) -> HTMLResponse:
    settings = get_settings()
    base = {"request": request, "app_name": settings.app_name, "active_nav": active_nav}
    base.update(context)
    return templates.TemplateResponse(template, base, status_code=status_code)


@router.get("", response_class=HTMLResponse)
def list_backups_page(
    request: Request,
    current_user: User = Depends(require_permission("system.manage_all")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    backups = backup_service.list_backups(db)
    return render(
        request,
        "backup/index.html",
        {"current_user": current_user, "backups": backups},
        active_nav="backups",
    )


@router.post("/create")
def create_backup_action(
    request: Request,
    current_user: User = Depends(require_permission("system.manage_all")),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    try:
        backup = backup_service.create_db_backup(db, current_user.username)
        write_activity_log(
            db,
            request=request,
            action="CREATE_BACKUP",
            module="Backups",
            user=current_user,
            entity_name="Backup",
            entity_id=str(backup.id),
            description=f"Created database backup: {backup.filename}.",
        )
        return RedirectResponse(url="/backups?msg=Backup+created+successfully", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as exc:
        return RedirectResponse(url=f"/backups?error={str(exc)}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{backup_id}/restore")
def restore_backup_action(
    request: Request,
    backup_id: int,
    current_user: User = Depends(require_permission("system.manage_all")),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    try:
        backup = backup_service.restore_db_backup(db, backup_id)
        write_activity_log(
            db,
            request=request,
            action="RESTORE_BACKUP",
            module="Backups",
            user=current_user,
            entity_name="Backup",
            entity_id=str(backup.id),
            description=f"Restored database from backup: {backup.filename}.",
        )
        return RedirectResponse(url="/backups?msg=Database+restored+successfully", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as exc:
        return RedirectResponse(url=f"/backups?error={str(exc)}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{backup_id}/delete")
def delete_backup_action(
    request: Request,
    backup_id: int,
    current_user: User = Depends(require_permission("system.manage_all")),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    try:
        backup_service.delete_backup(db, backup_id)
        write_activity_log(
            db,
            request=request,
            action="DELETE_BACKUP",
            module="Backups",
            user=current_user,
            entity_name="Backup",
            entity_id=str(backup_id),
            description=f"Deleted database backup ID {backup_id}.",
        )
        return RedirectResponse(url="/backups?msg=Backup+deleted+successfully", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as exc:
        return RedirectResponse(url=f"/backups?error={str(exc)}", status_code=status.HTTP_303_SEE_OTHER)
