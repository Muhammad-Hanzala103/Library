# Fixed Issues Report

| ID | Issue | Files | Retest |
|---|---|---|---|
| FIX-001 | FastAPI startup failed due invalid response union annotations | `app/routers/auth.py`, `app/routers/catalog.py`, `app/routers/circulation.py` | `from app.main import app` passes; Uvicorn smoke passes |
| FIX-002 | Password hashing failed with bcrypt 5 | `requirements.txt` | `pytest` password hash test passes |
| FIX-003 | Active issued copies could be soft-deleted | `app/services/catalog_service.py`, `app/routers/catalog.py` | Static guard verified |
| FIX-004 | Overdue reports ignored configured fine rate | `app/services/phase5_service.py`, `app/routers/phase5.py`, `app/services/phase7_service.py` | Static calls verified |
| FIX-005 | Backup restore confirmation was client-only | `app/routers/backup.py`, `app/templates/backup/index.html` | Server-side confirmation check verified |
| FIX-006 | Backup password was exposed in command arguments | `app/services/backup_service.py` | Password now passed via `MYSQL_PWD` env |
| FIX-007 | Import route accepted unsupported files without explicit checks | `app/routers/phase7.py` | Upload validation smoke coverage added |
| FIX-008 | Sidebar displayed links without permission checks | `app/templates/base.html` | Template guards verified |

