# Bug Report

| Bug ID | Module | Screen/API | Expected | Actual | Severity | Root cause | File changed | Fix summary | Retest |
|---|---|---|---|---|---|---|---|---|---|
| BUG-001 | Startup | App import/server | App imports | FastAPI route annotation crash before fix | Critical | Response-class union annotations were treated as response models | `app/routers/auth.py`, `app/routers/catalog.py`, `app/routers/circulation.py` | Invalid route return unions removed | Pass |
| BUG-002 | Authentication | Password hashing | Hash works | bcrypt/passlib incompatibility before fix | Critical | Unpinned bcrypt 5 incompatible with passlib 1.7.4 | `requirements.txt` | Pinned `bcrypt==4.2.1` | Pass |
| BUG-003 | Setup | Alembic migration | DB reachable and migrations apply | MySQL refused connection | Critical | Local MySQL service unavailable | None | Environment blocker | Fail |
| BUG-004 | Backup | Restore | Restore requires server-side confirmation | Client-only confirmation was bypassable before fix | Critical | Restore route did not validate confirmation text | `app/routers/backup.py`, `app/templates/backup/index.html` | Added server-side `CONFIRM RESTORE` validation | Static pass |
| BUG-005 | Catalog | Delete book/copy | Active issued copies cannot be deleted | Could corrupt issue state before fix | Critical | Delete path lacked active issue guard | `app/services/catalog_service.py`, `app/routers/catalog.py` | Added active issue checks and clean error handling | Static pass |
| BUG-006 | Reports | Overdue fine | Uses configured fine-per-day | Report calculations used hardcoded value before fix | Major | Report code ignored settings | `app/services/phase5_service.py`, `app/routers/phase5.py`, `app/services/phase7_service.py` | Uses `circulation.fine_per_day` | Static pass |
| BUG-007 | Import | CSV upload | Reject wrong/empty/large files | Import trusted raw upload before fix | Major | Missing upload validation | `app/routers/phase7.py` | Added extension, empty-file, and size checks | Smoke pass |
| BUG-008 | UI permissions | Sidebar | Restricted links hidden | Sidebar exposed broad links before fix | Major | Template lacked permission guards | `app/templates/base.html` | Added permission-gated navigation | Static pass |
| BUG-009 | Roles | Seed | All required demo roles/users seeded | Only 4 roles/users before fix | Major | Seed data did not cover full QA role matrix | `app/seed.py`, `tests/test_final_qa_smoke.py` | Added Student, Faculty, Staff, Auditor, Read Only Viewer and regression test | Pass |
| BUG-010 | Reports | Required reports | 39 named reports available | Implemented as limited grouped reports | Major | Report engine has limited report types | None | Pending product gap | Not fixed |
| BUG-011 | API | JSON REST API | 30 API groups available | Mostly HTML form routes | Major | Implementation is server-rendered | None | Pending product gap | Not fixed |
| BUG-012 | Backup | Backup/restore | Backup and restore execute | MySQL client binaries missing | Major | Environment missing `mysql`/`mysqldump` | None | Environment blocker | Fail |
