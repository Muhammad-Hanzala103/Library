from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    document_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    version: Mapped[str] = mapped_column(String(40), default="1.0", nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    uploaded_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    uploaded_by = relationship("User")


class VisitRecord(Base):
    __tablename__ = "visitrecords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    visit_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    organization: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    visit_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    team_members: Mapped[str | None] = mapped_column(Text, nullable=True)
    department: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggestions: Mapped[str | None] = mapped_column(Text, nullable=True)
    findings: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(60), default="Open", index=True, nullable=False)
    attachment_document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    attachment = relationship("Document")
    created_by = relationship("User")


class AuditRecord(Base):
    __tablename__ = "auditrecords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    audit_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    audit_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    financial_year: Mapped[str | None] = mapped_column(String(30), index=True, nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggestions: Mapped[str | None] = mapped_column(Text, nullable=True)
    findings: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_required: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)
    responsible_person: Mapped[str | None] = mapped_column(String(150), nullable=True)
    status: Mapped[str] = mapped_column(String(60), default="Open", index=True, nullable=False)
    attachment_document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    attachment = relationship("Document")
    created_by = relationship("User")


class InventoryItem(Base):
    __tablename__ = "inventoryitems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    item_name: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    item_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    available_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    damaged_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    condition: Mapped[str | None] = mapped_column(String(80), index=True, nullable=True)
    location: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    supplier: Mapped[str | None] = mapped_column(String(150), nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class NewArrival(Base):
    __tablename__ = "newarrivals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    arrival_number: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    material_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    department_category_id: Mapped[int | None] = mapped_column(ForeignKey("departmentcategories.id", ondelete="SET NULL"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    purchase_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    purchase_month: Mapped[str | None] = mapped_column(String(20), nullable=True)
    supplier: Mapped[str | None] = mapped_column(String(150), nullable=True)
    invoice_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    invoice_document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    received_date: Mapped[date | None] = mapped_column(Date, index=True, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    category = relationship("Category")
    department_category = relationship("DepartmentCategory")
    invoice_document = relationship("Document")
