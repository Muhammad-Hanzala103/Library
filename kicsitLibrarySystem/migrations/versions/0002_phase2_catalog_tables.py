"""phase2 catalog tables

Revision ID: 0002_phase2_catalog
Revises: 0001_phase1_auth
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa


revision = "0002_phase2_catalog"
down_revision = "0001_phase1_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_authors_id"), "authors", ["id"], unique=False)
    op.create_index(op.f("ix_authors_name"), "authors", ["name"], unique=True)

    op.create_table(
        "publishers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("contact", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_publishers_id"), "publishers", ["id"], unique=False)
    op.create_index(op.f("ix_publishers_name"), "publishers", ["name"], unique=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=False)
    op.create_index(op.f("ix_categories_name"), "categories", ["name"], unique=True)

    op.create_table(
        "departmentcategories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_departmentcategories_id"), "departmentcategories", ["id"], unique=False)
    op.create_index(op.f("ix_departmentcategories_name"), "departmentcategories", ["name"], unique=True)

    op.create_table(
        "literaturecategories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_literaturecategories_id"), "literaturecategories", ["id"], unique=False)
    op.create_index(op.f("ix_literaturecategories_name"), "literaturecategories", ["name"], unique=True)

    op.create_table(
        "bookmasters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("unique_title", sa.String(length=255), nullable=True),
        sa.Column("subtitle", sa.String(length=255), nullable=True),
        sa.Column("publisher_id", sa.Integer(), nullable=True),
        sa.Column("isbn", sa.String(length=30), nullable=True),
        sa.Column("issn", sa.String(length=30), nullable=True),
        sa.Column("source", sa.String(length=120), nullable=True),
        sa.Column("department_category_id", sa.Integer(), nullable=True),
        sa.Column("literature_category_id", sa.Integer(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("edition", sa.String(length=80), nullable=True),
        sa.Column("publication_place", sa.String(length=120), nullable=True),
        sa.Column("publication_year", sa.Integer(), nullable=True),
        sa.Column("language", sa.String(length=80), nullable=True),
        sa.Column("format", sa.String(length=80), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("book_location", sa.String(length=120), nullable=True),
        sa.Column("rack", sa.String(length=80), nullable=True),
        sa.Column("shelf", sa.String(length=80), nullable=True),
        sa.Column("hall", sa.String(length=80), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("book_image_filename", sa.String(length=255), nullable=True),
        sa.Column("bill_number", sa.String(length=120), nullable=True),
        sa.Column("store_name", sa.String(length=150), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("supplier", sa.String(length=150), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("deleted_reason", sa.String(length=255), nullable=True),
        sa.Column("deleted_by_user_id", sa.Integer(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["deleted_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["department_category_id"], ["departmentcategories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["literature_category_id"], ["literaturecategories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["publisher_id"], ["publishers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bookmasters_id"), "bookmasters", ["id"], unique=False)
    op.create_index(op.f("ix_bookmasters_title"), "bookmasters", ["title"], unique=False)
    op.create_index(op.f("ix_bookmasters_unique_title"), "bookmasters", ["unique_title"], unique=False)
    op.create_index(op.f("ix_bookmasters_isbn"), "bookmasters", ["isbn"], unique=False)
    op.create_index(op.f("ix_bookmasters_issn"), "bookmasters", ["issn"], unique=False)
    op.create_index(op.f("ix_bookmasters_is_deleted"), "bookmasters", ["is_deleted"], unique=False)

    op.create_table(
        "bookauthors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("book_master_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("author_order", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.ForeignKeyConstraint(["author_id"], ["authors.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["book_master_id"], ["bookmasters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("book_master_id", "author_id", name="uq_bookauthors_book_author"),
    )
    op.create_index(op.f("ix_bookauthors_id"), "bookauthors", ["id"], unique=False)

    op.create_table(
        "bookcopies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("accession_number", sa.String(length=80), nullable=False),
        sa.Column("book_master_id", sa.Integer(), nullable=False),
        sa.Column("copy_number", sa.Integer(), nullable=False),
        sa.Column("barcode_value", sa.String(length=120), nullable=True),
        sa.Column("rack", sa.String(length=80), nullable=True),
        sa.Column("shelf", sa.String(length=80), nullable=True),
        sa.Column("location", sa.String(length=120), nullable=True),
        sa.Column("hall", sa.String(length=80), nullable=True),
        sa.Column("physical_condition", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("current_holder_type", sa.String(length=40), nullable=True),
        sa.Column("current_holder_reference", sa.String(length=120), nullable=True),
        sa.Column("last_issue_date", sa.Date(), nullable=True),
        sa.Column("last_receive_date", sa.Date(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("deleted_reason", sa.String(length=255), nullable=True),
        sa.Column("deleted_by_user_id", sa.Integer(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["book_master_id"], ["bookmasters.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["deleted_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bookcopies_id"), "bookcopies", ["id"], unique=False)
    op.create_index(op.f("ix_bookcopies_accession_number"), "bookcopies", ["accession_number"], unique=True)
    op.create_index(op.f("ix_bookcopies_status"), "bookcopies", ["status"], unique=False)
    op.create_index(op.f("ix_bookcopies_is_deleted"), "bookcopies", ["is_deleted"], unique=False)
    op.create_unique_constraint("uq_bookcopies_barcode_value", "bookcopies", ["barcode_value"])


def downgrade() -> None:
    op.drop_constraint("uq_bookcopies_barcode_value", "bookcopies", type_="unique")
    op.drop_index(op.f("ix_bookcopies_is_deleted"), table_name="bookcopies")
    op.drop_index(op.f("ix_bookcopies_status"), table_name="bookcopies")
    op.drop_index(op.f("ix_bookcopies_accession_number"), table_name="bookcopies")
    op.drop_index(op.f("ix_bookcopies_id"), table_name="bookcopies")
    op.drop_table("bookcopies")
    op.drop_index(op.f("ix_bookauthors_id"), table_name="bookauthors")
    op.drop_table("bookauthors")
    op.drop_index(op.f("ix_bookmasters_is_deleted"), table_name="bookmasters")
    op.drop_index(op.f("ix_bookmasters_issn"), table_name="bookmasters")
    op.drop_index(op.f("ix_bookmasters_isbn"), table_name="bookmasters")
    op.drop_index(op.f("ix_bookmasters_unique_title"), table_name="bookmasters")
    op.drop_index(op.f("ix_bookmasters_title"), table_name="bookmasters")
    op.drop_index(op.f("ix_bookmasters_id"), table_name="bookmasters")
    op.drop_table("bookmasters")
    op.drop_index(op.f("ix_literaturecategories_name"), table_name="literaturecategories")
    op.drop_index(op.f("ix_literaturecategories_id"), table_name="literaturecategories")
    op.drop_table("literaturecategories")
    op.drop_index(op.f("ix_departmentcategories_name"), table_name="departmentcategories")
    op.drop_index(op.f("ix_departmentcategories_id"), table_name="departmentcategories")
    op.drop_table("departmentcategories")
    op.drop_index(op.f("ix_categories_name"), table_name="categories")
    op.drop_index(op.f("ix_categories_id"), table_name="categories")
    op.drop_table("categories")
    op.drop_index(op.f("ix_publishers_name"), table_name="publishers")
    op.drop_index(op.f("ix_publishers_id"), table_name="publishers")
    op.drop_table("publishers")
    op.drop_index(op.f("ix_authors_name"), table_name="authors")
    op.drop_index(op.f("ix_authors_id"), table_name="authors")
    op.drop_table("authors")

