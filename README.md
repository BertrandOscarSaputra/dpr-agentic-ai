# 🏛️ DPR Agentic AI

**Agentic AI untuk Klasifikasi AKD & Analisis Sentimen DPR RI**

[![CI](https://github.com/USERNAME/dpr-agentic-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/dpr-agentic-ai/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

---

## Overview

Sistem multi-agent berbasis AI yang secara otomatis:
1. **Mengumpulkan** konten dari 17+ portal berita media nasional Tier-1 (RSS Ingestion)
2. **Menganalisis** sentimen menggunakan IndoBERT (fine-tuned) & 3-tier cascade engine
3. **Mengklasifikasikan** ke 24 AKD (Alat Kelengkapan Dewan) DPR RI 2024–2029
4. **Mendeteksi** anomali tren per AKD menggunakan Sentiment-Weighted Damped Z-Score ($Z \ge 2.0$)
5. **Menghasilkan** rekomendasi aksi kebijakan dengan Self-Correction Reflection Loop & laporan PDF

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Uvicorn (Python 3.11+) |
| AI/ML | IndoBERT, Google Gemini (Gemini 3.6 Flash), LangGraph |
| Database | PostgreSQL 16 + SQLAlchemy 2.x |
| Cache/Queue | Redis 7 + Celery |
| Dashboard | Streamlit + Plotly |
| Package Manager | uv (Astral) |
| Container | Docker + Docker Compose |
| Test Suite | Pytest (102 Tests Passing — 100%) |

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
├── agents/      # LangGraph agent modules (Supervisor, Trend, Analysis, News, Recommendation)
├── models/      # SQLAlchemy ORM models
├── schemas/     # Pydantic validation schemas
├── routes/      # FastAPI route handlers
├── repositories/# Data access layer
├── tasks/       # Celery async tasks
└── utils/       # Shared utilities & benchmark evaluators
tests/           # Test suite (102 tests)
dashboard/       # Streamlit dashboard
kamus/           # AKD 2024-2029 reference taxonomy & feed configs
data/            # Partitioned daily datasets (news, analysis, annotations, benchmark)
docs/            # Documentation & sprint guides
```

## Documentation

- [Project Overview](docs/PROJECT_OVERVIEW.md)
- [Project Status](docs/PROJECT_STATUS.md)
- [Day-to-Day Timeline](docs/DAY_TO_DAY_TIMELINE.md)
- [Dokumentasi Resmi Model IndoBERT Final](docs/DOKUMENTASI_MODEL_INDOBERT_FINAL.md)
- [Panduan Operasional Sentimen (SI 1 & SI 2)](docs/PANDUAN_OPERASIONAL_SENTIMEN_SI1_SI2.md)
- [Panduan Task Informatika Sprint 6](docs/PANDUAN_TASK_INFORMATIKA_SPRINT_6.md)
- [Panduan Task Sistem Informasi Sprint 6](docs/PANDUAN_TASK_SISTEM_INFORMASI_SPRINT_6.md)
- [Architecture Blueprint](docs/ARCHITECTURE.md)
- [Agent Design](docs/AGENTS.md)
- [Database Schema](docs/DATABASE.md)
- [API Reference](docs/API.md)


## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE) for details.
