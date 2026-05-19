from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.database import get_db
from app.models import AuditRecord, Category, DepartmentCategory, Document, InventoryItem, NewArrival, User, VisitRecord
from app.permissions import require_permission
from app.services.activity_log_service import write_activity_log
from app.services.phase8_service import (
    DOCUMENT_TYPES,
    INVENTORY_TYPES,
    MATERIAL_TYPES,
    VISIT_ORGANIZATIONS,
    create_arrival,
    create_audit,
    create_inventory_item,
    create_visit,
    document_file_path,
    export_csv,
    export_excel,
    export_pdf,
    list_documents,
    parse_optional_date,
    parse_optional_decimal,
    parse_optional_int,
    report_data,
    save_document_upload,
)


router = APIRouter(tags=["Phase 8"])
templates = Jinja2Templates(directory="app/templates")


PHASE8_REPORTS = {
    "visits": "Visit Records",
    "audits": "Audit Records",
    "inventory": "Furniture and Equipment",
    "arrivals": "New Arrivals, Journals and Magazines",
    "documents": "SOP and National Library Rates Documents",
}


def render(request: Request, template: str, context: dict, active_nav: str, status_code: int = status.HTTP_200_OK) -> HTMLResponse:
    settings = get_settings()
    base = {"request": request, "app_name": settings.app_name, "active_nav": active_nav}
    base.update(context)
    return templates.TemplateResponse(template, base, status_code=status_code)


def documents_for_select(db: Session, document_type: str | None = None) -> list[Document]:
    statement = select(Document).where(Document.is_active == True).order_by(Document.upload_date.desc())  # noqa: E712
    if document_type:
        statement = statement.where(Document.document_type == document_type)
    return db.scalars(statement).all()


