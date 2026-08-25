# -*- coding: utf-8 -*-
"""Unit tests for FastAPI Agent routes (/api/v1/agents)."""

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_list_tools_endpoint():
    """Verify GET /api/v1/agents/tools returns all dynamic tools."""
    resp = client.get("/api/v1/agents/tools")
    assert resp.status_code == 200
    data = resp.json()
    assert "count" in data
    assert data["count"] == 5
    assert "tools" in data
    names = [t["name"] for t in data["tools"]]
    assert "fetch_rss_tool" in names
    assert "classify_akd_tool" in names


def test_feeds_health_endpoint():
    """Verify GET /api/v1/agents/health/feeds returns feed probe report."""
    resp = client.get("/api/v1/agents/health/feeds")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_feeds" in data
    assert data["total_feeds"] >= 10
    assert "healthy_feeds" in data
    assert "feeds" in data


def test_run_agent_pipeline_endpoint():
    """Verify POST /api/v1/agents/run executes the LangGraph supervisor workflow."""
    payload = {
        "task_type": "quick_scan",
        "articles": [
            {
                "title": "Komisi I Bahas Anggaran Siber BSSN",
                "content": "Komisi I DPR RI menggelar rapat kerja dengan BSSN membahas anggaran siber.",
                "url": "https://example.com/komisi-1-siber-test",
                "published_at": "2026-08-25T10:00:00+07:00",
                "source_type": "news_online",
                "source_name": "Antara",
            }
        ],
        "z_threshold": 3.0,
        "critique_threshold": 0.75,
        "max_critique_iterations": 2,
    }
    resp = client.post("/api/v1/agents/run", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["status"] in ("completed", "completed_with_warnings")
    assert "data" in data
    assert len(data["data"]["analyzed_items"]) == 1
    assert len(data["data"]["recommendations"]) >= 1
