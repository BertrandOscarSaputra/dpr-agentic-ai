# Technical Setup Guide — DPR Agentic AI

## Prerequisites

- **Python 3.11+** (managed via `uv`)
- **uv** — [Install guide](https://docs.astral.sh/uv/getting-started/installation/)
- **Docker & Docker Compose** 25+
- **Git** 2.40+

## Quick Start with `uv`

```bash
# 1. Clone repository
git clone https://github.com/USERNAME/dpr-agentic-ai.git
cd dpr-agentic-ai

# 2. Install all dependencies (including dev tools)
uv sync

# 3. Copy environment template
cp .env.example .env
# Edit .env with your API keys (especially GEMINI_API_KEY)

# 4. Start infrastructure (Postgres + Redis)
docker compose up -d postgres redis

# 5. Run database migrations
uv run alembic upgrade head

# 6. Start the API server
uv run uvicorn src.main:app --reload

# 7. Start the dashboard (in a separate terminal)
uv run streamlit run dashboard/app.py

# 8. Start Celery worker (in a separate terminal)
uv run celery -A src.tasks worker --loglevel=info
```

## Full Docker Setup

```bash
# Start all services (API + Dashboard + Postgres + Redis + Celery)
cp .env.example .env
# Edit .env with your GEMINI_API_KEY
docker compose up -d

# Verify
curl http://localhost:8000/health
# → {"status": "ok", "environment": "development"}

# Access
# API:       http://localhost:8000
# API Docs:  http://localhost:8000/docs
# Dashboard: http://localhost:8501
```

## Common `uv` Commands

```bash
# Add a new dependency
uv add <package-name>

# Add a dev-only dependency
uv add --dev <package-name>

# Run a command in the project environment
uv run <command>

# Run tests
uv run pytest tests/ -v

# Run linting
uv run ruff check src/

# Update lock file
uv lock

# Sync after pulling changes
uv sync
```

## Database

```bash
# Run migrations
uv run alembic upgrade head

# Create new migration
uv run alembic revision --autogenerate -m "description"

# Rollback last migration
uv run alembic downgrade -1
```

## Environment Variables

See `.env.example` for all available configuration options.

Required for basic operation:
- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` — Redis connection string
- `GEMINI_API_KEY` — Google Gemini API key
