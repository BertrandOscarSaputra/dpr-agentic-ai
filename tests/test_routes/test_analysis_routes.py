"""Tests for analysis API routes."""

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

    def test_analyze_accepts_valid_payload(self, client: TestClient) -> None:
        """POST /api/v1/analyze should accept valid content."""
        response = client.post(
            "/api/v1/analyze",
            json={"content": "DPR RI membahas RUU reformasi hukum", "source_type": "manual"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"

    def test_analyze_rejects_short_content(self, client: TestClient) -> None:
        """POST /api/v1/analyze should reject content shorter than 10 chars."""
        response = client.post(
            "/api/v1/analyze",
            json={"content": "short", "source_type": "manual"},
        )
        assert response.status_code == 422

    def test_get_analysis_by_id(self, client: TestClient) -> None:
        """GET /api/v1/analysis/{id} should return a result dict."""
        response = client.get("/api/v1/analysis/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
