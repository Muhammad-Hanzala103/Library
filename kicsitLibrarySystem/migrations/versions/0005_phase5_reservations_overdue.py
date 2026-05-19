"""phase5 reservations overdue

Revision ID: 0005_phase5_reservations
Revises: 0004_phase4_circulation
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa


revision = "0005_phase5_reservations"
down_revision = "0004_phase4_circulation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reservations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reservation_number", sa.String(length=40), nullable=False),
        sa.Column("consumer_type", sa.String(length=30), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=True),
        sa.Column("book_master_id", sa.Integer(), nullable=False),
        sa.Column("book_copy_id", sa.Integer(), nullable=True),
        sa.Column("reservation_date", sa.Date(), nullable=False),
        sa.Column("expiry_date", sa.Date(), nullable=False),
        sa.Column("queue_position", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("cancelled_reason", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["book_copy_id"], ["bookcopies.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["book_master_id"], ["bookmasters.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reservations_id"), "reservations", ["id"], unique=False)
    op.create_index(op.f("ix_reservations_reservation_number"), "reservations", ["reservation_number"], unique=True)
    op.create_index(op.f("ix_reservations_consumer_type"), "reservations", ["consumer_type"], unique=False)
    op.create_index(op.f("ix_reservations_student_id"), "reservations", ["student_id"], unique=False)
    op.create_index(op.f("ix_reservations_employee_id"), "reservations", ["employee_id"], unique=False)
    op.create_index(op.f("ix_reservations_book_master_id"), "reservations", ["book_master_id"], unique=False)
    op.create_index(op.f("ix_reservations_book_copy_id"), "reservations", ["book_copy_id"], unique=False)
    op.create_index(op.f("ix_reservations_reservation_date"), "reservations", ["reservation_date"], unique=False)
    op.create_index(op.f("ix_reservations_expiry_date"), "reservations", ["expiry_date"], unique=False)
    op.create_index(op.f("ix_reservations_status"), "reservations", ["status"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("consumer_type", sa.String(length=30), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=True),
        sa.Column("notification_type", sa.String(length=60), nullable=False),
        sa.Column("channel", sa.String(length=30), nullable=False),
        sa.Column("subject", sa.String(length=180), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("whatsapp_placeholder", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)
    op.create_index(op.f("ix_notifications_consumer_type"), "notifications", ["consumer_type"], unique=False)
    op.create_index(op.f("ix_notifications_student_id"), "notifications", ["student_id"], unique=False)
    op.create_index(op.f("ix_notifications_employee_id"), "notifications", ["employee_id"], unique=False)
    op.create_index(op.f("ix_notifications_notification_type"), "notifications", ["notification_type"], unique=False)
    op.create_index(op.f("ix_notifications_channel"), "notifications", ["channel"], unique=False)
    op.create_index(op.f("ix_notifications_status"), "notifications", ["status"], unique=False)

    op.create_table(
        "lostbooks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lost_date", sa.Date(), nullable=False),
        sa.Column("issue_record_id", sa.Integer(), nullable=True),
        sa.Column("book_copy_id", sa.Integer(), nullable=False),
        sa.Column("consumer_type", sa.String(length=30), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=True),
        sa.Column("fine_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("payment_status", sa.String(length=40), nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("resolved_status", sa.String(length=40), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["book_copy_id"], ["bookcopies.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["issue_record_id"], ["issuerecords.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_lostbooks_id"), "lostbooks", ["id"], unique=False)
    op.create_index(op.f("ix_lostbooks_lost_date"), "lostbooks", ["lost_date"], unique=False)
    op.create_index(op.f("ix_lostbooks_issue_record_id"), "lostbooks", ["issue_record_id"], unique=False)
    op.create_index(op.f("ix_lostbooks_book_copy_id"), "lostbooks", ["book_copy_id"], unique=False)
    op.create_index(op.f("ix_lostbooks_consumer_type"), "lostbooks", ["consumer_type"], unique=False)
    op.create_index(op.f("ix_lostbooks_student_id"), "lostbooks", ["student_id"], unique=False)
    op.create_index(op.f("ix_lostbooks_employee_id"), "lostbooks", ["employee_id"], unique=False)
    op.create_index(op.f("ix_lostbooks_payment_status"), "lostbooks", ["payment_status"], unique=False)
    op.create_index(op.f("ix_lostbooks_resolved_status"), "lostbooks", ["resolved_status"], unique=False)

    op.create_table(
        "damagedbooks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("damage_date", sa.Date(), nullable=False),
        sa.Column("issue_record_id", sa.Integer(), nullable=True),
        sa.Column("book_copy_id", sa.Integer(), nullable=False),
        sa.Column("consumer_type", sa.String(length=30), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=True),
        sa.Column("damage_level", sa.String(length=40), nullable=False),
        sa.Column("repair_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("resolved_status", sa.String(length=40), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["book_copy_id"], ["bookcopies.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["issue_record_id"], ["issuerecords.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_damagedbooks_id"), "damagedbooks", ["id"], unique=False)
    op.create_index(op.f("ix_damagedbooks_damage_date"), "damagedbooks", ["damage_date"], unique=False)
    op.create_index(op.f("ix_damagedbooks_issue_record_id"), "damagedbooks", ["issue_record_id"], unique=False)
    op.create_index(op.f("ix_damagedbooks_book_copy_id"), "damagedbooks", ["book_copy_id"], unique=False)
    op.create_index(op.f("ix_damagedbooks_consumer_type"), "damagedbooks", ["consumer_type"], unique=False)
    op.create_index(op.f("ix_damagedbooks_student_id"), "damagedbooks", ["student_id"], unique=False)
    op.create_index(op.f("ix_damagedbooks_employee_id"), "damagedbooks", ["employee_id"], unique=False)
    op.create_index(op.f("ix_damagedbooks_damage_level"), "damagedbooks", ["damage_level"], unique=False)
    op.create_index(op.f("ix_damagedbooks_resolved_status"), "damagedbooks", ["resolved_status"], unique=False)


def downgrade() -> None:
    op.drop_table("damagedbooks")
    op.drop_table("lostbooks")
    op.drop_table("notifications")
    op.drop_table("reservations")

