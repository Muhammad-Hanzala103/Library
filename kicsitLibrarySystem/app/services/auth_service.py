from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Role, User
from app.utils.security import verify_password


def get_user_by_username_or_email(db: Session, username_or_email: str) -> User | None:
    statement = (
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(or_(User.username == username_or_email, User.email == username_or_email))
    )
    return db.execute(statement).scalar_one_or_none()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    statement = select(User).options(selectinload(User.roles).selectinload(Role.permissions)).where(User.id == user_id)
    return db.execute(statement).scalar_one_or_none()


def authenticate_user(db: Session, username_or_email: str, password: str) -> User | None:
    user = get_user_by_username_or_email(db, username_or_email)
    if user is None:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        user.failed_login_count += 1
        db.add(user)
        db.commit()
        return None
    user.failed_login_count = 0
    user.last_login_at = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_permission_codes(user: User) -> set[str]:
    permission_codes: set[str] = set()
    for role in user.roles:
        for permission in role.permissions:
            permission_codes.add(permission.code)
    return permission_codes
