"""phase4 circulation tables

Revision ID: 0004_phase4_circulation
Revises: 0003_phase3_consumers
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa


revision = "0004_phase4_circulation"
down_revision = "0003_phase3_consumers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "issuerecords",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("issue_number", sa.String(length=40), nullable=False),
        sa.Column("book_copy_id", sa.Integer(), nullable=False),
        sa.Column("book_master_id", sa.Integer(), nullable=False),
        sa.Column("consumer_type", sa.String(length=30), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=True),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("issued_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["book_copy_id"], ["bookcopies.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["book_master_id"], ["bookmasters.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["issued_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_issuerecords_id"), "issuerecords", ["id"], unique=False)
    op.create_index(op.f("ix_issuerecords_issue_number"), "issuerecords", ["issue_number"], unique=True)
    op.create_index(op.f("ix_issuerecords_book_copy_id"), "issuerecords", ["book_copy_id"], unique=False)
    op.create_index(op.f("ix_issuerecords_book_master_id"), "issuerecords", ["book_master_id"], unique=False)
    op.create_index(op.f("ix_issuerecords_consumer_type"), "issuerecords", ["consumer_type"], unique=False)
    op.create_index(op.f("ix_issuerecords_student_id"), "issuerecords", ["student_id"], unique=False)
    op.create_index(op.f("ix_issuerecords_employee_id"), "issuerecords", ["employee_id"], unique=False)
    op.create_index(op.f("ix_issuerecords_issue_date"), "issuerecords", ["issue_date"], unique=False)
    op.create_index(op.f("ix_issuerecords_due_date"), "issuerecords", ["due_date"], unique=False)
    op.create_index(op.f("ix_issuerecords_status"), "issuerecords", ["status"], unique=False)

    op.create_table(
        "receiverecords",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("receive_number", sa.String(length=40), nullable=False),
        sa.Column("issue_record_id", sa.Integer(), nullable=False),
        sa.Column("book_copy_id", sa.Integer(), nullable=False),
        sa.Column("receive_date", sa.Date(), nullable=False),
        sa.Column("book_condition", sa.String(length=80), nullable=False),
        sa.Column("overdue_days", sa.Integer(), nullable=False),
        sa.Column("calculated_fine_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("fine_collected_status", sa.String(length=40), nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("received_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["book_copy_id"], ["bookcopies.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["issue_record_id"], ["issuerecords.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["received_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("issue_record_id"),
    )
    op.create_index(op.f("ix_receiverecords_id"), "receiverecords", ["id"], unique=False)
    op.create_index(op.f("ix_receiverecords_receive_number"), "receiverecords", ["receive_number"], unique=True)
    op.create_index(op.f("ix_receiverecords_book_copy_id"), "receiverecords", ["book_copy_id"], unique=False)
    op.create_index(op.f("ix_receiverecords_receive_date"), "receiverecords", ["receive_date"], unique=False)

    op.create_table(
        "fines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("fine_number", sa.String(length=40), nullable=False),
        sa.Column("issue_record_id", sa.Integer(), nullable=True),
        sa.Column("receive_record_id", sa.Integer(), nullable=True),
        sa.Column("book_copy_id", sa.Integer(), nullable=True),
        sa.Column("consumer_type", sa.String(length=30), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=True),
        sa.Column("fine_type", sa.String(length=40), nullable=False),
        sa.Column("fine_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("paid_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("remaining_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("payment_status", sa.String(length=40), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=True),
        sa.Column("collected_by_user_id", sa.Integer(), nullable=True),
        sa.Column("waiver_reason", sa.Text(), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["book_copy_id"], ["bookcopies.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["collected_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["issue_record_id"], ["issuerecords.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["receive_record_id"], ["receiverecords.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_fines_id"), "fines", ["id"], unique=False)
    op.create_index(op.f("ix_fines_fine_number"), "fines", ["fine_number"], unique=True)
    op.create_index(op.f("ix_fines_issue_record_id"), "fines", ["issue_record_id"], unique=False)
    op.create_index(op.f("ix_fines_receive_record_id"), "fines", ["receive_record_id"], unique=False)
    op.create_index(op.f("ix_fines_book_copy_id"), "fines", ["book_copy_id"], unique=False)
    op.create_index(op.f("ix_fines_consumer_type"), "fines", ["consumer_type"], unique=False)
    op.create_index(op.f("ix_fines_student_id"), "fines", ["student_id"], unique=False)
    op.create_index(op.f("ix_fines_employee_id"), "fines", ["employee_id"], unique=False)
    op.create_index(op.f("ix_fines_payment_status"), "fines", ["payment_status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_fines_payment_status"), table_name="fines")
    op.drop_index(op.f("ix_fines_employee_id"), table_name="fines")
    op.drop_index(op.f("ix_fines_student_id"), table_name="fines")
    op.drop_index(op.f("ix_fines_consumer_type"), table_name="fines")
    op.drop_index(op.f("ix_fines_book_copy_id"), table_name="fines")
    op.drop_index(op.f("ix_fines_receive_record_id"), table_name="fines")
    op.drop_index(op.f("ix_fines_issue_record_id"), table_name="fines")
    op.drop_index(op.f("ix_fines_fine_number"), table_name="fines")
    op.drop_index(op.f("ix_fines_id"), table_name="fines")
    op.drop_table("fines")
    op.drop_index(op.f("ix_receiverecords_receive_date"), table_name="receiverecords")
    op.drop_index(op.f("ix_receiverecords_book_copy_id"), table_name="receiverecords")
    op.drop_index(op.f("ix_receiverecords_receive_number"), table_name="receiverecords")
    op.drop_index(op.f("ix_receiverecords_id"), table_name="receiverecords")
    op.drop_table("receiverecords")
    op.drop_index(op.f("ix_issuerecords_status"), table_name="issuerecords")
    op.drop_index(op.f("ix_issuerecords_due_date"), table_name="issuerecords")
    op.drop_index(op.f("ix_issuerecords_issue_date"), table_name="issuerecords")
    op.drop_index(op.f("ix_issuerecords_employee_id"), table_name="issuerecords")
    op.drop_index(op.f("ix_issuerecords_student_id"), table_name="issuerecords")
    op.drop_index(op.f("ix_issuerecords_consumer_type"), table_name="issuerecords")
    op.drop_index(op.f("ix_issuerecords_book_master_id"), table_name="issuerecords")
    op.drop_index(op.f("ix_issuerecords_book_copy_id"), table_name="issuerecords")
    op.drop_index(op.f("ix_issuerecords_issue_number"), table_name="issuerecords")
    op.drop_index(op.f("ix_issuerecords_id"), table_name="issuerecords")
    op.drop_table("issuerecords")

