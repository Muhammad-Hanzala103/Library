from datetime import date

from pydantic import BaseModel, Field


CONSUMER_TYPES = {"Student", "Employee"}
RETURN_CONDITIONS = {"Normal", "Damaged", "Lost"}
FINE_STATUSES = {"Paid", "Unpaid"}


class IssueBookForm(BaseModel):
    consumer_type: str
    consumer_query: str = Field(min_length=1, max_length=150)
    accession_number: str = Field(min_length=1, max_length=80)
    issue_date: date
    due_date: date
    remarks: str | None = None


class ReturnBookForm(BaseModel):
    accession_number: str = Field(min_length=1, max_length=80)
    receive_date: date
    book_condition: str = "Normal"
    fine_collected_status: str = "Unpaid"
    remarks: str | None = None

