# Pending Limitations Report

- MySQL server is not running or reachable at `127.0.0.1:3306`; fresh migration, seed, authenticated workflow, live DB audit, report data checks, and backup restore cannot pass until this is fixed.
- MySQL client binaries `mysql` and `mysqldump` are not on PATH; backup and restore cannot pass.
- Student, Faculty, Staff, Auditor, and Read Only Viewer seeded users are missing.
- Fine-grained CRUD permissions are missing; current permissions are broad module permissions.
- User, role, and permission administration UI is not implemented.
- The project exposes mostly HTML form routes, not the requested full REST API surface.
- Many requested report names are grouped or absent as separate reports.
- Excel import is not implemented for the requested modules; CSV preview/import is partial.
- Full browser automation is blocked without a live database and seeded users.
- Full consistency SQL checks could not be run without MySQL.
- Backup restore into a separate test database could not be run without MySQL.
- Performance testing with many books could not be run without seed data.

