# 🏛️ DPR Agentic AI

**Agentic AI untuk Klasifikasi AKD & Analisis Sentimen DPR RI**

[![CI](https://github.com/USERNAME/dpr-agentic-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/dpr-agentic-ai/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

---

## Overview

Sistem multi-agent berbasis AI yang secara otomatis:
1. **Mengumpulkan** konten dari Twitter/X dan berita online
2. **Menganalisis** sentimen menggunakan IndoBERT
3. **Mengklasifikasikan** ke AKD (Alat Kelengkapan Dewan) dengan Gemini zero-shot
4. **Mendeteksi** anomali tren per AKD menggunakan z-score
5. **Menghasilkan** rekomendasi dan laporan PDF

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Uvicorn |
| AI/ML | IndoBERT, Google Gemini, LangGraph |
| Database | PostgreSQL 15 |
| Cache/Queue | Redis 7 + Celery |
| Dashboard | Streamlit + Plotly |
| Package Manager | uv |
| Container | Docker + Docker Compose |

## Quick Start

```bash
# Install dependencies
uv sync

# Setup environment
cp .env.example .env
# Edit .env with your GEMINI_API_KEY

# Start infrastructure
docker compose up -d postgres redis

# Run migrations
uv run alembic upgrade head

# Start API
uv run uvicorn src.main:app --reload
```

See [docs/SETUP.md](docs/SETUP.md) for the full setup guide.

## Project Structure

```
src/             # Application source code
├── agents/      # LangGraph agent modules
├── models/      # SQLAlchemy ORM models
├── schemas/     # Pydantic validation schemas
├── routes/      # FastAPI route handlers
├── tasks/       # Celery async tasks
└── utils/       # Shared utilities
tests/           # Test suite
dashboard/       # Streamlit dashboard
migrations/      # Alembic database migrations
kamus/           # AKD reference data
docs/            # Documentation
```

## Documentation

- [Setup Guide](docs/SETUP.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Database Schema](docs/DATABASE.md)
- [Agent Design](docs/AGENTS.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE) for details.
