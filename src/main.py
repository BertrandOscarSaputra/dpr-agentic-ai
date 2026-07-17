"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.logging_config import setup_logging
from src.routes import analysis, recommendations, reports, trends

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    setup_logging()

    app = FastAPI(
        title="DPR Agentic AI",
        description="Agentic AI untuk klasifikasi AKD & sentimen DPR RI",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware for dashboard and frontend access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8501",  # Streamlit dashboard (local dev)
            "http://dashboard:8501",  # Docker service name
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])
    app.include_router(recommendations.router, prefix="/api/v1", tags=["Recommendations"])
    app.include_router(trends.router, prefix="/api/v1", tags=["Trends"])
    app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "ok", "environment": settings.ENV}

    logger.info("Application started", extra={"environment": settings.ENV})
    return app


app = create_app()


def start() -> None:
    """Entry point for the `dpr-api` CLI script."""
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENV == "development",
    )
