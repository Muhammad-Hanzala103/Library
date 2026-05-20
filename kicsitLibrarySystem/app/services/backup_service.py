"""Backup and restore service – creates MySQL dumps and restores them."""

import os
import subprocess
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.settings import Backup
from app.services.settings_service import get_setting_value

BACKUP_DIR = Path("app/uploads/backups")


def _ensure_backup_dir(db: Session) -> Path:
    """Ensure the backup directory exists and return its path."""
    custom = get_setting_value(db, "backup.backup_directory", str(BACKUP_DIR))
    path = Path(custom)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _find_mysql_bin(binary: str) -> str:
    """Locate a MySQL binary (mysqldump or mysql) on Windows."""
    # Try PATH first
    import shutil
    found = shutil.which(binary)
    if found:
        return found
    # Common Windows install paths
    for base in [
        r"C:\Program Files\MySQL\MySQL Server 8.0\bin",
        r"C:\Program Files\MySQL\MySQL Server 8.4\bin",
        r"C:\Program Files\MySQL\MySQL Server 8.1\bin",
        r"C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin",
        r"C:\xampp\mysql\bin",
        r"C:\wamp64\bin\mysql\mysql8.0.31\bin",
        r"C:\laragon\bin\mysql\mysql-8.0.30-winx64\bin",
    ]:
        candidate = os.path.join(base, f"{binary}.exe")
        if os.path.isfile(candidate):
            return candidate
    raise FileNotFoundError(
        f"Cannot find '{binary}'. Please add MySQL bin directory to your system PATH "
        f"or install MySQL Server / MySQL Workbench."
    )


def create_db_backup(db: Session, username: str) -> Backup:
    """Create a MySQL database dump and record it in the backups table."""
    cfg = get_settings()
    backup_dir = _ensure_backup_dir(db)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"kicsit_backup_{timestamp}.sql"
    filepath = backup_dir / filename

    mysqldump = _find_mysql_bin("mysqldump")
    cmd = [
        mysqldump,
        f"--host={cfg.mysql_host}",
        f"--port={cfg.mysql_port}",
        f"--user={cfg.mysql_user}",
        f"--databases", cfg.mysql_database,
        "--routines",
        "--triggers",
        "--single-transaction",
        "--set-gtid-purged=OFF",
    ]
    env = os.environ.copy()
    if cfg.mysql_password:
        env["MYSQL_PWD"] = cfg.mysql_password

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, timeout=300, env=env)
        if result.returncode != 0:
            error_msg = result.stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"mysqldump failed: {error_msg}")
        filesize = filepath.stat().st_size
        status = "Success"
        remarks = None
    except Exception as exc:
        filesize = filepath.stat().st_size if filepath.exists() else 0
        status = "Failed"
        remarks = str(exc)

    backup = Backup(
        filename=filename,
        filepath=str(filepath),
        filesize_bytes=filesize,
        status=status,
        remarks=remarks,
        created_by_username=username,
    )
    db.add(backup)
    db.commit()
    db.refresh(backup)
    return backup


def restore_db_backup(db: Session, backup_id: int) -> Backup:
    """Restore a database from a previously created backup file."""
    backup = db.get(Backup, backup_id)
    if backup is None:
        raise ValueError("Backup record not found.")
    if backup.status != "Success":
        raise ValueError("Only successful backups can be restored.")
    path = Path(backup.filepath)
    if not path.exists():
        raise FileNotFoundError(f"Backup file not found: {backup.filepath}")

    cfg = get_settings()
    mysql_bin = _find_mysql_bin("mysql")
    cmd = [
        mysql_bin,
        f"--host={cfg.mysql_host}",
        f"--port={cfg.mysql_port}",
        f"--user={cfg.mysql_user}",
        cfg.mysql_database,
    ]
    env = os.environ.copy()
    if cfg.mysql_password:
        env["MYSQL_PWD"] = cfg.mysql_password

    with open(path, "r", encoding="utf-8") as f:
        result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, timeout=600, env=env)
    if result.returncode != 0:
        error_msg = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"mysql restore failed: {error_msg}")
    return backup


def list_backups(db: Session) -> list[Backup]:
    """Return all backup records ordered by most recent first."""
    from sqlalchemy import select
    return db.scalars(select(Backup).order_by(Backup.created_at.desc())).all()


def delete_backup(db: Session, backup_id: int) -> None:
    """Delete a backup record and its file from disk."""
    backup = db.get(Backup, backup_id)
    if backup is None:
        raise ValueError("Backup record not found.")
    path = Path(backup.filepath)
    if path.exists():
        path.unlink()
    db.delete(backup)
    db.commit()