@router.get("/visits", response_class=HTMLResponse)
def visits_page(request: Request, q: str | None = None, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    statement = select(VisitRecord).options(selectinload(VisitRecord.attachment)).order_by(VisitRecord.visit_date.desc())
    if q:
        like = f"%{q.strip()}%"
        statement = statement.where(or_(VisitRecord.organization.ilike(like), VisitRecord.department.ilike(like), VisitRecord.visit_type.ilike(like), VisitRecord.status.ilike(like)))
    return render(request, "phase8/visits.html", {"current_user": current_user, "records": db.scalars(statement).all(), "q": q or "", "organizations": VISIT_ORGANIZATIONS, "documents": documents_for_select(db, "Visit evidence"), "error": None}, "visits")


@router.post("/visits")
def create_visit_action(
    request: Request,
    visit_date: str = Form(...),
    organization: str = Form(...),
    visit_type: str = Form(...),
    team_members: str | None = Form(None),
    department: str | None = Form(None),
    purpose: str | None = Form(None),
    observations: str | None = Form(None),
    suggestions: str | None = Form(None),
    findings: str | None = Form(None),
    action_taken: str | None = Form(None),
    follow_up_date: str | None = Form(None),
    status_value: str = Form("Open"),
    attachment_document_id: str | None = Form(None),
    current_user: User = Depends(require_permission("circulation.manage")),
    db: Session = Depends(get_db),
):
    try:
        visit = create_visit(
            db,
            {
                "visit_date": parse_optional_date(visit_date),
                "organization": organization,
                "visit_type": visit_type.strip(),
                "team_members": team_members or None,
                "department": department or None,
                "purpose": purpose or None,
                "observations": observations or None,
                "suggestions": suggestions or None,
                "findings": findings or None,
                "action_taken": action_taken or None,
                "follow_up_date": parse_optional_date(follow_up_date),
                "status": status_value.strip() or "Open",
                "attachment_document_id": parse_optional_int(attachment_document_id, 0) or None,
            },
            current_user,
        )
        write_activity_log(db, request=request, action="VISIT_ADDED", module="Audit", user=current_user, entity_name="VisitRecord", entity_id=str(visit.id), description=f"Added {organization} visit.")
        return RedirectResponse(url="/visits", status_code=status.HTTP_302_FOUND)
    except Exception as exc:
        records = db.scalars(select(VisitRecord).options(selectinload(VisitRecord.attachment)).order_by(VisitRecord.visit_date.desc())).all()
        return render(request, "phase8/visits.html", {"current_user": current_user, "records": records, "q": "", "organizations": VISIT_ORGANIZATIONS, "documents": documents_for_select(db, "Visit evidence"), "error": str(exc)}, "visits", status.HTTP_400_BAD_REQUEST)


@router.get("/audits", response_class=HTMLResponse)
def audits_page(request: Request, q: str | None = None, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    statement = select(AuditRecord).options(selectinload(AuditRecord.attachment)).order_by(AuditRecord.audit_date.desc())
    if q:
        like = f"%{q.strip()}%"
        statement = statement.where(or_(AuditRecord.audit_type.ilike(like), AuditRecord.financial_year.ilike(like), AuditRecord.responsible_person.ilike(like), AuditRecord.status.ilike(like)))
    return render(request, "phase8/audits.html", {"current_user": current_user, "records": db.scalars(statement).all(), "q": q or "", "documents": documents_for_select(db, "Audit evidence"), "error": None}, "audits")


@router.post("/audits")
def create_audit_action(
    request: Request,
    audit_date: str = Form(...),
    audit_type: str = Form(...),
    financial_year: str | None = Form(None),
    observations: str | None = Form(None),
    suggestions: str | None = Form(None),
    findings: str | None = Form(None),
    recommendations: str | None = Form(None),
    action_required: str | None = Form(None),
    action_taken: str | None = Form(None),
    responsible_person: str | None = Form(None),
    status_value: str = Form("Open"),
    attachment_document_id: str | None = Form(None),
    current_user: User = Depends(require_permission("circulation.manage")),
    db: Session = Depends(get_db),
):
    try:
        audit = create_audit(
            db,
            {
                "audit_date": parse_optional_date(audit_date),
                "audit_type": audit_type.strip(),
                "financial_year": financial_year or None,
                "observations": observations or None,
                "suggestions": suggestions or None,
                "findings": findings or None,
                "recommendations": recommendations or None,
                "action_required": action_required or None,
                "action_taken": action_taken or None,
                "responsible_person": responsible_person or None,
                "status": status_value.strip() or "Open",
                "attachment_document_id": parse_optional_int(attachment_document_id, 0) or None,
            },
            current_user,
        )
        write_activity_log(db, request=request, action="AUDIT_ADDED", module="Audit", user=current_user, entity_name="AuditRecord", entity_id=str(audit.id), description=f"Added {audit_type} audit.")
        return RedirectResponse(url="/audits", status_code=status.HTTP_302_FOUND)
    except Exception as exc:
        records = db.scalars(select(AuditRecord).options(selectinload(AuditRecord.attachment)).order_by(AuditRecord.audit_date.desc())).all()
        return render(request, "phase8/audits.html", {"current_user": current_user, "records": records, "q": "", "documents": documents_for_select(db, "Audit evidence"), "error": str(exc)}, "audits", status.HTTP_400_BAD_REQUEST)


@router.get("/inventory", response_class=HTMLResponse)
def inventory_page(request: Request, q: str | None = None, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    statement = select(InventoryItem).order_by(InventoryItem.item_type, InventoryItem.item_name)
    if q:
        like = f"%{q.strip()}%"
        statement = statement.where(or_(InventoryItem.item_name.ilike(like), InventoryItem.item_type.ilike(like), InventoryItem.location.ilike(like), InventoryItem.condition.ilike(like)))
    return render(request, "phase8/inventory.html", {"current_user": current_user, "records": db.scalars(statement).all(), "q": q or "", "item_types": INVENTORY_TYPES, "error": None}, "inventory")


@router.post("/inventory")
def create_inventory_action(
    request: Request,
    item_name: str = Form(...),
    item_type: str = Form(...),
    quantity: str = Form("0"),
    available_quantity: str = Form("0"),
    damaged_quantity: str = Form("0"),
    condition: str | None = Form(None),
    location: str | None = Form(None),
    purchase_date: str | None = Form(None),
    price: str | None = Form(None),
    supplier: str | None = Form(None),
    remarks: str | None = Form(None),
    current_user: User = Depends(require_permission("circulation.manage")),
    db: Session = Depends(get_db),
):
    try:
        item = create_inventory_item(db, {"item_name": item_name.strip(), "item_type": item_type, "quantity": parse_optional_int(quantity), "available_quantity": parse_optional_int(available_quantity), "damaged_quantity": parse_optional_int(damaged_quantity), "condition": condition or None, "location": location or None, "purchase_date": parse_optional_date(purchase_date), "price": parse_optional_decimal(price), "supplier": supplier or None, "remarks": remarks or None})
        write_activity_log(db, request=request, action="INVENTORY_ADDED", module="Inventory", user=current_user, entity_name="InventoryItem", entity_id=str(item.id), description=f"Added inventory item {item.item_name}.")
        return RedirectResponse(url="/inventory", status_code=status.HTTP_302_FOUND)
    except Exception as exc:
        records = db.scalars(select(InventoryItem).order_by(InventoryItem.item_type, InventoryItem.item_name)).all()
        return render(request, "phase8/inventory.html", {"current_user": current_user, "records": records, "q": "", "item_types": INVENTORY_TYPES, "error": str(exc)}, "inventory", status.HTTP_400_BAD_REQUEST)


@router.get("/arrivals", response_class=HTMLResponse)
def arrivals_page(request: Request, q: str | None = None, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    statement = select(NewArrival).options(selectinload(NewArrival.category), selectinload(NewArrival.department_category), selectinload(NewArrival.invoice_document)).order_by(NewArrival.received_date.desc())
    if q:
        like = f"%{q.strip()}%"
        statement = statement.where(or_(NewArrival.arrival_number.ilike(like), NewArrival.title.ilike(like), NewArrival.material_type.ilike(like), NewArrival.invoice_number.ilike(like)))
    return render(request, "phase8/arrivals.html", {"current_user": current_user, "records": db.scalars(statement).all(), "q": q or "", "material_types": MATERIAL_TYPES, "categories": db.scalars(select(Category).order_by(Category.name)).all(), "departments": db.scalars(select(DepartmentCategory).order_by(DepartmentCategory.name)).all(), "documents": documents_for_select(db, "Invoices"), "error": None}, "arrivals")


@router.post("/arrivals")
def create_arrival_action(
    request: Request,
    arrival_number: str = Form(...),
    material_type: str = Form(...),
    title: str = Form(...),
    category_id: str | None = Form(None),
    department_category_id: str | None = Form(None),
    quantity: str = Form("1"),
    purchase_year: str | None = Form(None),
    purchase_month: str | None = Form(None),
    supplier: str | None = Form(None),
    invoice_number: str | None = Form(None),
    invoice_document_id: str | None = Form(None),
    received_date: str | None = Form(None),
    remarks: str | None = Form(None),
    current_user: User = Depends(require_permission("circulation.manage")),
    db: Session = Depends(get_db),
):
    try:
        arrival = create_arrival(db, {"arrival_number": arrival_number.strip(), "material_type": material_type, "title": title.strip(), "category_id": parse_optional_int(category_id, 0) or None, "department_category_id": parse_optional_int(department_category_id, 0) or None, "quantity": parse_optional_int(quantity, 1), "purchase_year": parse_optional_int(purchase_year, 0) or None, "purchase_month": purchase_month or None, "supplier": supplier or None, "invoice_number": invoice_number or None, "invoice_document_id": parse_optional_int(invoice_document_id, 0) or None, "received_date": parse_optional_date(received_date), "remarks": remarks or None})
        write_activity_log(db, request=request, action="ARRIVAL_ADDED", module="New Arrivals", user=current_user, entity_name="NewArrival", entity_id=str(arrival.id), description=f"Added {material_type}: {title}.")
        return RedirectResponse(url="/arrivals", status_code=status.HTTP_302_FOUND)
    except Exception as exc:
        records = db.scalars(select(NewArrival).options(selectinload(NewArrival.category), selectinload(NewArrival.department_category), selectinload(NewArrival.invoice_document)).order_by(NewArrival.received_date.desc())).all()
        return render(request, "phase8/arrivals.html", {"current_user": current_user, "records": records, "q": "", "material_types": MATERIAL_TYPES, "categories": db.scalars(select(Category).order_by(Category.name)).all(), "departments": db.scalars(select(DepartmentCategory).order_by(DepartmentCategory.name)).all(), "documents": documents_for_select(db, "Invoices"), "error": str(exc)}, "arrivals", status.HTTP_400_BAD_REQUEST)


@router.get("/documents", response_class=HTMLResponse)
def documents_page(request: Request, q: str | None = None, document_type: str | None = None, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    return render(request, "phase8/documents.html", {"current_user": current_user, "records": list_documents(db, q, document_type or None), "q": q or "", "document_type": document_type or "", "document_types": DOCUMENT_TYPES, "error": None}, "documents")


@router.post("/documents")
async def upload_document_action(
    request: Request,
    title: str = Form(...),
    document_type: str = Form(...),
    version: str = Form("1.0"),
    description: str | None = Form(None),
    category: str | None = Form(None),
    remarks: str | None = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission("circulation.manage")),
    db: Session = Depends(get_db),
):
    try:
        document = save_document_upload(db, upload=file, title=title, document_type=document_type, version=version, current_user=current_user, description=description, category=category, remarks=remarks)
        write_activity_log(db, request=request, action="DOCUMENT_UPLOADED", module="Documents", user=current_user, entity_name="Document", entity_id=str(document.id), description=f"Uploaded {document_type}: {title}.")
        return RedirectResponse(url="/documents", status_code=status.HTTP_302_FOUND)
    except Exception as exc:
        return render(request, "phase8/documents.html", {"current_user": current_user, "records": list_documents(db), "q": "", "document_type": "", "document_types": DOCUMENT_TYPES, "error": str(exc)}, "documents", status.HTTP_400_BAD_REQUEST)


@router.get("/documents/{document_id}/download")
def download_document(document_id: int, current_user: User = Depends(require_permission("circulation.manage")), db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if document is None or not document.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    path = document_file_path(document)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File missing on server.")
    return FileResponse(path, media_type=document.mime_type or "application/octet-stream", filename=document.original_filename)


@router.get("/phase8-reports", response_class=HTMLResponse)
def phase8_reports_page(request: Request, report_type: str = "visits", current_user: User = Depends(require_permission("reports.view")), db: Session = Depends(get_db)):
    result = report_data(db, report_type)
    return render(request, "phase8/reports.html", {"current_user": current_user, "report_types": PHASE8_REPORTS, "report_type": report_type, "result": result}, "phase8_reports")


@router.get("/phase8-reports/export/{fmt}")
def phase8_report_export(request: Request, fmt: str, report_type: str = "visits", current_user: User = Depends(require_permission("reports.view")), db: Session = Depends(get_db)):
    result = report_data(db, report_type)
    write_activity_log(db, request=request, action="PHASE8_REPORT_EXPORTED", module="Reports", user=current_user, entity_name="Report", entity_id=report_type, description=f"Exported {result.title} as {fmt}.")
    if fmt == "pdf":
        return Response(export_pdf(result), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{report_type}.pdf"'})
    if fmt == "excel":
        return Response(export_excel(result), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f'attachment; filename="{report_type}.xlsx"'})
    return Response(export_csv(result), media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="{report_type}.csv"'})
