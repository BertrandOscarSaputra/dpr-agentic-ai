"""Tests for AnalysisAgent (sentiment analysis & AKD classification)."""

from unittest.mock import AsyncMock, patch

import pytest

from src.agents.analysis import AnalysisAgent


class TestAnalysisAgent:
    """Test suite for AnalysisAgent."""

    def test_agent_initializes(self) -> None:
        """Analysis agent should instantiate without errors."""
        agent = AnalysisAgent()
        assert agent is not None
        assert len(agent.akd_list) > 0

    @pytest.mark.asyncio
    async def test_analyze_returns_expected_structure(self) -> None:
        """analyze() should return a dict with sentiment, score, and akd_mappings."""
        agent = AnalysisAgent()
        result = await agent.analyze("Komisi III DPR RI menyetujui RUU Hukum Pidana demi keadilan")
        assert "sentiment" in result
        assert "sentiment_score" in result
        assert "akd_mappings" in result
        assert result["sentiment"] in {"Positif", "Negatif", "Netral"}
        assert -1.0 <= result["sentiment_score"] <= 1.0

    def test_sentiment_positive_text(self) -> None:
        """Positive keywords should yield Positif sentiment and positive score."""
        agent = AnalysisAgent()
        sentiment, score = agent.analyze_sentiment(
            "Gubernur mengapresiasi dukungan penuh DPR dan memuji komitmen bersama"
        )
        assert sentiment == "Positif"
        assert score > 0.15

    def test_sentiment_negative_text(self) -> None:
        """Negative keywords should yield Negatif sentiment and negative score."""
        agent = AnalysisAgent()
        sentiment, score = agent.analyze_sentiment(
            "Masyarakat kecewa dan menolak kasus korupsi serta suap di lembaga negara"
        )
        assert sentiment == "Negatif"
        assert score < -0.15

    def test_sentiment_neutral_text(self) -> None:
        """Text without strong sentiment words should yield Netral."""
        agent = AnalysisAgent()
        sentiment, score = agent.analyze_sentiment(
            "Rapat kerja dilaksanakan di Gedung Nusantara II Senayan Jakarta"
        )
        assert sentiment == "Netral"
        assert -0.15 <= score <= 0.15

    def test_keyword_fallback_akd_classification(self) -> None:
        """Fallback keyword matcher should identify Komisi III for legal keywords."""
        agent = AnalysisAgent()
        results = agent._keyword_classify_akd(
            "Komisi III DPR menggelar rapat dengan Kejaksaan Agung dan KPK terkait penegakan hukum"
        )
        assert len(results) > 0
        top_akd = results[0]["akd_name"]
        assert top_akd == "Komisi III"
        assert results[0]["rank"] == 1
        assert 0.0 <= results[0]["confidence_score"] <= 1.0

    @pytest.mark.asyncio
    @patch("src.agents.analysis.gemini_classify_akd")
    async def test_classify_akd_uses_gemini_when_available(
        self, mock_gemini: AsyncMock,
    ) -> None:
        """classify_akd should prefer Gemini zero-shot results when available."""
        mock_gemini.return_value = [
            {"akd_name": "Komisi I", "confidence_score": 0.95, "rank": 1},
            {"akd_name": "Baleg", "confidence_score": 0.70, "rank": 2},
        ]
        agent = AnalysisAgent()
        results = await agent.classify_akd("Prajurit TNI dan Kemenhan bahas pertahanan negara")

        assert len(results) == 2
        assert results[0]["akd_name"] == "Komisi I"
        assert results[0]["akd_type"] == "Komisi"
        assert results[1]["akd_name"] == "Baleg"
        assert results[1]["akd_type"] == "Badan"
