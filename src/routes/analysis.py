"""Analysis routes — POST /analyze, GET /analysis/{id}."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.agents.analysis import AnalysisAgent
from src.auth import require_api_key
from src.database import get_db
from src.models.akd_mapping import AKDMapping
from src.models.analysis_result import AnalysisResult
from src.models.content_item import ContentItem
from src.schemas.analysis import AnalyzeRequest

logger = logging.getLogger(__name__)

router = APIRouter()
_agent = AnalysisAgent()


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_content(
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
    _api_key: str = Depends(require_api_key),
) -> dict[str, Any]:
    """Submit content for sentiment analysis and AKD classification.

    Performs sentiment analysis and AKD classification, then saves the
    ContentItem, AnalysisResult, and AKDMappings to the database.
    """
    logger.info(
        "Analysis requested",
        extra={"source_type": request.source_type},
    )

    # 1. Run Analysis Agent
    analysis_res = await _agent.analyze(request.content)

    # 2. Save ContentItem to DB
    content_item = ContentItem(
        source_type=request.source_type,
        source_name=request.source_name,
        content=request.content,
        title=request.title,
        url=request.url,
        published_at=request.published_at,
        collected_at=datetime.now(UTC),
    )
    db.add(content_item)
    db.flush()  # get content_item.id

    # 3. Save AnalysisResult to DB
    analysis_record = AnalysisResult(
        item_id=content_item.id,
        sentiment=analysis_res["sentiment"],
        sentiment_score=analysis_res["sentiment_score"],
        analyzed_at=datetime.now(UTC),
    )
    db.add(analysis_record)
    db.flush()  # get analysis_record.id

    # 4. Save AKDMappings to DB
    akd_mappings_data = analysis_res.get("akd_mappings", [])
    akd_records: list[dict[str, Any]] = []

    for mapping in akd_mappings_data:
        akd_rec = AKDMapping(
            item_id=content_item.id,
            akd_name=mapping["akd_name"],
            akd_type=mapping.get("akd_type", "Komisi"),
            confidence_score=mapping["confidence_score"],
            rank=mapping["rank"],
        )
        db.add(akd_rec)
        akd_records.append({
            "akd_name": mapping["akd_name"],
            "akd_type": mapping.get("akd_type", "Komisi"),
            "confidence_score": mapping["confidence_score"],
            "rank": mapping["rank"],
        })

    db.commit()

    logger.info(
        "Analysis completed and saved",
        extra={"item_id": content_item.id, "analysis_id": analysis_record.id},
    )

    return {
        "id": analysis_record.id,
        "item_id": content_item.id,
        "source_type": content_item.source_type,
        "sentiment": analysis_record.sentiment,
        "sentiment_score": analysis_record.sentiment_score,
        "akd_mappings": akd_records,
        "analyzed_at": analysis_record.analyzed_at.isoformat(),
    }


@router.get("/analysis/{analysis_id}")
async def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve a specific analysis result by ID."""
    logger.info("Analysis result requested", extra={"analysis_id": analysis_id})

    analysis_record = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.id == analysis_id)
        .first()
    )
    if not analysis_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis result with id {analysis_id} not found",
        )

    # Fetch item and AKD mappings
    item = analysis_record.content_item
    akd_mappings = (
        db.query(AKDMapping)
        .filter(AKDMapping.item_id == item.id)
        .order_by(AKDMapping.rank.asc())
        .all()
    )

    return {
        "id": analysis_record.id,
        "item_id": item.id,
        "source_type": item.source_type,
        "source_name": item.source_name,
        "content_preview": item.content[:150] + "..." if len(item.content) > 150 else item.content,
        "url": item.url,
        "sentiment": analysis_record.sentiment,
        "sentiment_score": analysis_record.sentiment_score,
        "analyzed_at": analysis_record.analyzed_at.isoformat(),
        "akd_mappings": [
            {
                "akd_name": m.akd_name,
                "akd_type": m.akd_type,
                "confidence_score": m.confidence_score,
                "rank": m.rank,
            }
            for m in akd_mappings
        ],
    }
