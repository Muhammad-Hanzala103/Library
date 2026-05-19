from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Employee, Student
from app.schemas.consumers import CLEARANCE_STATUSES, EMPLOYEE_TYPES, STUDENT_STATUSES, EmployeeForm, StudentForm


def clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def parse_date(value: str | None) -> date | None:
    value = clean_optional(value)
    return date.fromisoformat(value) if value else None


def checkbox_bool(value: str | None) -> bool:
    return value == "on"


def get_student_or_404(db: Session, student_id: int) -> Student:
    student = db.scalar(select(Student).where(Student.id == student_id))
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student


def get_employee_or_404(db: Session, employee_id: int) -> Employee:
    employee = db.scalar(select(Employee).where(Employee.id == employee_id))
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


def validate_student(form: StudentForm) -> None:
    if form.status not in STUDENT_STATUSES:
        raise ValueError("Invalid student status.")
    if form.clearance_status not in CLEARANCE_STATUSES:
        raise ValueError("Invalid clearance status.")
    if form.clearance_status == "Cleared" and form.clearance_date is None:
        raise ValueError("Clearance date is required when student is cleared.")


def validate_employee(form: EmployeeForm) -> None:
    if form.employee_type not in EMPLOYEE_TYPES:
        raise ValueError("Invalid employee type.")
    if form.employee_type in {"Permanent Faculty", "Permanent Staff"} and not form.p_number:
        raise ValueError("P Number is required for permanent employees.")
    if form.employee_type in {"Visiting Faculty", "Temporary Staff"} and not form.cnic:
        raise ValueError("CNIC is required for visiting faculty and temporary staff.")


def search_students(db: Session, query: str | None = None, status_value: str | None = None) -> list[Student]:
    statement = select(Student).order_by(Student.created_at.desc())
    query = clean_optional(query)
    status_value = clean_optional(status_value)
    if query:
        like = f"%{query}%"
        statement = statement.where(
            or_(
                Student.registration_number.ilike(like),
                Student.admission_number.ilike(like),
                Student.roll_number.ilike(like),
                Student.name.ilike(like),
                Student.father_name.ilike(like),
                Student.phone.ilike(like),
                Student.email.ilike(like),
            )
        )
    if status_value:
        statement = statement.where(Student.status == status_value)
    return db.scalars(statement).all()


def search_employees(db: Session, query: str | None = None, employee_type: str | None = None) -> list[Employee]:
    statement = select(Employee).order_by(Employee.created_at.desc())
    query = clean_optional(query)
    employee_type = clean_optional(employee_type)
    if query:
        like = f"%{query}%"
        statement = statement.where(
            or_(
                Employee.p_number.ilike(like),
                Employee.cnic.ilike(like),
                Employee.name.ilike(like),
                Employee.phone.ilike(like),
                Employee.email.ilike(like),
                Employee.department.ilike(like),
                Employee.designation.ilike(like),
            )
        )
    if employee_type:
        statement = statement.where(Employee.employee_type == employee_type)
    return db.scalars(statement).all()


def create_student(db: Session, form: StudentForm) -> Student:
    validate_student(form)
    student = Student(**form.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def update_student(db: Session, student: Student, form: StudentForm) -> Student:
    validate_student(form)
    for key, value in form.model_dump().items():
        setattr(student, key, value)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def create_employee(db: Session, form: EmployeeForm) -> Employee:
    validate_employee(form)
    employee = Employee(**form.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def update_employee(db: Session, employee: Employee, form: EmployeeForm) -> Employee:
    validate_employee(form)
    for key, value in form.model_dump().items():
        setattr(employee, key, value)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

