# System Architecture

## Overview

DPR Agentic AI is a multi-agent system for classifying parliamentary content (AKD — Alat Kelengkapan Dewan) and analyzing public sentiment toward DPR RI.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                   │
│                    (localhost:8501)                       │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP
┌──────────────────────▼──────────────────────────────────┐
│                     FastAPI (API)                        │
│                    (localhost:8000)                       │
│  ┌──────────┐  ┌────────────┐  ┌──────────────────────┐ │
│  │ /analyze │  │ /recommend │  │ /trends  /reports    │ │
│  └────┬─────┘  └─────┬──────┘  └──────────┬───────────┘ │
└───────┼──────────────┼─────────────────────┼────────────┘
        │              │                     │
┌───────▼──────────────▼─────────────────────▼────────────┐
│                  LangGraph Supervisor                    │
│  ┌─────────┐ ┌──────────┐ ┌───────┐ ┌────────────────┐ │
│  │Collect  │ │ Analysis │ │ Trend │ │ Insight/Report │ │
│  │Agent    │ │ Agent    │ │ Agent │ │ Agent          │ │
│  └────┬────┘ └────┬─────┘ └───┬───┘ └───────┬────────┘ │
└───────┼───────────┼───────────┼──────────────┼──────────┘
        │           │           │              │
   ┌────▼────┐ ┌────▼─────┐    │         ┌────▼─────┐
   │ Twitter │ │ IndoBERT │    │         │ Gemini   │
   │ RSS     │ │ Gemini   │    │         │ API      │
   └─────────┘ └──────────┘    │         └──────────┘
                          ┌────▼──────────────────────┐
                          │  PostgreSQL  │   Redis     │
                          └───────────────────────────┘
```

## Components

- **FastAPI**: REST API layer
- **LangGraph**: Multi-agent orchestration
- **IndoBERT**: Indonesian sentiment analysis
- **Gemini**: Zero-shot AKD classification & summarization
- **Celery + Redis**: Async task queue
- **PostgreSQL**: Persistent storage
- **Streamlit**: Data visualization dashboard

<!-- TODO: Add detailed component diagrams and data flow -->
