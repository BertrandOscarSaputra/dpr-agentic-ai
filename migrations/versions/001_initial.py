"""Initial schema — content_items, item_analysis, akd_mapping, trend_windows, recommendations.

All DateTime columns use TIMESTAMP WITH TIME ZONE (timestamptz) to ensure
timezone-aware storage, matching the ORM model definitions.

Revision ID: 001_initial
Revises: None
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # content_items table
    op.create_table(
        "content_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("source_name", sa.String(200)),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("title", sa.String(500)),
        sa.Column("url", sa.String(1000)),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column(
            "collected_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("url", name="uq_content_items_url"),
    )

    # item_analysis table
    op.create_table(
        "item_analysis",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "item_id",
            sa.Integer,
            sa.ForeignKey("content_items.id"),
            nullable=False,
        ),
        sa.Column("sentiment", sa.String(20), nullable=False),
        sa.Column("sentiment_score", sa.Float, nullable=False),
        sa.Column(
            "analyzed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # akd_mapping table
    op.create_table(
        "akd_mapping",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "item_id",
            sa.Integer,
            sa.ForeignKey("content_items.id"),
            nullable=False,
        ),
        sa.Column("akd_name", sa.String(50), nullable=False),
        sa.Column("akd_type", sa.String(50)),
        sa.Column("confidence_score", sa.Float, nullable=False),
        sa.Column("rank", sa.Integer, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "item_id", "akd_name", name="uq_akd_mapping_item_akd"
        ),
    )

    # trend_windows table
    op.create_table(
        "trend_windows",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("akd_name", sa.String(50), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("item_count", sa.Integer, default=0),
        sa.Column("z_score", sa.Float),
        sa.Column("is_anomaly", sa.Boolean, default=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # recommendations table
    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("akd_name", sa.String(50), nullable=False),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("recommendation", sa.Text, nullable=False),
        sa.Column("status", sa.String(20), default="draft"),
        sa.Column("reviewed_by", sa.String(100)),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "trend_window_id",
            sa.Integer,
            sa.ForeignKey("trend_windows.id"),
            nullable=True,
        ),
    )

    # Indexes
    op.create_index(
        "ix_content_items_source_type", "content_items", ["source_type"]
    )
    op.create_index(
        "ix_item_analysis_sentiment", "item_analysis", ["sentiment"]
    )
    op.create_index(
        "ix_akd_mapping_akd_name", "akd_mapping", ["akd_name"]
    )
    op.create_index(
        "ix_trend_windows_anomaly", "trend_windows", ["is_anomaly"]
    )
    op.create_index(
        "ix_recommendations_status", "recommendations", ["status"]
    )


def downgrade() -> None:
    op.drop_index("ix_recommendations_status")
    op.drop_index("ix_trend_windows_anomaly")
    op.drop_index("ix_akd_mapping_akd_name")
    op.drop_index("ix_item_analysis_sentiment")
    op.drop_index("ix_content_items_source_type")
    op.drop_table("recommendations")
    op.drop_table("trend_windows")
    op.drop_table("akd_mapping")
    op.drop_table("item_analysis")
    op.drop_table("content_items")
