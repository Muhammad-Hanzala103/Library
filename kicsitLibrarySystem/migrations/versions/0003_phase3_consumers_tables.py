"""phase3 consumers tables

Revision ID: 0003_phase3_consumers
Revises: 0002_phase2_catalog
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa


revision = "0003_phase3_consumers"
down_revision = "0002_phase2_catalog"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("registration_number", sa.String(length=80), nullable=False),
        sa.Column("admission_number", sa.String(length=80), nullable=True),
        sa.Column("roll_number", sa.String(length=80), nullable=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("father_name", sa.String(length=150), nullable=True),
        sa.Column("department", sa.String(length=120), nullable=True),
        sa.Column("program", sa.String(length=120), nullable=True),
        sa.Column("semester", sa.String(length=40), nullable=True),
        sa.Column("session", sa.String(length=60), nullable=True),
        sa.Column("batch", sa.String(length=60), nullable=True),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="Active"),
        sa.Column("clearance_status", sa.String(length=40), nullable=False, server_default="Not Cleared"),
        sa.Column("clearance_date", sa.Date(), nullable=True),
        sa.Column("clearance_remarks", sa.Text(), nullable=True),
        sa.Column("page_number", sa.String(length=80), nullable=True),
        sa.Column("register_number", sa.String(length=80), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_students_id"), "students", ["id"], unique=False)
    op.create_index(op.f("ix_students_registration_number"), "students", ["registration_number"], unique=True)
    op.create_index(op.f("ix_students_admission_number"), "students", ["admission_number"], unique=True)
    op.create_index(op.f("ix_students_roll_number"), "students", ["roll_number"], unique=False)
    op.create_index(op.f("ix_students_name"), "students", ["name"], unique=False)
    op.create_index(op.f("ix_students_department"), "students", ["department"], unique=False)
    op.create_index(op.f("ix_students_phone"), "students", ["phone"], unique=False)
    op.create_index(op.f("ix_students_email"), "students", ["email"], unique=False)
    op.create_index(op.f("ix_students_status"), "students", ["status"], unique=False)
    op.create_index(op.f("ix_students_clearance_status"), "students", ["clearance_status"], unique=False)
    op.create_index(op.f("ix_students_is_active"), "students", ["is_active"], unique=False)

    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("p_number", sa.String(length=80), nullable=True),
        sa.Column("cnic", sa.String(length=30), nullable=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("department", sa.String(length=120), nullable=True),
        sa.Column("designation", sa.String(length=120), nullable=True),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("employee_type", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("joining_date", sa.Date(), nullable=True),
        sa.Column("leaving_date", sa.Date(), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_employees_id"), "employees", ["id"], unique=False)
    op.create_index(op.f("ix_employees_p_number"), "employees", ["p_number"], unique=True)
    op.create_index(op.f("ix_employees_cnic"), "employees", ["cnic"], unique=True)
    op.create_index(op.f("ix_employees_name"), "employees", ["name"], unique=False)
    op.create_index(op.f("ix_employees_department"), "employees", ["department"], unique=False)
    op.create_index(op.f("ix_employees_phone"), "employees", ["phone"], unique=False)
    op.create_index(op.f("ix_employees_email"), "employees", ["email"], unique=False)
    op.create_index(op.f("ix_employees_employee_type"), "employees", ["employee_type"], unique=False)
    op.create_index(op.f("ix_employees_is_active"), "employees", ["is_active"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_employees_is_active"), table_name="employees")
    op.drop_index(op.f("ix_employees_employee_type"), table_name="employees")
    op.drop_index(op.f("ix_employees_email"), table_name="employees")
    op.drop_index(op.f("ix_employees_phone"), table_name="employees")
    op.drop_index(op.f("ix_employees_department"), table_name="employees")
    op.drop_index(op.f("ix_employees_name"), table_name="employees")
    op.drop_index(op.f("ix_employees_cnic"), table_name="employees")
    op.drop_index(op.f("ix_employees_p_number"), table_name="employees")
    op.drop_index(op.f("ix_employees_id"), table_name="employees")
    op.drop_table("employees")
    op.drop_index(op.f("ix_students_is_active"), table_name="students")
    op.drop_index(op.f("ix_students_clearance_status"), table_name="students")
    op.drop_index(op.f("ix_students_status"), table_name="students")
    op.drop_index(op.f("ix_students_email"), table_name="students")
    op.drop_index(op.f("ix_students_phone"), table_name="students")
    op.drop_index(op.f("ix_students_department"), table_name="students")
    op.drop_index(op.f("ix_students_name"), table_name="students")
    op.drop_index(op.f("ix_students_roll_number"), table_name="students")
    op.drop_index(op.f("ix_students_admission_number"), table_name="students")
    op.drop_index(op.f("ix_students_registration_number"), table_name="students")
    op.drop_index(op.f("ix_students_id"), table_name="students")
    op.drop_table("students")

