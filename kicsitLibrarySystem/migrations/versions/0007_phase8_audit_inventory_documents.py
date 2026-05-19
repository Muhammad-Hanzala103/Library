"""phase8 audit inventory documents

Revision ID: 0007_phase8_audit
Revises: 0006_phase7_imports
Create Date: 2026-05-19
"""

from alembic import op
import sqlalchemy as sa


revision = "0007_phase8_audit"
down_revision = "0006_phase7_imports"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("document_type", sa.String(length=80), nullable=False),
        sa.Column("version", sa.String(length=40), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=120), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("uploaded_by_user_id", sa.Integer(), nullable=True),
        sa.Column("upload_date", sa.DateTime(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
        sa.UniqueConstraint("stored_filename"),
    )
    op.create_index(op.f("ix_documents_category"), "documents", ["category"], unique=False)
    op.create_index(op.f("ix_documents_document_type"), "documents", ["document_type"], unique=False)
    op.create_index(op.f("ix_documents_id"), "documents", ["id"], unique=False)
    op.create_index(op.f("ix_documents_is_active"), "documents", ["is_active"], unique=False)
    op.create_index(op.f("ix_documents_title"), "documents", ["title"], unique=False)
    op.create_index(op.f("ix_documents_upload_date"), "documents", ["upload_date"], unique=False)

    op.create_table(
        "auditrecords",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("audit_date", sa.Date(), nullable=False),
        sa.Column("audit_type", sa.String(length=100), nullable=False),
        sa.Column("financial_year", sa.String(length=30), nullable=True),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("suggestions", sa.Text(), nullable=True),
        sa.Column("findings", sa.Text(), nullable=True),
        sa.Column("recommendations", sa.Text(), nullable=True),
        sa.Column("action_required", sa.Text(), nullable=True),
        sa.Column("action_taken", sa.Text(), nullable=True),
        sa.Column("responsible_person", sa.String(length=150), nullable=True),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("attachment_document_id", sa.Integer(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["attachment_document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_auditrecords_audit_date"), "auditrecords", ["audit_date"], unique=False)
    op.create_index(op.f("ix_auditrecords_audit_type"), "auditrecords", ["audit_type"], unique=False)
    op.create_index(op.f("ix_auditrecords_financial_year"), "auditrecords", ["financial_year"], unique=False)
    op.create_index(op.f("ix_auditrecords_id"), "auditrecords", ["id"], unique=False)
    op.create_index(op.f("ix_auditrecords_status"), "auditrecords", ["status"], unique=False)

    op.create_table(
        "inventoryitems",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("item_name", sa.String(length=180), nullable=False),
        sa.Column("item_type", sa.String(length=80), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("available_quantity", sa.Integer(), nullable=False),
        sa.Column("damaged_quantity", sa.Integer(), nullable=False),
        sa.Column("condition", sa.String(length=80), nullable=True),
        sa.Column("location", sa.String(length=120), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("supplier", sa.String(length=150), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inventoryitems_condition"), "inventoryitems", ["condition"], unique=False)
    op.create_index(op.f("ix_inventoryitems_id"), "inventoryitems", ["id"], unique=False)
    op.create_index(op.f("ix_inventoryitems_item_name"), "inventoryitems", ["item_name"], unique=False)
    op.create_index(op.f("ix_inventoryitems_item_type"), "inventoryitems", ["item_type"], unique=False)
    op.create_index(op.f("ix_inventoryitems_location"), "inventoryitems", ["location"], unique=False)

    op.create_table(
        "newarrivals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("arrival_number", sa.String(length=80), nullable=False),
        sa.Column("material_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("department_category_id", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("purchase_year", sa.Integer(), nullable=True),
        sa.Column("purchase_month", sa.String(length=20), nullable=True),
        sa.Column("supplier", sa.String(length=150), nullable=True),
        sa.Column("invoice_number", sa.String(length=120), nullable=True),
        sa.Column("invoice_document_id", sa.Integer(), nullable=True),
        sa.Column("received_date", sa.Date(), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["department_category_id"], ["departmentcategories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["invoice_document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("arrival_number"),
    )
    op.create_index(op.f("ix_newarrivals_arrival_number"), "newarrivals", ["arrival_number"], unique=False)
    op.create_index(op.f("ix_newarrivals_id"), "newarrivals", ["id"], unique=False)
    op.create_index(op.f("ix_newarrivals_material_type"), "newarrivals", ["material_type"], unique=False)
    op.create_index(op.f("ix_newarrivals_received_date"), "newarrivals", ["received_date"], unique=False)
    op.create_index(op.f("ix_newarrivals_title"), "newarrivals", ["title"], unique=False)

    op.create_table(
        "visitrecords",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("visit_date", sa.Date(), nullable=False),
        sa.Column("organization", sa.String(length=80), nullable=False),
        sa.Column("visit_type", sa.String(length=80), nullable=False),
        sa.Column("team_members", sa.Text(), nullable=True),
        sa.Column("department", sa.String(length=120), nullable=True),
        sa.Column("purpose", sa.Text(), nullable=True),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("suggestions", sa.Text(), nullable=True),
        sa.Column("findings", sa.Text(), nullable=True),
        sa.Column("action_taken", sa.Text(), nullable=True),
        sa.Column("follow_up_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("attachment_document_id", sa.Integer(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["attachment_document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_visitrecords_department"), "visitrecords", ["department"], unique=False)
    op.create_index(op.f("ix_visitrecords_id"), "visitrecords", ["id"], unique=False)
    op.create_index(op.f("ix_visitrecords_organization"), "visitrecords", ["organization"], unique=False)
    op.create_index(op.f("ix_visitrecords_status"), "visitrecords", ["status"], unique=False)
    op.create_index(op.f("ix_visitrecords_visit_date"), "visitrecords", ["visit_date"], unique=False)
    op.create_index(op.f("ix_visitrecords_visit_type"), "visitrecords", ["visit_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_visitrecords_visit_type"), table_name="visitrecords")
    op.drop_index(op.f("ix_visitrecords_visit_date"), table_name="visitrecords")
    op.drop_index(op.f("ix_visitrecords_status"), table_name="visitrecords")
    op.drop_index(op.f("ix_visitrecords_organization"), table_name="visitrecords")
    op.drop_index(op.f("ix_visitrecords_id"), table_name="visitrecords")
    op.drop_index(op.f("ix_visitrecords_department"), table_name="visitrecords")
    op.drop_table("visitrecords")
    op.drop_index(op.f("ix_newarrivals_title"), table_name="newarrivals")
    op.drop_index(op.f("ix_newarrivals_received_date"), table_name="newarrivals")
    op.drop_index(op.f("ix_newarrivals_material_type"), table_name="newarrivals")
    op.drop_index(op.f("ix_newarrivals_id"), table_name="newarrivals")
    op.drop_index(op.f("ix_newarrivals_arrival_number"), table_name="newarrivals")
    op.drop_table("newarrivals")
    op.drop_index(op.f("ix_inventoryitems_location"), table_name="inventoryitems")
    op.drop_index(op.f("ix_inventoryitems_item_type"), table_name="inventoryitems")
    op.drop_index(op.f("ix_inventoryitems_item_name"), table_name="inventoryitems")
    op.drop_index(op.f("ix_inventoryitems_id"), table_name="inventoryitems")
    op.drop_index(op.f("ix_inventoryitems_condition"), table_name="inventoryitems")
    op.drop_table("inventoryitems")
    op.drop_index(op.f("ix_auditrecords_status"), table_name="auditrecords")
    op.drop_index(op.f("ix_auditrecords_id"), table_name="auditrecords")
    op.drop_index(op.f("ix_auditrecords_financial_year"), table_name="auditrecords")
    op.drop_index(op.f("ix_auditrecords_audit_type"), table_name="auditrecords")
    op.drop_index(op.f("ix_auditrecords_audit_date"), table_name="auditrecords")
    op.drop_table("auditrecords")
    op.drop_index(op.f("ix_documents_upload_date"), table_name="documents")
    op.drop_index(op.f("ix_documents_title"), table_name="documents")
    op.drop_index(op.f("ix_documents_is_active"), table_name="documents")
    op.drop_index(op.f("ix_documents_id"), table_name="documents")
    op.drop_index(op.f("ix_documents_document_type"), table_name="documents")
    op.drop_index(op.f("ix_documents_category"), table_name="documents")
    op.drop_table("documents")
