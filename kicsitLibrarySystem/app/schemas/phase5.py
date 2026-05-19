from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


RESERVATION_STATUSES = {"Waiting", "Ready for pickup", "Completed", "Cancelled", "Expired"}
DAMAGE_LEVELS = {"Minor", "Major", "Repairable", "Discarded"}


class ReservationForm(BaseModel):
    consumer_type: str
    consumer_query: str = Field(min_length=1, max_length=150)
    book_master_id: int
    book_copy_id: int | None = None
    reservation_date: date
    expiry_date: date
    remarks: str | None = None


class LostBookForm(BaseModel):
    accession_number: str = Field(min_length=1, max_length=80)
    lost_date: date
    fine_amount: Decimal = Decimal("0.00")
    payment_status: str = "Unpaid"
    remarks: str | None = None


class DamagedBookForm(BaseModel):
    accession_number: str = Field(min_length=1, max_length=80)
    damage_date: date
    damage_level: str
    repair_cost: Decimal = Decimal("0.00")
    remarks: str | None = None

