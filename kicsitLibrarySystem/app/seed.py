from sqlalchemy import select

from app.database import SessionLocal
from app.models import Permission, Role, User
from app.models import Category, DepartmentCategory, LiteratureCategory
from app.utils.security import hash_password


PERMISSIONS = [
    ("system.manage_all", "Manage Entire System", "System", "Full access for Super Admin."),
    ("dashboard.view", "View Dashboard", "Dashboard", "Open the main dashboard."),
    ("users.manage", "Manage Users", "Administration", "Manage users, roles, and permissions."),
    ("settings.manage", "Manage Settings", "Administration", "Manage system settings."),
    ("reports.view", "View Reports", "Reports", "View selected reports."),
    ("logs.view", "View Activity Logs", "Administration", "View activity logs."),
    ("catalog.manage", "Manage Catalog", "Library Catalog", "Manage book masters and copies."),
    ("circulation.manage", "Manage Issue Return", "Circulation", "Issue and return books."),
]

ROLE_PERMISSION_CODES = {
    "Super Admin": [code for code, *_ in PERMISSIONS],
    "Admin": ["dashboard.view", "users.manage", "settings.manage", "reports.view", "logs.view"],
    "Librarian": ["dashboard.view", "catalog.manage", "circulation.manage", "reports.view", "logs.view"],
    "Assistant Librarian": ["dashboard.view", "circulation.manage", "reports.view"],
}

SEED_USERS = [
    ("superadmin", "superadmin@kicsit.local", "Super Admin", "Super Admin"),
    ("admin", "admin@kicsit.local", "Admin", "Admin"),
    ("librarian", "librarian@kicsit.local", "Librarian", "Librarian"),
    ("assistant", "assistant@kicsit.local", "Assistant Librarian", "Assistant Librarian"),
]

DEFAULT_PASSWORD = "ChangeMe@123"


def get_or_create_permission(db, code: str, name: str, module: str, description: str) -> Permission:
    permission = db.scalar(select(Permission).where(Permission.code == code))
    if permission:
        return permission
    permission = Permission(code=code, name=name, module=module, description=description)
    db.add(permission)
    db.flush()
    return permission


def get_or_create_role(db, name: str) -> Role:
    role = db.scalar(select(Role).where(Role.name == name))
    if role:
        return role
    role = Role(name=name, description=f"System role for {name}.", is_system_role=True)
    db.add(role)
    db.flush()
    return role


def get_or_create_user(db, username: str, email: str, full_name: str, role: Role) -> User:
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            password_hash=hash_password(DEFAULT_PASSWORD),
            is_active=True,
        )
        db.add(user)
        db.flush()
    if role not in user.roles:
        user.roles.append(role)
    return user


def seed() -> None:
    db = SessionLocal()
    try:
        permissions_by_code = {
            code: get_or_create_permission(db, code, name, module, description)
            for code, name, module, description in PERMISSIONS
        }

        roles_by_name = {role_name: get_or_create_role(db, role_name) for role_name in ROLE_PERMISSION_CODES}

        for role_name, permission_codes in ROLE_PERMISSION_CODES.items():
            role = roles_by_name[role_name]
            for code in permission_codes:
                permission = permissions_by_code[code]
                if permission not in role.permissions:
                    role.permissions.append(permission)

        for username, email, full_name, role_name in SEED_USERS:
            get_or_create_user(db, username, email, full_name, roles_by_name[role_name])

        for name, code in [("Programming", "PROGRAMMING"), ("Artificial Intelligence", "AI"), ("Networking", "NETWORKING"), ("Database", "DATABASE")]:
            if db.scalar(select(Category).where(Category.name == name)) is None:
                db.add(Category(name=name, code=code, description=f"Default category: {name}"))

        for name, code in [("CS", "CS"), ("CE", "CE")]:
            if db.scalar(select(DepartmentCategory).where(DepartmentCategory.name == name)) is None:
                db.add(DepartmentCategory(name=name, code=code, description=f"Default department category: {name}"))

        for name, code in [("Urdu", "URDU"), ("English", "ENGLISH"), ("History", "HISTORY"), ("Islam", "ISLAM")]:
            if db.scalar(select(LiteratureCategory).where(LiteratureCategory.name == name)) is None:
                db.add(LiteratureCategory(name=name, code=code, description=f"Default literature category: {name}"))

        db.commit()
        print("Seed completed.")
        print("Default password for seed users: ChangeMe@123")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
