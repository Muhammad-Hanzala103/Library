# Phase 5 Manual Test Checklist

Run after applying migrations and seed data.

## Commands

```powershell
cd d:\Project\Library\kicsitLibrarySystem
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

## Reservations

1. Open `Reservations`.
2. Create a reservation for a student or employee and a book.
3. Confirm queue position is assigned.
4. Mark reservation `Ready`.
5. Confirm an email notification record is created.
6. Complete a reservation.
7. Cancel a reservation with reason.

## Overdue

1. Issue a book with due date before today.
2. Open `Overdue`.
3. Confirm the book appears with overdue days and calculated fine.
4. Search by accession, title, or consumer.
5. Click Email reminder and confirm notification record is created.
6. Click WhatsApp reminder and confirm placeholder notification record is created.
7. Export PDF.
8. Export Excel.

## Unpaid Fines

1. Return a book overdue with fine status `Unpaid`.
2. Open `Unpaid Fines`.
3. Confirm fine appears.
4. Mark fine paid.
5. Confirm fine disappears from unpaid list.

## Lost Books

1. Issue a book.
2. Open `Lost Books`.
3. Enter accession number, lost date, fine amount, and payment status.
4. Submit.
5. Confirm lost case appears.
6. Confirm book copy status becomes `Lost`.
7. Confirm lost fine appears when payment status is unpaid.

## Damaged Books

1. Issue a book.
2. Open `Damaged Books`.
3. Enter accession number, damage level, repair cost, and remarks.
4. Submit.
5. Confirm damaged case appears.
6. Confirm book copy status becomes `Damaged`.
7. Confirm damage fine appears when repair cost is greater than zero.

## Activity Logs

1. Confirm `RESERVATION_CREATED`.
2. Confirm `SEND_OVERDUE_REMINDER`.
3. Confirm `FINE_PAID`.
4. Confirm `MARK_LOST`.
5. Confirm `MARK_DAMAGED`.

