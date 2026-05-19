from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    reservation_number: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    consumer_type: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("students.id", ondelete="SET NULL"), index=True, nullable=True)
    employee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id", ondelete="SET NULL"), index=True, nullable=True)
    book_master_id: Mapped[int] = mapped_column(ForeignKey("bookmasters.id", ondelete="RESTRICT"), index=True, nullable=False)
    book_copy_id: Mapped[int | None] = mapped_column(ForeignKey("bookcopies.id", ondelete="SET NULL"), index=True, nullable=True)
    reservation_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    queue_position: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="Waiting", index=True, nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancelled_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    student = relationship("Student")
    employee = relationship("Employee")
    book_master = relationship("BookMaster")
    book_copy = relationship("BookCopy")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    consumer_type: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("students.id", ondelete="SET NULL"), index=True, nullable=True)
    employee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id", ondelete="SET NULL"), index=True, nullable=True)
    notification_type: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    channel: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    subject: Mapped[str] = mapped_column(String(180), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="Pending", index=True, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    whatsapp_placeholder: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    student = relationship("Student")
    employee = relationship("Employee")


class LostBook(Base):
    __tablename__ = "lostbooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lost_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    issue_record_id: Mapped[int | None] = mapped_column(ForeignKey("issuerecords.id", ondelete="SET NULL"), index=True, nullable=True)
    book_copy_id: Mapped[int] = mapped_column(ForeignKey("bookcopies.id", ondelete="RESTRICT"), index=True, nullable=False)
    consumer_type: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("students.id", ondelete="SET NULL"), index=True, nullable=True)
    employee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id", ondelete="SET NULL"), index=True, nullable=True)
    fine_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    payment_status: Mapped[str] = mapped_column(String(40), default="Unpaid", index=True, nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_status: Mapped[str] = mapped_column(String(40), default="Unresolved", index=True, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    issue_record = relationship("IssueRecord")
    book_copy = relationship("BookCopy")
    student = relationship("Student")
    employee = relationship("Employee")


class DamagedBook(Base):
    __tablename__ = "damagedbooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    damage_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    issue_record_id: Mapped[int | None] = mapped_column(ForeignKey("issuerecords.id", ondelete="SET NULL"), index=True, nullable=True)
    book_copy_id: Mapped[int] = mapped_column(ForeignKey("bookcopies.id", ondelete="RESTRICT"), index=True, nullable=False)
    consumer_type: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("students.id", ondelete="SET NULL"), index=True, nullable=True)
    employee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id", ondelete="SET NULL"), index=True, nullable=True)
    damage_level: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    repair_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_status: Mapped[str] = mapped_column(String(40), default="Unresolved", index=True, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    issue_record = relationship("IssueRecord")
    book_copy = relationship("BookCopy")
    student = relationship("Student")
    employee = relationship("Employee")

