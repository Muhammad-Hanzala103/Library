# QA Installation Guide

```powershell
cd C:\Projects\Library-1\kicsitLibrarySystem
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Install and start MySQL Server, then create the database:

```sql
CREATE DATABASE kicsit_library CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Ensure `mysql.exe` and `mysqldump.exe` are on PATH for backup/restore.

Run:

```powershell
alembic upgrade head
python -m app.seed
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/login`.

QA note: In this audit, MySQL refused connections on `127.0.0.1:3306`, so migration and seed could not complete.

