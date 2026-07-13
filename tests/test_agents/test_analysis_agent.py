"""Tests for the Analysis Agent."""

import pytest

from src.agents.analysis import AnalysisAgent


class TestAnalysisAgent:
    """Test suite for AnalysisAgent."""

    def test_agent_initializes(self) -> None:
        """Analysis agent should instantiate without errors."""
        agent = AnalysisAgent()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_analyze_returns_expected_structure(self) -> None:
        """analyze() should return a dict with sentiment and akd_mappings keys."""
        agent = AnalysisAgent()
        result = await agent.analyze("Contoh teks tentang DPR RI dan reformasi hukum")
        assert "sentiment" in result
        assert "sentiment_score" in result
        assert "akd_mappings" in result
        assert result["sentiment"] in {"Positif", "Negatif", "Netral"}
