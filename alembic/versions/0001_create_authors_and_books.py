"""create authors and books tables

Revision ID: 0001
Revises:
Create Date: 2026-09-18

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.UniqueConstraint("email", name="uq_authors_email"),
    )
    op.create_index(op.f("ix_authors_id"), "authors", ["id"])

    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column(
            "author_id",
            sa.Integer(),
            sa.ForeignKey("authors.id"),
            nullable=False,
        ),
    )
    op.create_index(op.f("ix_books_id"), "books", ["id"])
    op.create_index(op.f("ix_books_title"), "books", ["title"])


def downgrade() -> None:
    op.drop_index(op.f("ix_books_title"), table_name="books")
    op.drop_index(op.f("ix_books_id"), table_name="books")
    op.drop_table("books")

    op.drop_index(op.f("ix_authors_id"), table_name="authors")
    op.drop_table("authors")
