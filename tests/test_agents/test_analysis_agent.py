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
        """analyze() should return a dict with sentiment, score, akd_mappings, and is_dpr_relevant."""
        agent = AnalysisAgent()
        result = await agent.analyze("Komisi III DPR RI menyetujui RUU Hukum Pidana demi keadilan")
        assert "sentiment" in result
        assert "sentiment_score" in result
        assert "akd_mappings" in result
        assert "is_dpr_relevant" in result
        assert "relevance_score" in result
        assert result["sentiment"] in {"Positif", "Negatif", "Netral"}
        assert -1.0 <= result["sentiment_score"] <= 1.0
        assert result["is_dpr_relevant"] is True
        assert result["relevance_score"] >= 0.60

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
            "Kejaksaan Agung dan Kepolisian menggelar penegakan hukum dan peradilan"
        )
        assert len(results) >= 1
        assert results[0]["akd_name"] == "Komisi III"
        assert results[0]["akd_type"] == "Komisi"
        assert results[0]["confidence_score"] > 0.60

    def test_keyword_classification_sorts_by_confidence(self) -> None:
        """Multiple AKD matches should be sorted by confidence descending."""
        agent = AnalysisAgent()
        results = agent._keyword_classify_akd(
            "Pertahanan siber dan diplomasi luar negeri serta pendidikan nasional"
        )
        assert len(results) >= 2
        for i in range(len(results) - 1):
            assert results[i]["confidence_score"] >= results[i + 1]["confidence_score"]
            assert results[i]["rank"] == i + 1

    def test_keyword_classification_no_match(self) -> None:
        """Text with zero political/policy keywords should return empty list."""
        agent = AnalysisAgent()
        results = agent._keyword_classify_akd("Resep kue bolu coklat kukus empuk dan manis")
        assert results == []

    def test_policy_relevance_evaluation(self) -> None:
        """evaluate_policy_relevance should separate governance news from irrelevant noise."""
        agent = AnalysisAgent()

        # 1. Relevant with AKD mapping
        rel, score = agent.evaluate_policy_relevance(
            "Rapat APBN di Senayan", [{"akd_name": "Badan Anggaran", "confidence_score": 0.90}]
        )
        assert rel is True
        assert score >= 0.80

        # 2. Relevant via governance keywords without explicit AKD
        rel_gov, score_gov = agent.evaluate_policy_relevance(
            "Pemerintah dan kementerian umumkan regulasi pajak baru terkait subsidi", []
        )
        assert rel_gov is True
        assert score_gov >= 0.60

        # 3. Irrelevant text
        rel_noise, score_noise = agent.evaluate_policy_relevance(
            "Kucing lucu bermain di taman kota sore hari", []
        )
        assert rel_noise is False
        assert score_noise < 0.30


class TestTierRouting:
    """Tests for 3-tier AKD classification routing."""

    @pytest.mark.asyncio
    @patch("src.agents.analysis.gemini_classify_akd")
    async def test_tier1_bypasses_gemini(self, mock_gemini: AsyncMock) -> None:
        """When Tier 1 matches, Gemini API should NOT be called."""
        agent = AnalysisAgent()
        results = await agent.classify_akd(
            "Komisi IX DPR RI membahas program BPJS Kesehatan"
        )
        # Tier 1 should match "Komisi IX" directly
        assert len(results) >= 1
        assert results[0]["akd_name"] == "Komisi IX"
        assert results[0]["confidence_score"] >= 0.90
        # Gemini should NOT have been called
        mock_gemini.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.agents.analysis.gemini_classify_akd")
    async def test_tier2_called_when_tier1_fails(self, mock_gemini: AsyncMock) -> None:
        """When Tier 1 has no match, Gemini API should be called."""
        mock_gemini.return_value = [
            {"akd_name": "Komisi IV", "confidence_score": 0.88, "rank": 1},
        ]
        agent = AnalysisAgent()
        results = await agent.classify_akd(
            "Harga pupuk subsidi melonjak di daerah pertanian"
        )
        assert len(results) >= 1
        assert results[0]["akd_name"] == "Komisi IV"
        mock_gemini.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.agents.analysis.gemini_classify_akd")
    async def test_tier3_keyword_fallback(self, mock_gemini: AsyncMock) -> None:
        """When Gemini returns empty, keyword fallback (Tier 3) should be used."""
        mock_gemini.return_value = []
        agent = AnalysisAgent()
        results = await agent.classify_akd(
            "Penegakan hukum dan kejaksaan menindak korupsi besar"
        )
        assert len(results) >= 1
        assert results[0]["akd_name"] == "Komisi III"
        assert results[0]["confidence_score"] <= 0.95
