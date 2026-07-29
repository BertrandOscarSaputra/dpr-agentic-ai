"""Fix DateTime columns to use TIMESTAMPTZ and add missing columns.

Ensures all DateTime columns store timezone-aware timestamps (TIMESTAMPTZ)
instead of naive timestamps (TIMESTAMP). Also adds:
- content_items.source_name (media outlet name)
- recommendations.trend_window_id (FK to trend_windows)

Revision ID: 002_fix_timestamptz
Revises: 001_initial
Create Date: 2026-07-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002_fix_timestamptz"
down_revision: str = "001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# All (table, column) pairs that need TIMESTAMP -> TIMESTAMPTZ
DATETIME_COLUMNS = [
    ("content_items", "published_at"),
    ("content_items", "collected_at"),
    ("content_items", "created_at"),
    ("item_analysis", "analyzed_at"),
    ("akd_mapping", "created_at"),
    ("trend_windows", "window_start"),
    ("trend_windows", "window_end"),
    ("trend_windows", "created_at"),
    ("recommendations", "reviewed_at"),
    ("recommendations", "created_at"),
]


def upgrade() -> None:
    # 1. Alter all DateTime columns to TIMESTAMPTZ
    for table, column in DATETIME_COLUMNS:
        op.alter_column(
            table,
            column,
            type_=sa.DateTime(timezone=True),
            existing_type=sa.DateTime(),
            existing_nullable=True,
        )

    # 2. Add missing source_name column to content_items
    op.add_column(
        "content_items",
        sa.Column("source_name", sa.String(200), nullable=True),
    )

    # 3. Add missing trend_window_id FK to recommendations
    op.add_column(
        "recommendations",
        sa.Column(
            "trend_window_id",
            sa.Integer,
            sa.ForeignKey("trend_windows.id"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    # Remove added columns
    op.drop_column("recommendations", "trend_window_id")
    op.drop_column("content_items", "source_name")

    # Revert TIMESTAMPTZ back to TIMESTAMP
    for table, column in DATETIME_COLUMNS:
        op.alter_column(
            table,
            column,
            type_=sa.DateTime(),
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=True,
        )
