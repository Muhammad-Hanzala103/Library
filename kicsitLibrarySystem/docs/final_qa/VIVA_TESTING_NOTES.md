# Viva Testing Notes

- The project stack is FastAPI, SQLAlchemy, Alembic, MySQL, Jinja templates, JWT cookie auth, report exports, local uploads, and backup/restore through MySQL CLI tools.
- The application now starts after fixing FastAPI response annotation issues.
- Automated smoke tests pass for startup, public pages, security utilities, protected route redirects, metadata table coverage, and upload validation.
- The live database portion is not accepted because MySQL was not reachable during QA.
- The system is a strong prototype but should not be called production-ready until live migration, seed, role matrix, workflows, reports, and restore testing pass.

