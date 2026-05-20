# Security Test Report

Passed executable checks:
- Password hashes are not plain text.
- Correct password verifies.
- Valid JWT decodes.
- Tampered JWT is rejected.
- Protected routes redirect without session.
- Invalid upload extensions and empty uploads are rejected.

Fixed security issues:
- Startup error from invalid FastAPI response annotations.
- bcrypt dependency break.
- Backup restore now requires server-side confirmation.
- Backup password no longer goes into process arguments.
- Active issued books cannot be deleted through catalog service.
- Permission-restricted sidebar links are hidden.

Remaining risks:
- Live role matrix could not be executed without MySQL.
- Seed roles are incomplete.
- Fine-grained backend permissions are too broad.
- Full upload malware/content sniffing is not implemented.
- CSRF protection for form POSTs is not implemented.
- Rate limiting/account lockout is not implemented despite `failed_login_count` fields.

