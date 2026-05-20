"""Dynamic settings service – reads configuration from the `settings` database table."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.settings import Setting


def get_setting_value(db: Session, key: str, default: str = "") -> str:
    """Return the value for a setting key, or the default if not found."""
    row = db.scalar(select(Setting).where(Setting.key == key))
    if row is None or row.value is None:
        return default
    return row.value


def get_setting_int(db: Session, key: str, default: int = 0) -> int:
    """Return the value for a setting key as an integer."""
    raw = get_setting_value(db, key, str(default))
    try:
        return int(raw)
    except (ValueError, TypeError):
        return default


def get_setting_decimal(db: Session, key: str, default: Decimal = Decimal("0")) -> Decimal:
    """Return the value for a setting key as a Decimal."""
    raw = get_setting_value(db, key, str(default))
    try:
        return Decimal(raw)
    except Exception:
        return default


def save_setting_value(db: Session, key: str, value: str) -> Setting:
    """Update an existing setting or create a new one."""
    row = db.scalar(select(Setting).where(Setting.key == key))
    if row is None:
        row = Setting(key=key, value=value, category=key.split(".")[0] if "." in key else "general")
        db.add(row)
    else:
        row.value = value
    db.flush()
    return row


def all_settings(db: Session) -> dict[str, str]:
    """Return all settings as a flat key→value dictionary."""
    rows = db.scalars(select(Setting).order_by(Setting.category, Setting.key)).all()
    return {r.key: (r.value or "") for r in rows}


def settings_by_category(db: Session) -> dict[str, list[Setting]]:
    """Return settings grouped by category."""
    rows = db.scalars(select(Setting).order_by(Setting.category, Setting.key)).all()
    grouped: dict[str, list[Setting]] = {}
    for row in rows:
        grouped.setdefault(row.category, []).append(row)
    return grouped
