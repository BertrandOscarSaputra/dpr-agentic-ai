# -*- coding: utf-8 -*-
"""FastAPI REST API routes for LangGraph Supervisor Agent and Multi-Agent Tool Registry."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.agents.news_collection import NewsCollectionAgent
from src.agents.supervisor import SupervisorAgent
from src.agents.tools import ALL_AGENTIC_TOOLS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentRunRequest(BaseModel):
    """Payload for triggering the LangGraph multi-agent workflow."""

    task_type: str = Field(default="full_analysis", description="Task type (e.g. 'full_analysis', 'quick_scan')")
    content: str = Field(default="", description="Optional direct text content to process")
    articles: list[dict[str, Any]] = Field(default_factory=list, description="Optional pre-ingested articles")
    z_threshold: float = Field(default=2.0, ge=0.5, le=5.0, description="Z-score threshold for anomaly detection")
    critique_threshold: float = Field(default=0.75, ge=0.0, le=1.0, description="Quality score threshold for recommendation critique loop")
    max_critique_iterations: int = Field(default=3, ge=1, le=5, description="Max allowed self-correction critique loops")


@router.post("/run")
async def run_supervisor_pipeline(req: AgentRunRequest) -> dict[str, Any]:
    """Execute the full autonomous multi-agent LangGraph workflow.

    Runs nodes:
    1. collect (NewsCollectionAgent)
    2. analyze (AnalysisAgent with 3-tier matching)
    3. trend (TrendAgent with Z-score calculation)
    4. anomaly_critique (Conditional: audits spikes if Z >= threshold)
    5. insight (InsightAgent narrative synthesis)
    6. recommend (RecommendationAgent policy strategy)
    7. critique_validator (Self-Correction loop if score < threshold)
    """
    logger.info("Triggering LangGraph supervisor pipeline", extra={"task_type": req.task_type})
    supervisor = SupervisorAgent(
        z_threshold=req.z_threshold,
        critique_threshold=req.critique_threshold,
        max_critique_iterations=req.max_critique_iterations,
    )

    task_dict = {
        "type": req.task_type,
        "content": req.content,
        "articles": req.articles,
    }

    try:
        result = await supervisor.run(task_dict)
        return {
            "success": True,
            "status": result.get("status", "completed"),
            "data": result,
        }
    except Exception as exc:
        logger.error("Supervisor pipeline execution failed", extra={"error": str(exc)})
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(exc)}") from exc


@router.get("/health/feeds")
def get_rss_feeds_health() -> dict[str, Any]:
    """Probe all configured RSS media feeds and return live availability and health status."""
    logger.info("Probing live RSS feeds health")
    agent = NewsCollectionAgent()
    health_list = agent.check_all_feeds_health()

    healthy_count = sum(1 for h in health_list if h.get("status") == "HEALTHY")
    dead_count = sum(1 for h in health_list if h.get("status") in ("DEAD", "UNREACHABLE"))

    return {
        "total_feeds": len(health_list),
        "healthy_feeds": healthy_count,
        "dead_or_unreachable_feeds": dead_count,
        "feeds": health_list,
    }


@router.get("/tools")
def list_available_tools() -> dict[str, Any]:
    """List all registered dynamic tools available to LangGraph sub-agents."""
    tools_meta = [
        {
            "name": t.name,
            "description": t.description,
            "args_schema": str(t.args) if hasattr(t, "args") else None,
        }
        for t in ALL_AGENTIC_TOOLS
    ]
    return {
        "count": len(tools_meta),
        "tools": tools_meta,
    }
