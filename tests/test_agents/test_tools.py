# -*- coding: utf-8 -*-
"""Unit tests for Dynamic Tool Registry (src/agents/tools.py)."""

import pytest

from src.agents.tools import (
    ALL_AGENTIC_TOOLS,
    analyze_sentiment_tool,
    calculate_zscore_tool,
    classify_akd_tool,
    fetch_rss_tool,
    lookup_akd_metadata_tool,
)


class TestDynamicTools:
    """Test suite for @tool decorated multi-agent tools."""

    def test_tool_registry_completeness(self) -> None:
        """Verify all 5 core agent tools are present in registry."""
        assert len(ALL_AGENTIC_TOOLS) == 5
        tool_names = [t.name for t in ALL_AGENTIC_TOOLS]
        assert "fetch_rss_tool" in tool_names
        assert "classify_akd_tool" in tool_names
        assert "analyze_sentiment_tool" in tool_names
        assert "calculate_zscore_tool" in tool_names
        assert "lookup_akd_metadata_tool" in tool_names

    def test_analyze_sentiment_tool(self) -> None:
        """Test sentiment analysis tool output structure."""
        text = "Pemerintah dan DPR RI sepakat meningkatkan anggaran pendidikan nasional secara transparan."
        result = analyze_sentiment_tool.invoke({"text": text})
        assert "sentiment" in result
        assert "sentiment_score" in result
        assert "confidence" in result
        assert result["sentiment"].lower() in ["positif", "negatif", "netral"]

    def test_classify_akd_tool(self) -> None:
        """Test AKD classification tool output."""
        text = "Komisi I DPR RI menggelar rapat kerja membahas pertahanan siber bersama Menhan."
        result = classify_akd_tool.invoke({"text": text})
        assert isinstance(result, list)
        assert len(result) > 0
        assert any(m["akd_name"] == "Komisi I" for m in result)

    def test_calculate_zscore_tool_normal(self) -> None:
        """Test Z-score calculator with non-anomalous baseline."""
        counts = [10, 12, 11, 10, 13, 11, 12]
        result = calculate_zscore_tool.invoke({"daily_counts": counts, "current_count": 12})
        assert result["is_anomaly"] is False
        assert result["z_score"] < 2.0

    def test_calculate_zscore_tool_anomaly(self) -> None:
        """Test Z-score calculator triggers anomaly on significant spike."""
        counts = [10, 10, 11, 10, 12, 10, 11]
        result = calculate_zscore_tool.invoke({"daily_counts": counts, "current_count": 50})
        assert result["is_anomaly"] is True
        assert result["z_score"] > 2.0

    def test_lookup_akd_metadata_tool(self) -> None:
        """Test AKD master taxonomy lookup tool."""
        res_found = lookup_akd_metadata_tool.invoke({"akd_name": "Komisi I"})
        assert res_found["found"] is True
        assert res_found["akd_name"] == "Komisi I"
        assert "metadata" in res_found

        res_not_found = lookup_akd_metadata_tool.invoke({"akd_name": "Komisi Non-Existent"})
        assert res_not_found["found"] is False
