from fastapi import Request
from sqlalchemy.orm import Session

from app.models import ActivityLog, User


def write_activity_log(
    db: Session,
    *,
    request: Request | None,
    action: str,
    module: str,
    user: User | None = None,
    entity_name: str | None = None,
    entity_id: str | None = None,
    description: str | None = None,
) -> ActivityLog:
    ip_address = None
    user_agent = None
    if request is not None:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    log = ActivityLog(
        user_id=user.id if user else None,
        action=action,
        module=module,
        entity_name=entity_name,
        entity_id=entity_id,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent[:255] if user_agent else None,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

