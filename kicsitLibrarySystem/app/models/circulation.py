from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IssueRecord(Base):
    __tablename__ = "issuerecords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    issue_number: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    book_copy_id: Mapped[int] = mapped_column(ForeignKey("bookcopies.id", ondelete="RESTRICT"), index=True, nullable=False)
    book_master_id: Mapped[int] = mapped_column(ForeignKey("bookmasters.id", ondelete="RESTRICT"), index=True, nullable=False)
    consumer_type: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("students.id", ondelete="RESTRICT"), index=True, nullable=True)
    employee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id", ondelete="RESTRICT"), index=True, nullable=True)
    issue_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="Active", index=True, nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    issued_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    book_copy = relationship("BookCopy")
    book_master = relationship("BookMaster")
    student = relationship("Student")
    employee = relationship("Employee")
    receive_record = relationship("ReceiveRecord", back_populates="issue_record", uselist=False)
    fines = relationship("Fine", back_populates="issue_record")


class ReceiveRecord(Base):
    __tablename__ = "receiverecords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    receive_number: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    issue_record_id: Mapped[int] = mapped_column(ForeignKey("issuerecords.id", ondelete="RESTRICT"), unique=True, nullable=False)
    book_copy_id: Mapped[int] = mapped_column(ForeignKey("bookcopies.id", ondelete="RESTRICT"), index=True, nullable=False)
    receive_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    book_condition: Mapped[str] = mapped_column(String(80), nullable=False)
    overdue_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    calculated_fine_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    fine_collected_status: Mapped[str] = mapped_column(String(40), default="Unpaid", nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    issue_record = relationship("IssueRecord", back_populates="receive_record")
    book_copy = relationship("BookCopy")


class Fine(Base):
    __tablename__ = "fines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fine_number: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    issue_record_id: Mapped[int | None] = mapped_column(ForeignKey("issuerecords.id", ondelete="SET NULL"), index=True, nullable=True)
    receive_record_id: Mapped[int | None] = mapped_column(ForeignKey("receiverecords.id", ondelete="SET NULL"), index=True, nullable=True)
    book_copy_id: Mapped[int | None] = mapped_column(ForeignKey("bookcopies.id", ondelete="SET NULL"), index=True, nullable=True)
    consumer_type: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("students.id", ondelete="SET NULL"), index=True, nullable=True)
    employee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id", ondelete="SET NULL"), index=True, nullable=True)
    fine_type: Mapped[str] = mapped_column(String(40), default="Overdue", nullable=False)
    fine_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    remaining_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(40), default="Unpaid", index=True, nullable=False)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    collected_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    waiver_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    issue_record = relationship("IssueRecord", back_populates="fines")
    receive_record = relationship("ReceiveRecord")
    book_copy = relationship("BookCopy")
    student = relationship("Student")
    employee = relationship("Employee")

