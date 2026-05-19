# Phase 1 Manual Test Checklist

Run these checks after installing dependencies, creating the MySQL database, applying migrations, and running the seed script.

## Setup Checks

1. Copy `.env.example` to `.env`.
2. Set MySQL username, password, host, port, and database name.
3. Create the MySQL database manually in MySQL Workbench:
   ```sql
   CREATE DATABASE kicsit_library CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
4. Run `alembic upgrade head`.
5. Run `python -m app.seed`.

## Authentication Checks

1. Open `http://127.0.0.1:8000/login`.
2. Login with username `superadmin` and password `ChangeMe@123`.
3. Confirm dashboard opens.
4. Logout from the top bar.
5. Confirm the browser returns to login page.
6. Try wrong password and confirm error message appears.
7. Confirm failed login creates an activity log row.

## Seed User Checks

Test these accounts with password `ChangeMe@123`:

1. `superadmin`
2. `admin`
3. `librarian`
4. `assistant`

## Dashboard Checks

1. Confirm sidebar is visible.
2. Confirm top bar shows institute name and logged-in user.
3. Confirm dashboard cards show counts for users, roles, permissions, and activity logs.
4. Confirm current access panel shows name, email, and roles.
5. Confirm recent activity shows login and logout records.

## Database Checks

Confirm these tables exist:

1. `users`
2. `roles`
3. `permissions`
4. `userroles`
5. `rolepermissions`
6. `activitylogs`

