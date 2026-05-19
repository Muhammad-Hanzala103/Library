from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    books: Mapped[list["BookMaster"]] = relationship(
        "BookMaster", secondary="bookauthors", back_populates="authors"
    )


class Publisher(Base):
    __tablename__ = "publishers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contact: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    books: Mapped[list["BookMaster"]] = relationship("BookMaster", back_populates="publisher")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    code: Mapped[str | None] = mapped_column(String(40), unique=True, nullable=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    books: Mapped[list["BookMaster"]] = relationship("BookMaster", back_populates="category")


class DepartmentCategory(Base):
    __tablename__ = "departmentcategories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    code: Mapped[str | None] = mapped_column(String(40), unique=True, nullable=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    books: Mapped[list["BookMaster"]] = relationship("BookMaster", back_populates="department_category")


class LiteratureCategory(Base):
    __tablename__ = "literaturecategories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    code: Mapped[str | None] = mapped_column(String(40), unique=True, nullable=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    books: Mapped[list["BookMaster"]] = relationship("BookMaster", back_populates="literature_category")


class BookAuthor(Base):
    __tablename__ = "bookauthors"
    __table_args__ = (UniqueConstraint("book_master_id", "author_id", name="uq_bookauthors_book_author"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    book_master_id: Mapped[int] = mapped_column(ForeignKey("bookmasters.id", ondelete="CASCADE"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="RESTRICT"), nullable=False)
    author_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class BookMaster(Base):
    __tablename__ = "bookmasters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    unique_title: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    subtitle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    publisher_id: Mapped[int | None] = mapped_column(ForeignKey("publishers.id", ondelete="SET NULL"), nullable=True)
    isbn: Mapped[str | None] = mapped_column(String(30), index=True, nullable=True)
    issn: Mapped[str | None] = mapped_column(String(30), index=True, nullable=True)
    source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    department_category_id: Mapped[int | None] = mapped_column(
        ForeignKey("departmentcategories.id", ondelete="SET NULL"), nullable=True
    )
    literature_category_id: Mapped[int | None] = mapped_column(
        ForeignKey("literaturecategories.id", ondelete="SET NULL"), nullable=True
    )
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    edition: Mapped[str | None] = mapped_column(String(80), nullable=True)
    publication_place: Mapped[str | None] = mapped_column(String(120), nullable=True)
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str | None] = mapped_column(String(80), nullable=True)
    format: Mapped[str | None] = mapped_column(String(80), nullable=True)
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    book_location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    rack: Mapped[str | None] = mapped_column(String(80), nullable=True)
    shelf: Mapped[str | None] = mapped_column(String(80), nullable=True)
    hall: Mapped[str | None] = mapped_column(String(80), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    book_image_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bill_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    store_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    supplier: Mapped[str | None] = mapped_column(String(150), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    deleted_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    deleted_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    publisher: Mapped[Publisher | None] = relationship("Publisher", back_populates="books")
    category: Mapped[Category | None] = relationship("Category", back_populates="books")
    department_category: Mapped[DepartmentCategory | None] = relationship(
        "DepartmentCategory", back_populates="books"
    )
    literature_category: Mapped[LiteratureCategory | None] = relationship(
        "LiteratureCategory", back_populates="books"
    )
    authors: Mapped[list[Author]] = relationship("Author", secondary="bookauthors", back_populates="books")
    copies: Mapped[list["BookCopy"]] = relationship("BookCopy", back_populates="book_master")


class BookCopy(Base):
    __tablename__ = "bookcopies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    accession_number: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    book_master_id: Mapped[int] = mapped_column(ForeignKey("bookmasters.id", ondelete="RESTRICT"), nullable=False)
    copy_number: Mapped[int] = mapped_column(Integer, nullable=False)
    barcode_value: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)
    rack: Mapped[str | None] = mapped_column(String(80), nullable=True)
    shelf: Mapped[str | None] = mapped_column(String(80), nullable=True)
    location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    hall: Mapped[str | None] = mapped_column(String(80), nullable=True)
    physical_condition: Mapped[str] = mapped_column(String(80), default="Good", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="Available", index=True, nullable=False)
    current_holder_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    current_holder_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last_issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_receive_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    deleted_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    deleted_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    book_master: Mapped[BookMaster] = relationship("BookMaster", back_populates="copies")

