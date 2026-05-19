from datetime import date

from pydantic import BaseModel, Field


STUDENT_STATUSES = {"Active", "Blocked", "Graduated", "Cleared", "Not Cleared"}
CLEARANCE_STATUSES = {"Cleared", "Not Cleared"}
EMPLOYEE_TYPES = {"Permanent Faculty", "Visiting Faculty", "Permanent Staff", "Temporary Staff"}


class StudentForm(BaseModel):
    registration_number: str = Field(min_length=1, max_length=80)
    admission_number: str | None = Field(default=None, max_length=80)
    roll_number: str | None = Field(default=None, max_length=80)
    name: str = Field(min_length=1, max_length=150)
    father_name: str | None = Field(default=None, max_length=150)
    department: str | None = Field(default=None, max_length=120)
    program: str | None = Field(default=None, max_length=120)
    semester: str | None = Field(default=None, max_length=40)
    session: str | None = Field(default=None, max_length=60)
    batch: str | None = Field(default=None, max_length=60)
    phone: str | None = Field(default=None, max_length=40)
    email: str | None = Field(default=None, max_length=255)
    status: str = Field(default="Active", max_length=40)
    clearance_status: str = Field(default="Not Cleared", max_length=40)
    clearance_date: date | None = None
    clearance_remarks: str | None = None
    page_number: str | None = Field(default=None, max_length=80)
    register_number: str | None = Field(default=None, max_length=80)
    is_active: bool = True


class EmployeeForm(BaseModel):
    p_number: str | None = Field(default=None, max_length=80)
    cnic: str | None = Field(default=None, max_length=30)
    name: str = Field(min_length=1, max_length=150)
    department: str | None = Field(default=None, max_length=120)
    designation: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    email: str | None = Field(default=None, max_length=255)
    employee_type: str = Field(max_length=50)
    is_active: bool = True
    joining_date: date | None = None
    leaving_date: date | None = None
    remarks: str | None = None

