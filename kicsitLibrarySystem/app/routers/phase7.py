from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.database import get_db
from app.models import ImportBatch, User
from app.permissions import require_permission
from app.services.activity_log_service import write_activity_log
from app.services.phase7_service import (
    REPORT_TITLES,
    build_report,
    commit_import,
    global_search,
    import_error_csv,
    import_preview,
    parse_csv_upload,
    report_csv,
    report_excel,
    report_pdf,
)


router = APIRouter(tags=["Phase 7"])
templates = Jinja2Templates(directory="app/templates")


def render(request: Request, template: str, context: dict, active_nav: str, status_code: int = status.HTTP_200_OK) -> HTMLResponse:
    settings = get_settings()
    base = {"request": request, "app_name": settings.app_name, "active_nav": active_nav}
    base.update(context)
    return templates.TemplateResponse(template, base, status_code=status_code)


@router.get("/reports", response_class=HTMLResponse)
def reports_page(request: Request, report_type: str = "catalog", q: str | None = None, status_filter: str | None = None, current_user: User = Depends(require_permission("reports.view")), db: Session = Depends(get_db)):
    result = build_report(db, report_type, q, status_filter)
    return render(request, "phase7/reports.html", {"current_user": current_user, "report_types": REPORT_TITLES, "report_type": report_type, "q": q or "", "status_filter": status_filter or "", "result": result}, "reports")


@router.get("/reports/export/{fmt}")
def report_export(fmt: str, report_type: str = "catalog", q: str | None = None, status_filter: str | None = None, current_user: User = Depends(require_permission("reports.view")), db: Session = Depends(get_db)):
    result = build_report(db, report_type, q, status_filter)
    if fmt == "pdf":
        return Response(report_pdf(result), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{report_type}.pdf"'})
    if fmt == "excel":
        return Response(report_excel(result), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f'attachment; filename="{report_type}.xlsx"'})
    return Response(report_csv(result), media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="{report_type}.csv"'})


@router.get("/imports", response_class=HTMLResponse)
def imports_page(request: Request, current_user: User = Depends(require_permission("catalog.manage")), db: Session = Depends(get_db)):
    batches = db.scalars(select(ImportBatch).options(selectinload(ImportBatch.errors)).order_by(ImportBatch.created_at.desc()).limit(20)).all()
    return render(request, "phase7/imports.html", {"current_user": current_user, "batches": batches, "error": None}, "imports")


@router.post("/imports/preview")
async def import_preview_action(request: Request, import_type: str = Form(...), file: UploadFile = File(...), current_user: User = Depends(require_permission("catalog.manage")), db: Session = Depends(get_db)):
    try:
        rows = parse_csv_upload(await file.read())
        batch = import_preview(db, import_type, file.filename or "upload.csv", rows, current_user)
        if batch.failed_rows == 0:
            commit_import(db, batch, rows)
        write_activity_log(db, request=request, action="IMPORT_PREVIEW", module="Import", user=current_user, entity_name="ImportBatch", entity_id=str(batch.id), description=f"Previewed {import_type} import.")
        return RedirectResponse(url="/imports", status_code=status.HTTP_302_FOUND)
    except Exception as exc:
        batches = db.scalars(select(ImportBatch).options(selectinload(ImportBatch.errors)).order_by(ImportBatch.created_at.desc()).limit(20)).all()
        return render(request, "phase7/imports.html", {"current_user": current_user, "batches": batches, "error": str(exc)}, "imports", status.HTTP_400_BAD_REQUEST)


@router.get("/imports/{batch_id}/errors.csv")
def import_errors(batch_id: int, current_user: User = Depends(require_permission("catalog.manage")), db: Session = Depends(get_db)):
    batch = db.scalar(select(ImportBatch).options(selectinload(ImportBatch.errors)).where(ImportBatch.id == batch_id))
    if batch is None:
        return Response(b"", media_type="text/csv")
    return Response(import_error_csv(batch), media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="import-errors-{batch.id}.csv"'})


@router.get("/search", response_class=HTMLResponse)
def smart_search_page(request: Request, q: str | None = None, current_user: User = Depends(require_permission("dashboard.view")), db: Session = Depends(get_db)):
    results = global_search(db, q or "")
    return render(request, "phase7/search.html", {"current_user": current_user, "q": q or "", "results": results}, "search")
