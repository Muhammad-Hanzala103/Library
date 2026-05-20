from datetime import date, datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select, or_
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.database import get_db
from app.models import (
    ActivityLog, BookCopy, BookMaster, DamagedBook, Employee, Fine,
    IssueRecord, LostBook, Permission, Reservation, Role, Student, User,
    NewArrival, Notification, AuditRecord, VisitRecord, InventoryItem,
    DepartmentCategory
)
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
    today = date.today()
    first_of_month = today.replace(day=1)
    first_of_year = today.replace(month=1, day=1)

    # 1. Compute 22 exact metrics
    metrics = {
        "users": db.scalar(select(func.count(User.id))) or 0,
        "roles": db.scalar(select(func.count(Role.id))) or 0,
        "permissions": db.scalar(select(func.count(Permission.id))) or 0,
        "activity_logs": db.scalar(select(func.count(ActivityLog.id))) or 0,
        
        "books": db.scalar(select(func.count(BookMaster.id)).where(BookMaster.is_deleted == False)) or 0,
        "copies": db.scalar(select(func.count(BookCopy.id)).where(BookCopy.is_deleted == False)) or 0,
        "available_copies": db.scalar(select(func.count(BookCopy.id)).where(BookCopy.status == "Available", BookCopy.is_deleted == False)) or 0,
        "issued_copies": db.scalar(select(func.count(BookCopy.id)).where(BookCopy.status == "Issued", BookCopy.is_deleted == False)) or 0,
        "reserved_books": db.scalar(select(func.count(Reservation.id)).where(Reservation.status.in_(["Waiting", "Ready for pickup"]))) or 0,
        "overdue_books": db.scalar(select(func.count(IssueRecord.id)).where(IssueRecord.status == "Active", IssueRecord.due_date < today)) or 0,
        "lost_books": db.scalar(select(func.count(LostBook.id)).where(LostBook.resolved_status == "Unresolved")) or 0,
        "damaged_books": db.scalar(select(func.count(DamagedBook.id)).where(DamagedBook.resolved_status == "Unresolved")) or 0,
        
        "students": db.scalar(select(func.count(Student.id))) or 0,
        "employees": db.scalar(select(func.count(Employee.id))) or 0,
        "students_cleared": db.scalar(select(func.count(Student.id)).where(Student.clearance_status == "Cleared")) or 0,
        "students_uncleared": db.scalar(select(func.count(Student.id)).where(Student.clearance_status != "Cleared")) or 0,
        
        "fine_collected_today": db.scalar(select(func.sum(Fine.paid_amount)).where(Fine.payment_date == today)) or Decimal("0.00"),
        "fine_collected_month": db.scalar(select(func.sum(Fine.paid_amount)).where(Fine.payment_date >= first_of_month)) or Decimal("0.00"),
        "new_arrivals_year": db.scalar(select(func.count(NewArrival.id)).where(NewArrival.received_date >= first_of_year)) or 0,
        "pending_reservations": db.scalar(select(func.count(Reservation.id)).where(Reservation.status == "Waiting")) or 0,
        "pending_notifications": db.scalar(select(func.count(Notification.id)).where(Notification.status == "Pending")) or 0,
        "audit_records": db.scalar(select(func.count(AuditRecord.id)).where(AuditRecord.status == "Open")) or 0,
        "visit_records": db.scalar(select(func.count(VisitRecord.id)).where(VisitRecord.status == "Open")) or 0,
        "inventory_items": db.scalar(select(func.sum(InventoryItem.quantity))) or 0,
    }

    # 2. Query Chart Aggregations
    # Chart 1: Monthly issue trend (count of active + returned issue records grouped by month, past 12 months)
    issue_trend_rows = db.execute(
        select(func.date_format(IssueRecord.issue_date, "%b %Y").label("month"), func.count(IssueRecord.id))
        .where(IssueRecord.issue_date >= today - timedelta(days=365))
        .group_by(func.date_format(IssueRecord.issue_date, "%Y-%m"), func.date_format(IssueRecord.issue_date, "%b %Y"))
        .order_by(func.date_format(IssueRecord.issue_date, "%Y-%m"))
    ).all()
    
    chart_issue_labels = [row[0] for row in issue_trend_rows]
    chart_issue_data = [row[1] for row in issue_trend_rows]

    # Chart 2: Department-wise books (Total books belonging to each department category)
    dept_books_rows = db.execute(
        select(DepartmentCategory.name, func.count(BookMaster.id))
        .join(BookMaster, BookMaster.department_category_id == DepartmentCategory.id)
        .where(BookMaster.is_deleted == False)
        .group_by(DepartmentCategory.name)
    ).all()
    chart_dept_labels = [row[0] for row in dept_books_rows]
    chart_dept_data = [row[1] for row in dept_books_rows]

    # Chart 3: CS vs CE (Specific comparison of Computer Science vs Computer Engineering department book copies)
    cs_books_count = db.scalar(select(func.count(BookCopy.id)).join(BookCopy.book_master).join(DepartmentCategory, BookMaster.department_category_id == DepartmentCategory.id).where(DepartmentCategory.name == "CS", BookCopy.is_deleted == False)) or 0
    ce_books_count = db.scalar(select(func.count(BookCopy.id)).join(BookCopy.book_master).join(DepartmentCategory, BookMaster.department_category_id == DepartmentCategory.id).where(DepartmentCategory.name == "CE", BookCopy.is_deleted == False)) or 0
    chart_cs_ce_labels = ["CS Department", "CE Department"]
    chart_cs_ce_data = [cs_books_count, ce_books_count]

    # Chart 4: Overdue trend (Number of active overdue issues grouped by due month)
    overdue_trend_rows = db.execute(
        select(func.date_format(IssueRecord.due_date, "%b %Y").label("month"), func.count(IssueRecord.id))
        .where(IssueRecord.status == "Active", IssueRecord.due_date < today)
        .group_by(func.date_format(IssueRecord.due_date, "%Y-%m"), func.date_format(IssueRecord.due_date, "%b %Y"))
        .order_by(func.date_format(IssueRecord.due_date, "%Y-%m"))
    ).all()
    chart_overdue_labels = [row[0] for row in overdue_trend_rows]
    chart_overdue_data = [row[1] for row in overdue_trend_rows]

    # Chart 5: Most issued books (Top 5 most issued book titles)
    most_issued_rows = db.execute(
        select(BookMaster.title, func.count(IssueRecord.id))
        .join(BookMaster, IssueRecord.book_master_id == BookMaster.id)
        .group_by(BookMaster.title)
        .order_by(func.count(IssueRecord.id).desc())
        .limit(5)
    ).all()
    chart_most_issued_labels = [row[0][:30] + "..." if len(row[0]) > 30 else row[0] for row in most_issued_rows]
    chart_most_issued_data = [row[1] for row in most_issued_rows]

    charts = {
        "issues": {"labels": chart_issue_labels, "data": chart_issue_data},
        "departments": {"labels": chart_dept_labels, "data": chart_dept_data},
        "cs_ce": {"labels": chart_cs_ce_labels, "data": chart_cs_ce_data},
        "overdues": {"labels": chart_overdue_labels, "data": chart_overdue_data},
        "most_issued": {"labels": chart_most_issued_labels, "data": chart_most_issued_data},
    }

    # 3. Collect real Quick Alerts
    # A. Active Overdue Holdings
    overdue_alerts = db.scalars(
        select(IssueRecord)
        .options(selectinload(IssueRecord.book_copy), selectinload(IssueRecord.book_master), selectinload(IssueRecord.student), selectinload(IssueRecord.employee))
        .where(IssueRecord.status == "Active", IssueRecord.due_date < today)
        .order_by(IssueRecord.due_date.asc())
        .limit(5)
    ).all()

    # B. Pending Reservations ready for pickup
    ready_reservations = db.scalars(
        select(Reservation)
        .options(selectinload(Reservation.book_master), selectinload(Reservation.student), selectinload(Reservation.employee))
        .where(Reservation.status == "Ready for pickup")
        .order_by(Reservation.expiry_date.asc())
        .limit(5)
    ).all()

    # C. Low Stock Accession Copies (Available Copies count = 0 or 1 for titles)
    # We can fetch copies that are damaged or lost, or book masters where total quantity <= 1
    low_stock = db.scalars(
        select(BookMaster)
        .where(BookMaster.quantity <= 1, BookMaster.is_deleted == False)
        .order_by(BookMaster.quantity.asc())
        .limit(5)
    ).all()

    # D. Unpaid or Partial Fines
    pending_fines = db.scalars(
        select(Fine)
        .options(selectinload(Fine.book_copy), selectinload(Fine.student), selectinload(Fine.employee))
        .where(Fine.payment_status.in_(["Unpaid", "Partial"]))
        .order_by(Fine.fine_amount.desc())
        .limit(5)
    ).all()

    alerts = {
        "overdues": overdue_alerts,
        "reservations": ready_reservations,
        "low_stock": low_stock,
        "fines": pending_fines,
    }

    # 4. Recent Activity Logs & User Information
    recent_logs = db.scalars(
        select(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
    ).all()
    
    permissions = get_user_permission_codes(current_user)

    return templates.TemplateResponse(
        "dashboard/index.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "current_user": current_user,
            "permissions": permissions,
            "metrics": metrics,
            "charts": charts,
            "alerts": alerts,
            "recent_logs": recent_logs,
        },
    )

