"""phase9 settings backups

Revision ID: 0008_phase9_settings
Revises: 0007_phase8_audit
Create Date: 2026-05-20
"""

from alembic import op
import sqlalchemy as sa


revision = "0008_phase9_settings"
down_revision = "0007_phase8_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index(op.f("ix_settings_id"), "settings", ["id"], unique=False)
    op.create_index(op.f("ix_settings_key"), "settings", ["key"], unique=True)
    op.create_index(op.f("ix_settings_category"), "settings", ["category"], unique=False)

    op.create_table(
        "backups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("filepath", sa.String(length=255), nullable=False),
        sa.Column("filesize_bytes", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_by_username", sa.String(length=150), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_backups_id"), "backups", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_backups_id"), table_name="backups")
    op.drop_table("backups")

    op.drop_index(op.f("ix_settings_category"), table_name="settings")
    op.drop_index(op.f("ix_settings_key"), table_name="settings")
    op.drop_index(op.f("ix_settings_id"), table_name="settings")
    op.drop_table("settings")
