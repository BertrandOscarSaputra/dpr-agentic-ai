"""Tests for analysis Pydantic schemas."""

import pytest
from pydantic import ValidationError

from src.schemas.analysis import AnalysisResultCreate, AnalyzeRequest


class TestAnalyzeRequest:
    """Test the POST /analyze request schema validation."""

    def test_valid_request(self) -> None:
        req = AnalyzeRequest(
            content="This is valid content for analysis by the system",
            source_type="manual",
        )
        assert req.source_type == "manual"
        assert len(req.content) >= 10

    def test_default_source_type(self) -> None:
        req = AnalyzeRequest(content="Valid content with enough characters for analysis")
        assert req.source_type == "manual"

    def test_content_too_short_raises(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeRequest(content="short")
        errors = str(exc_info.value).lower()
        assert "min_length" in errors or "too_short" in errors

    def test_empty_content_raises(self) -> None:
        with pytest.raises(ValidationError):
            AnalyzeRequest(content="")


class TestAnalysisResultCreate:
    """Test the analysis result creation schema."""

    def test_valid_result(self) -> None:
        result = AnalysisResultCreate(
            item_id=1,
            sentiment="Positif",
            sentiment_score=0.85,
        )
        assert result.sentiment == "Positif"
        assert result.sentiment_score == 0.85

    def test_sentiment_score_bounds(self) -> None:
        with pytest.raises(ValidationError):
            AnalysisResultCreate(item_id=1, sentiment="Positif", sentiment_score=1.5)

        with pytest.raises(ValidationError):
            AnalysisResultCreate(item_id=1, sentiment="Negatif", sentiment_score=-1.5)

    def test_boundary_scores_valid(self) -> None:
        pos = AnalysisResultCreate(item_id=1, sentiment="Positif", sentiment_score=1.0)
        neg = AnalysisResultCreate(item_id=1, sentiment="Negatif", sentiment_score=-1.0)
        assert pos.sentiment_score == 1.0
        assert neg.sentiment_score == -1.0
