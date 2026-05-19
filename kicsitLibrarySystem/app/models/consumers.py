from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    registration_number: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    admission_number: Mapped[str | None] = mapped_column(String(80), unique=True, index=True, nullable=True)
    roll_number: Mapped[str | None] = mapped_column(String(80), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    father_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    department: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    program: Mapped[str | None] = mapped_column(String(120), nullable=True)
    semester: Mapped[str | None] = mapped_column(String(40), nullable=True)
    session: Mapped[str | None] = mapped_column(String(60), nullable=True)
    batch: Mapped[str | None] = mapped_column(String(60), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), index=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="Active", index=True, nullable=False)
    clearance_status: Mapped[str] = mapped_column(String(40), default="Not Cleared", index=True, nullable=False)
    clearance_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    clearance_remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_number: Mapped[str | None] = mapped_column(String(80), nullable=True)
    register_number: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    p_number: Mapped[str | None] = mapped_column(String(80), unique=True, index=True, nullable=True)
    cnic: Mapped[str | None] = mapped_column(String(30), unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    department: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    designation: Mapped[str | None] = mapped_column(String(120), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), index=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    employee_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    joining_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    leaving_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

