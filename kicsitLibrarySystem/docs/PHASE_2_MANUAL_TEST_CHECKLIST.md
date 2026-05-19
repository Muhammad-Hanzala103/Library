# Phase 2 Manual Test Checklist

Run this after Phase 1 setup and after applying the Phase 2 migration.

## Commands

```powershell
cd d:\Project\Library\kicsitLibrarySystem
.\.venv\Scripts\Activate.ps1
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/login
```

Use `superadmin` or `librarian` with password `ChangeMe@123`.

## Catalog Setup

1. Open `Catalog Setup`.
2. Add one author.
3. Add one publisher.
4. Confirm default categories exist: Programming, Artificial Intelligence, Networking, Database, CS, CE, Urdu, English, History, and Islam.

## Add New Book

1. Open `Library Catalog`.
2. Click `Add New Book`.
3. Enter title, unique title, author, publisher, ISBN, department category, category, location, rack, shelf, and hall.
4. Upload a JPG or PNG book image.
5. Save the book.
6. Confirm the View Book page opens.
7. Confirm the book appears in Manage Books.

## Book Copies

1. Open `Book Copies`.
2. Select the new book.
3. Add accession number `KICSIT-TEST-001`.
4. Confirm the copy appears in the accession register.
5. Add the same accession number again.
6. Confirm duplicate accession is blocked.

## Search

1. Search Manage Books by title.
2. Search Manage Books by author.
3. Search Manage Books by ISBN.
4. Search Manage Books by accession number.
5. Search Book Copies by accession number, rack, shelf, or title.

## Edit Book

1. Open a book.
2. Click `Edit`.
3. Change rack, shelf, hall, or category.
4. Save.
5. Confirm updated values appear on View Book.

## Delete Book with Reason

1. Open a book.
2. Click `Delete`.
3. Submit without reason and confirm validation blocks it.
4. Enter a reason and delete.
5. Confirm the book no longer appears in Manage Books.
6. Confirm an activity log row exists for delete.

## Import Template

1. Open `Library Catalog`.
2. Click `Import Template`.
3. Confirm CSV file downloads with catalog import columns.

