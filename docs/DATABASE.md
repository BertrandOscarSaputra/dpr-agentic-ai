# Database Documentation

## Schema Overview

| Table | Description |
|-------|-------------|
| `content_items` | Collected content from Twitter and news sources |
| `item_analysis` | Sentiment analysis results per content item |
| `akd_mapping` | Multi-label AKD classification (max 3 per item) |
| `trend_windows` | Time-windowed volume + anomaly detection per AKD |
| `recommendations` | AI-generated recommendations with review status |

## Migrations

Using Alembic for database migrations:

```bash
# Apply all migrations
uv run alembic upgrade head

# Create new migration (after model changes)
uv run alembic revision --autogenerate -m "description"

# Rollback
uv run alembic downgrade -1
```

<!-- TODO: Add ER diagram and detailed field documentation -->
