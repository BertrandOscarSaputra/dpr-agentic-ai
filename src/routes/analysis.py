"""Analysis routes — POST /analyze, GET /analysis/{id}."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth import require_api_key
from src.database import get_db
from src.schemas.analysis import AnalyzeRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze")
async def analyze_content(
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
    _api_key: str = Depends(require_api_key),
) -> dict:
    """Submit content for sentiment analysis and AKD classification."""
    logger.info("Analysis requested", extra={"source_type": request.source_type})
    # TODO: Implement via Analysis Agent
    return {"status": "queued", "message": "Analysis will be processed asynchronously"}


@router.get("/analysis/{analysis_id}")
async def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Retrieve a specific analysis result by ID."""
    logger.info("Analysis result requested", extra={"analysis_id": analysis_id})
    # TODO: Query AnalysisResult + AKDMapping
    return {"id": analysis_id, "status": "not_implemented"}
