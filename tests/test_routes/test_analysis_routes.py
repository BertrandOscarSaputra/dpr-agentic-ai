"""Tests for analysis API routes."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_returns_ok(self, client: TestClient) -> None:
        """GET /health should return status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestAnalysisRoutes:
    """Test the analysis API routes."""

    def test_analyze_accepts_valid_payload(
        self, client: TestClient, mock_db: MagicMock,
    ) -> None:
        """POST /api/v1/analyze should accept valid content and return analysis result."""
        # Mocking ID assignment on DB model flush
        def flush_side_effect():
            # The route creates ContentItem first, then AnalysisResult
            pass

        mock_db.flush.side_effect = flush_side_effect

        response = client.post(
            "/api/v1/analyze",
            json={
                "content": "DPR RI membahas RUU reformasi hukum nasional",
                "source_type": "manual",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "sentiment" in data
        assert "sentiment_score" in data
        assert "akd_mappings" in data

    def test_analyze_rejects_short_content(self, client: TestClient) -> None:
        """POST /api/v1/analyze should reject content shorter than 10 chars."""
        response = client.post(
            "/api/v1/analyze",
            json={"content": "short", "source_type": "manual"},
        )
        assert response.status_code == 422

    def test_get_analysis_by_id_success(
        self, client: TestClient, mock_db: MagicMock,
    ) -> None:
        """GET /api/v1/analysis/{id} should return stored result when found."""
        mock_item = MagicMock()
        mock_item.id = 1
        mock_item.source_type = "manual"
        mock_item.source_name = "User"
        mock_item.content = "DPR RI membahas RUU reformasi hukum"
        mock_item.url = None

        mock_record = MagicMock()
        mock_record.id = 1
        mock_record.content_item = mock_item
        mock_record.sentiment = "Positif"
        mock_record.sentiment_score = 0.75
        mock_record.analyzed_at = datetime(2026, 7, 29, 12, 0, 0, tzinfo=UTC)

        mock_mapping = MagicMock()
        mock_mapping.akd_name = "Komisi III"
        mock_mapping.akd_type = "Komisi"
        mock_mapping.confidence_score = 0.85
        mock_mapping.rank = 1

        # mock_db query chain
        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.first.return_value = mock_record
        query_mock.all.return_value = [mock_mapping]
        mock_db.query.return_value = query_mock

        response = client.get("/api/v1/analysis/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["sentiment"] == "Positif"
        assert len(data["akd_mappings"]) == 1

    def test_get_analysis_by_id_not_found(
        self, client: TestClient, mock_db: MagicMock,
    ) -> None:
        """GET /api/v1/analysis/{id} should return 404 when not found."""
        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        mock_db.query.return_value = query_mock

        response = client.get("/api/v1/analysis/999")
        assert response.status_code == 404
