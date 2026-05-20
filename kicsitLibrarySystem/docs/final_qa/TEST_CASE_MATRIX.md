# Test Case Matrix

| Area | Test cases | Passed | Failed | Blocked | Notes |
|---|---:|---:|---:|---:|---|
| Fresh venv/install | 3 | 3 | 0 | 0 | Install passes after bcrypt pin |
| App startup | 3 | 3 | 0 | 0 | Compile, import, Uvicorn smoke pass |
| MySQL setup | 3 | 0 | 2 | 1 | Client missing, server refused connection |
| Auth utility | 3 | 3 | 0 | 0 | Hash, verify, JWT tamper tests pass |
| Authorization smoke | 5 | 5 | 0 | 0 | Protected routes redirect when unauthenticated |
| Metadata DB audit | 1 | 1 | 0 | 0 | 32 table names present in metadata |
| Live DB audit | 32+ | 0 | 1 | 31+ | MySQL unavailable |
| File upload validation | 5 | 5 | 0 | 0 | Valid/invalid document uploads covered |
| UI smoke | 2 | 2 | 0 | 0 | `/health`, `/login` |
| Full UI workflows | 44 screens | 0 | 0 | 44 | Requires DB/users |
| Reports | 39 reports | 0 | 0 | 39 | Requires DB; many missing as separate report types |
| Backup/restore | 13 | 0 | 2 | 11 | MySQL service/binaries unavailable |

Automated pytest result: 10 passed, 0 failed.

