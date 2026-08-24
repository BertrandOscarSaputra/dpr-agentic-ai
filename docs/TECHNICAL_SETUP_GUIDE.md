# Technical Setup & Deployment Guide — DPR Agentic AI

## Overview

This guide provides step-by-step instructions for installing, configuring, running, and deploying the **DPR Agentic AI** platform. It covers local development setup using `uv`, environment configuration, database migrations, running batch data pipelines, local API/Dashboard execution, and production Docker containerization.

---

## Prerequisites

Ensure your development environment meets the following software requirements:

- **Operating System**: Windows 11 / Linux (Ubuntu 22.04+) / macOS Sonoma
- **Python**: Version 3.11 or higher (Python 3.11.9 recommended)
- **`uv` Package Manager**: Fast Python package installer and venv manager (`curl -sSf https://astral.sh/uv/install.ps1 | iex` on Windows)
- **PostgreSQL**: Version 15 or 16
- **Redis**: Version 7.0 or higher
- **Docker & Docker Compose**: (Optional, for containerized deployment)

---

## 1. Environment Configuration

Copy the example environment file `.env.example` to `.env` in the root workspace directory:

```bash
cp .env.example .env
```

Open `.env` and configure the required environment variables:

```env
# Database Configuration
DATABASE_URL=postgresql://dpr_user:dpr_dev_password@localhost:5432/dpr_agentic_ai
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis Cache & Broker Configuration
REDIS_URL=redis://localhost:6379

# AI & External API Keys
GEMINI_API_KEY=AIzaSyAOPPA_your_valid_gemini_api_key_here
HUGGINGFACE_API_KEY=

# X / Twitter Scraping Configuration (Scrapfly Web Scraper)
SCRAPFLY_KEY=scp-live-your_scrapfly_api_key_here
X_USERNAME="totoropoporo123"
X_EMAIL="totoropoporo123@gmail.com"
X_PASSWORD="YourPasswordHere"
X_COOKIES_PATH=cookies.json

# Application Runtime Configuration
ENV=development
DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=dev-secret-key-dpr-agentic-ai

# Celery Task Queue
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379

# Authentication (Comma-separated API keys for API endpoints)
API_KEYS=[]
```

---

## 2. Virtual Environment & Dependency Installation

Using `uv`, initialize the virtual environment and install all locked dependencies from `uv.lock`:

```bash
# 1. Create Python 3.11 virtual environment
uv venv .venv --python 3.11

# 2. Sync all project dependencies
uv sync
```

To activate the virtual environment manually (if needed):
- **Windows PowerShell**: `.venv\Scripts\Activate.ps1`
- **Linux/macOS**: `source .venv/bin/activate`

---

## 3. Database Initialization & Migrations

Ensure PostgreSQL server is running and create the database `dpr_agentic_ai`:

```sql
CREATE DATABASE dpr_agentic_ai;
CREATE USER dpr_user WITH PASSWORD 'dpr_dev_password';
GRANT ALL PRIVILEGES ON DATABASE dpr_agentic_ai TO dpr_user;
```

Run Alembic migrations to apply the latest database schema:

```bash
# Apply migrations to database
uv run alembic upgrade head
```

To check current migration revision:

```bash
uv run alembic current
```

---

## 4. Running Test Suite

Verify that all 100+ unit and integration tests pass cleanly:

```bash
uv run pytest tests/ -v
```

Expected output:
```text
====================== 101 passed in 13.50s ======================
```

---

## 5. Running Data Ingestion & Batch Analysis Pipelines

### Step A: Collect Live Online News (RSS Feeds)
Fetches live articles from 12+ Indonesian Tier-1 news portals, deduplicates by URL/Title, and saves partitioned daily JSON outputs:

```bash
uv run run_news_collection.py
```
Outputs generated in: `data/news/news_YYYY-MM-DD.json` and `data/news/news_output.json`.

### Step B: Collect Real X/Twitter Discourse (Scrapfly API)
Scrapes public tweets matching official DPR RI and AKD search queries:

```bash
uv run run_twitter_collection.py
```
Outputs generated in: `data/tweets/tweets_YYYY-MM-DD.json` and `data/tweets/tweets_output.json`.

### Step C: Execute 2-Tier AI Sentiment & AKD Classification Batch Engine
Analyzes raw articles/tweets using Tier-1 Fast Matcher and Tier-2 Gemini LLM Zero-Shot AI:

```bash
# Run full batch analysis:
uv run run_analysis_batch.py

# Run small test batch (e.g. 10 items):
uv run run_analysis_batch.py --limit 10
```
Outputs generated in: `data/analysis/analysis_YYYY-MM-DD.json` and `data/analysis/analysis_output.json`.

---

## 6. Running Local Development Services

### A. FastAPI Backend REST API Server
Start the FastAPI server on `http://localhost:8000`:

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```
- **API Documentation**: Open `http://localhost:8000/docs` in your browser for Interactive OpenAPI (Swagger) UI.

### B. Streamlit Executive Dashboard
Start the Streamlit Executive Dashboard UI on `http://localhost:8501`:

```bash
uv run streamlit run dashboard/app.py
```

---

## 7. Docker & Production Containerization

The repository includes multi-stage Dockerfiles for production container deployment:

### Build and Run with Docker Compose

```bash
# Build and start PostgreSQL, Redis, FastAPI Backend, and Streamlit Dashboard
docker-compose up --build -d
```

### Container Port Mappings:
- **FastAPI REST API**: `http://localhost:8000`
- **Streamlit Executive Dashboard**: `http://localhost:8501`
- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`

To view container logs:

```bash
docker-compose logs -f backend dashboard
```

To stop all services:

```bash
docker-compose down
```

---

## 8. Production Security & Performance Hardening

1. **Environment Variables**: Never commit `.env` containing production secrets to version control.
2. **Reverse Proxy & SSL**: Deploy Nginx or Traefik in front of FastAPI (port 8000) and Streamlit (port 8501) with SSL certificates (Let's Encrypt / Certbot).
3. **Database Connection Pooling**: Ensure `DATABASE_POOL_SIZE` is set appropriately according to available database RAM.
4. **Redis Cache TTL**: Set suitable Redis cache eviction policies for high-frequency dashboard queries.
