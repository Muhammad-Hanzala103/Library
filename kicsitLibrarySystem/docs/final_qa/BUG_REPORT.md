# Bug Report

| Bug ID | Module | Screen/API | Steps | Expected | Actual | Severity | Root cause | File changed | Fix summary | Retest |
|---|---|---|---|---|---|---|---|---|---|---|
| BUG-001 | Startup | App import/server | Import `app.main:app` | App imports | FastAPIError on `HTMLResponse | RedirectResponse` annotations | Critical | FastAPI tried to generate response models from response classes | `app/routers/auth.py`, `app/routers/catalog.py`, `app/routers/circulation.py` | Removed invalid union response annotations | Pass |
| BUG-002 | Authentication | Password hashing | Run `hash_password` | Hash produced | bcrypt 5/passlib failure | Critical | Unpinned transitive `bcrypt` incompatible with passlib 1.7.4 | `requirements.txt` | Pinned `bcrypt==4.2.1` | Pass |
| BUG-003 | Setup | Alembic migration | `alembic upgrade head` | Migrate DB | MySQL refused connection | Critical | MySQL service unavailable | None | Environment blocker, not code-fixed | Fail |
| BUG-004 | Backup | Restore | POST restore without real confirmation | Server blocks | Client-only confirmation was bypassable before fix | Critical | Confirmation value not posted/validated server-side | `app/routers/backup.py`, `templates/backup/index.html` | Added required `confirm_text` server check | Static retest pass |
| BUG-005 | Catalog | Delete book/copy | Delete issued accession | Block delete | Could corrupt active issue state before fix | Critical | Delete did not guard active issues | `app/services/catalog_service.py`, `app/routers/catalog.py` | Added active issue guards | Static retest pass |
| BUG-006 | Reports | Overdue fine | Change setting and view/export overdue | Uses setting | Hardcoded `10.00` in report calculations before fix | Major | Report code ignored settings | `phase5_service.py`, `phase5.py`, `phase7_service.py` | Use `circulation.fine_per_day` | Static retest pass |
| BUG-007 | Import | CSV upload | Upload wrong/empty/large file | Reject cleanly | Missing explicit validation before fix | Major | Import route trusted raw upload | `app/routers/phase7.py` | Extension, empty, and size checks added | Smoke partial pass |
| BUG-008 | UI permissions | Sidebar | Login as limited user | Hide restricted links | Broad sidebar exposure before fix | Major | Template lacked permission guards | `templates/base.html` | Added permission-gated nav groups | Static retest pass |
| BUG-009 | Roles | Seed | Seed all required roles | 9 roles available | Only 4 roles/users seeded | Major | Seed scope incomplete | Pending | Needs role model expansion | Not fixed |
| BUG-010 | Reports | Required report list | Open 39 reports | All exist | Many are grouped/missing | Major | Report engine has limited report types | Pending | Add report definitions | Not fixed |
| BUG-011 | API | JSON REST API | Test 30 API groups | Endpoints exist | Mostly HTML routes, no full REST API | Major | Implementation is server-rendered | Pending | Add REST API layer if required | Not fixed |
| BUG-012 | Backup | Backup/restore | Create/restore backup | Works | MySQL binaries missing on PATH | Major | Environment missing `mysql`/`mysqldump` | Pending env | Install MySQL client/server | Blocked |

