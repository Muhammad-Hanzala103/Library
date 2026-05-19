from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.permissions import require_permission
from app.schemas.consumers import EMPLOYEE_TYPES, STUDENT_STATUSES, EmployeeForm, StudentForm
from app.services.activity_log_service import write_activity_log
from app.services.consumer_service import (
    checkbox_bool,
    clean_optional,
    create_employee,
    create_student,
    get_employee_or_404,
    get_student_or_404,
    parse_date,
    search_employees,
    search_students,
    update_employee,
    update_student,
)


router = APIRouter(prefix="/consumers", tags=["Consumers"])
templates = Jinja2Templates(directory="app/templates")


def render(request: Request, template: str, context: dict, status_code: int = status.HTTP_200_OK) -> HTMLResponse:
    settings = get_settings()
    base = {"request": request, "app_name": settings.app_name, "active_nav": "consumers"}
    base.update(context)
    return templates.TemplateResponse(template, base, status_code=status_code)


def build_student_form(
    registration_number: str,
    admission_number: str | None,
    roll_number: str | None,
    name: str,
    father_name: str | None,
    department: str | None,
    program: str | None,
    semester: str | None,
    session: str | None,
    batch: str | None,
    phone: str | None,
    email: str | None,
    status_value: str,
    clearance_status: str,
    clearance_date: str | None,
    clearance_remarks: str | None,
    page_number: str | None,
    register_number: str | None,
    is_active: str | None,
) -> StudentForm:
    return StudentForm(
        registration_number=registration_number.strip(),
        admission_number=clean_optional(admission_number),
        roll_number=clean_optional(roll_number),
        name=name.strip(),
        father_name=clean_optional(father_name),
        department=clean_optional(department),
        program=clean_optional(program),
        semester=clean_optional(semester),
        session=clean_optional(session),
        batch=clean_optional(batch),
        phone=clean_optional(phone),
        email=clean_optional(email),
        status=status_value,
        clearance_status=clearance_status,
        clearance_date=parse_date(clearance_date),
        clearance_remarks=clean_optional(clearance_remarks),
        page_number=clean_optional(page_number),
        register_number=clean_optional(register_number),
        is_active=checkbox_bool(is_active),
    )


def build_employee_form(
    p_number: str | None,
    cnic: str | None,
    name: str,
    department: str | None,
    designation: str | None,
    phone: str | None,
    email: str | None,
    employee_type: str,
    is_active: str | None,
    joining_date: str | None,
    leaving_date: str | None,
    remarks: str | None,
) -> EmployeeForm:
    return EmployeeForm(
        p_number=clean_optional(p_number),
        cnic=clean_optional(cnic),
        name=name.strip(),
        department=clean_optional(department),
        designation=clean_optional(designation),
        phone=clean_optional(phone),
        email=clean_optional(email),
        employee_type=employee_type,
        is_active=checkbox_bool(is_active),
        joining_date=parse_date(joining_date),
        leaving_date=parse_date(leaving_date),
        remarks=clean_optional(remarks),
    )


