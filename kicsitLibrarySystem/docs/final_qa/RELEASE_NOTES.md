# Release Notes

Release decision: Not Ready.

Changed or verified during final QA:
- Fixed FastAPI startup route annotation blocker.
- Pinned bcrypt dependency for stable password hashing.
- Added smoke tests.
- Verified app import, Uvicorn smoke, `/health`, `/login`, protected route redirects, JWT/password utilities, upload validation, and metadata table coverage.

Known release blockers:
- MySQL unavailable.
- MySQL CLI tools unavailable.
- Seeded role/user set incomplete.
- Full REST API surface missing.
- Full required report catalog missing.
- Full UI workflow/browser testing blocked.

