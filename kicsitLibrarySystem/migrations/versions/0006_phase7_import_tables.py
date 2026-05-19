"""phase7 import tables

Revision ID: 0006_phase7_imports
Revises: 0005_phase5_reservations
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa


revision = "0006_phase7_imports"
down_revision = "0005_phase5_reservations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "importbatches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("import_type", sa.String(length=60), nullable=False),
        sa.Column("source_filename", sa.String(length=255), nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False),
        sa.Column("success_rows", sa.Integer(), nullable=False),
        sa.Column("failed_rows", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_importbatches_id"), "importbatches", ["id"], unique=False)
    op.create_index(op.f("ix_importbatches_import_type"), "importbatches", ["import_type"], unique=False)
    op.create_index(op.f("ix_importbatches_status"), "importbatches", ["status"], unique=False)

    op.create_table(
        "importerrors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("import_batch_id", sa.Integer(), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("row_data_json", sa.Text(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["import_batch_id"], ["importbatches.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_importerrors_id"), "importerrors", ["id"], unique=False)
    op.create_index(op.f("ix_importerrors_import_batch_id"), "importerrors", ["import_batch_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_importerrors_import_batch_id"), table_name="importerrors")
    op.drop_index(op.f("ix_importerrors_id"), table_name="importerrors")
    op.drop_table("importerrors")
    op.drop_index(op.f("ix_importbatches_status"), table_name="importbatches")
    op.drop_index(op.f("ix_importbatches_import_type"), table_name="importbatches")
    op.drop_index(op.f("ix_importbatches_id"), table_name="importbatches")
    op.drop_table("importbatches")