@router.get("/students", response_class=HTMLResponse)
def students_index(
    request: Request,
    q: str | None = None,
    status_filter: str | None = None,
    current_user: User = Depends(require_permission("consumers.manage")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    students = search_students(db, q, status_filter)
    return render(
        request,
        "consumers/students.html",
        {
            "current_user": current_user,
            "students": students,
            "q": q or "",
            "status_filter": status_filter or "",
            "student_statuses": sorted(STUDENT_STATUSES),
        },
    )


@router.get("/students/new", response_class=HTMLResponse)
def new_student_page(
    request: Request,
    current_user: User = Depends(require_permission("consumers.manage")),
) -> HTMLResponse:
    return render(
        request,
        "consumers/student_form.html",
        {"current_user": current_user, "student": None, "mode": "create", "error": None, "student_statuses": sorted(STUDENT_STATUSES)},
    )


@router.post("/students/new")
def create_student_action(
    request: Request,
    registration_number: str = Form(...),
    admission_number: str | None = Form(None),
    roll_number: str | None = Form(None),
    name: str = Form(...),
    father_name: str | None = Form(None),
    department: str | None = Form(None),
    program: str | None = Form(None),
    semester: str | None = Form(None),
    session: str | None = Form(None),
    batch: str | None = Form(None),
    phone: str | None = Form(None),
    email: str | None = Form(None),
    status_value: str = Form("Active"),
    clearance_status: str = Form("Not Cleared"),
    clearance_date: str | None = Form(None),
    clearance_remarks: str | None = Form(None),
    page_number: str | None = Form(None),
    register_number: str | None = Form(None),
    is_active: str | None = Form(None),
    current_user: User = Depends(require_permission("consumers.manage")),
    db: Session = Depends(get_db),
):
    try:
        form = build_student_form(
            registration_number, admission_number, roll_number, name, father_name, department, program,
            semester, session, batch, phone, email, status_value, clearance_status, clearance_date,
            clearance_remarks, page_number, register_number, is_active,
        )
        student = create_student(db, form)
        write_activity_log(db, request=request, action="ADD_STUDENT", module="Consumers", user=current_user, entity_name="Student", entity_id=str(student.id), description=f"Added student: {student.registration_number}")
        return RedirectResponse(url=f"/consumers/students/{student.id}", status_code=status.HTTP_302_FOUND)
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        return render(request, "consumers/student_form.html", {"current_user": current_user, "student": None, "mode": "create", "error": str(exc), "student_statuses": sorted(STUDENT_STATUSES)}, status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/students/{student_id}", response_class=HTMLResponse)
def student_profile(request: Request, student_id: int, current_user: User = Depends(require_permission("consumers.manage")), db: Session = Depends(get_db)) -> HTMLResponse:
    student = get_student_or_404(db, student_id)
    return render(request, "consumers/student_profile.html", {"current_user": current_user, "student": student})


@router.get("/students/{student_id}/edit", response_class=HTMLResponse)
def edit_student_page(request: Request, student_id: int, current_user: User = Depends(require_permission("consumers.manage")), db: Session = Depends(get_db)) -> HTMLResponse:
    student = get_student_or_404(db, student_id)
    return render(request, "consumers/student_form.html", {"current_user": current_user, "student": student, "mode": "edit", "error": None, "student_statuses": sorted(STUDENT_STATUSES)})


@router.post("/students/{student_id}/edit")
def edit_student_action(
    request: Request,
    student_id: int,
    registration_number: str = Form(...),
    admission_number: str | None = Form(None),
    roll_number: str | None = Form(None),
    name: str = Form(...),
    father_name: str | None = Form(None),
    department: str | None = Form(None),
    program: str | None = Form(None),
    semester: str | None = Form(None),
    session: str | None = Form(None),
    batch: str | None = Form(None),
    phone: str | None = Form(None),
    email: str | None = Form(None),
    status_value: str = Form("Active"),
    clearance_status: str = Form("Not Cleared"),
    clearance_date: str | None = Form(None),
    clearance_remarks: str | None = Form(None),
    page_number: str | None = Form(None),
    register_number: str | None = Form(None),
    is_active: str | None = Form(None),
    current_user: User = Depends(require_permission("consumers.manage")),
    db: Session = Depends(get_db),
):
    student = get_student_or_404(db, student_id)
    try:
        form = build_student_form(
            registration_number, admission_number, roll_number, name, father_name, department, program,
            semester, session, batch, phone, email, status_value, clearance_status, clearance_date,
            clearance_remarks, page_number, register_number, is_active,
        )
        update_student(db, student, form)
        write_activity_log(db, request=request, action="EDIT_STUDENT", module="Consumers", user=current_user, entity_name="Student", entity_id=str(student.id), description=f"Edited student: {student.registration_number}")
        return RedirectResponse(url=f"/consumers/students/{student.id}", status_code=status.HTTP_302_FOUND)
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        return render(request, "consumers/student_form.html", {"current_user": current_user, "student": student, "mode": "edit", "error": str(exc), "student_statuses": sorted(STUDENT_STATUSES)}, status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/employees", response_class=HTMLResponse)
def employees_index(
    request: Request,
    q: str | None = None,
    employee_type: str | None = None,
    current_user: User = Depends(require_permission("consumers.manage")),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    employees = search_employees(db, q, employee_type)
    return render(request, "consumers/employees.html", {"current_user": current_user, "employees": employees, "q": q or "", "employee_type": employee_type or "", "employee_types": sorted(EMPLOYEE_TYPES)})


@router.get("/employees/new", response_class=HTMLResponse)
def new_employee_page(request: Request, current_user: User = Depends(require_permission("consumers.manage"))) -> HTMLResponse:
    return render(request, "consumers/employee_form.html", {"current_user": current_user, "employee": None, "mode": "create", "error": None, "employee_types": sorted(EMPLOYEE_TYPES)})


@router.post("/employees/new")
def create_employee_action(
    request: Request,
    p_number: str | None = Form(None),
    cnic: str | None = Form(None),
    name: str = Form(...),
    department: str | None = Form(None),
    designation: str | None = Form(None),
    phone: str | None = Form(None),
    email: str | None = Form(None),
    employee_type: str = Form(...),
    is_active: str | None = Form(None),
    joining_date: str | None = Form(None),
    leaving_date: str | None = Form(None),
    remarks: str | None = Form(None),
    current_user: User = Depends(require_permission("consumers.manage")),
    db: Session = Depends(get_db),
):
    try:
        form = build_employee_form(p_number, cnic, name, department, designation, phone, email, employee_type, is_active, joining_date, leaving_date, remarks)
        employee = create_employee(db, form)
        write_activity_log(db, request=request, action="ADD_EMPLOYEE", module="Consumers", user=current_user, entity_name="Employee", entity_id=str(employee.id), description=f"Added employee: {employee.name}")
        return RedirectResponse(url=f"/consumers/employees/{employee.id}", status_code=status.HTTP_302_FOUND)
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        return render(request, "consumers/employee_form.html", {"current_user": current_user, "employee": None, "mode": "create", "error": str(exc), "employee_types": sorted(EMPLOYEE_TYPES)}, status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/employees/{employee_id}", response_class=HTMLResponse)
def employee_profile(request: Request, employee_id: int, current_user: User = Depends(require_permission("consumers.manage")), db: Session = Depends(get_db)) -> HTMLResponse:
    employee = get_employee_or_404(db, employee_id)
    return render(request, "consumers/employee_profile.html", {"current_user": current_user, "employee": employee})


@router.get("/employees/{employee_id}/edit", response_class=HTMLResponse)
def edit_employee_page(request: Request, employee_id: int, current_user: User = Depends(require_permission("consumers.manage")), db: Session = Depends(get_db)) -> HTMLResponse:
    employee = get_employee_or_404(db, employee_id)
    return render(request, "consumers/employee_form.html", {"current_user": current_user, "employee": employee, "mode": "edit", "error": None, "employee_types": sorted(EMPLOYEE_TYPES)})


@router.post("/employees/{employee_id}/edit")
def edit_employee_action(
    request: Request,
    employee_id: int,
    p_number: str | None = Form(None),
    cnic: str | None = Form(None),
    name: str = Form(...),
    department: str | None = Form(None),
    designation: str | None = Form(None),
    phone: str | None = Form(None),
    email: str | None = Form(None),
    employee_type: str = Form(...),
    is_active: str | None = Form(None),
    joining_date: str | None = Form(None),
    leaving_date: str | None = Form(None),
    remarks: str | None = Form(None),
    current_user: User = Depends(require_permission("consumers.manage")),
    db: Session = Depends(get_db),
):
    employee = get_employee_or_404(db, employee_id)
    try:
        form = build_employee_form(p_number, cnic, name, department, designation, phone, email, employee_type, is_active, joining_date, leaving_date, remarks)
        update_employee(db, employee, form)
        write_activity_log(db, request=request, action="EDIT_EMPLOYEE", module="Consumers", user=current_user, entity_name="Employee", entity_id=str(employee.id), description=f"Edited employee: {employee.name}")
        return RedirectResponse(url=f"/consumers/employees/{employee.id}", status_code=status.HTTP_302_FOUND)
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        return render(request, "consumers/employee_form.html", {"current_user": current_user, "employee": employee, "mode": "edit", "error": str(exc), "employee_types": sorted(EMPLOYEE_TYPES)}, status_code=status.HTTP_400_BAD_REQUEST)

