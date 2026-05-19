from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class ReferenceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    code: str | None = Field(default=None, max_length=40)
    description: str | None = Field(default=None, max_length=255)


class PublisherCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    contact: str | None = Field(default=None, max_length=120)


class BookMasterForm(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    unique_title: str | None = Field(default=None, max_length=255)
    subtitle: str | None = Field(default=None, max_length=255)
    publisher_id: int | None = None
    author_ids: list[int] = []
    isbn: str | None = Field(default=None, max_length=30)
    issn: str | None = Field(default=None, max_length=30)
    source: str | None = Field(default=None, max_length=120)
    department_category_id: int | None = None
    literature_category_id: int | None = None
    category_id: int | None = None
    edition: str | None = Field(default=None, max_length=80)
    publication_place: str | None = Field(default=None, max_length=120)
    publication_year: int | None = None
    language: str | None = Field(default=None, max_length=80)
    format: str | None = Field(default=None, max_length=80)
    keywords: str | None = None
    notes: str | None = None
    price: Decimal | None = None
    book_location: str | None = Field(default=None, max_length=120)
    rack: str | None = Field(default=None, max_length=80)
    shelf: str | None = Field(default=None, max_length=80)
    hall: str | None = Field(default=None, max_length=80)
    description: str | None = None
    bill_number: str | None = Field(default=None, max_length=120)
    store_name: str | None = Field(default=None, max_length=150)
    purchase_date: date | None = None
    supplier: str | None = Field(default=None, max_length=150)


class BookCopyForm(BaseModel):
    book_master_id: int
    accession_number: str = Field(min_length=1, max_length=80)
    copy_number: int = Field(ge=1)
    barcode_value: str | None = Field(default=None, max_length=120)
    rack: str | None = Field(default=None, max_length=80)
    shelf: str | None = Field(default=None, max_length=80)
    location: str | None = Field(default=None, max_length=120)
    hall: str | None = Field(default=None, max_length=80)
    physical_condition: str = Field(default="Good", max_length=80)
    status: str = Field(default="Available", max_length=40)

