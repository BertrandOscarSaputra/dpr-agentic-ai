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
        # Use text without explicit AKD mention so Tier 1 doesn't match
        results = await agent.classify_akd("Prajurit TNI dan Kemenhan bahas pertahanan negara")

        assert len(results) == 2
        assert results[0]["akd_name"] == "Komisi I"
        assert results[0]["akd_type"] == "Komisi"
        assert results[1]["akd_name"] == "Baleg"
        assert results[1]["akd_type"] == "Badan"


class TestTier1FastExplicitMatch:
    """Tests for Tier-1 fast explicit AKD regex matching."""

    def test_explicit_komisi_match(self) -> None:
        """Explicit 'Komisi III' in text should return high-confidence match."""
        agent = AnalysisAgent()
        results = agent._fast_explicit_akd_match(
            "Komisi III DPR RI menggelar rapat dengan Kejaksaan Agung"
        )
        assert len(results) >= 1
        assert results[0]["akd_name"] == "Komisi III"
        assert results[0]["confidence_score"] == 0.98

    def test_explicit_baleg_match(self) -> None:
        """Explicit 'Baleg' in text should return a match."""
        agent = AnalysisAgent()
        results = agent._fast_explicit_akd_match(
            "Baleg DPR RI membahas RUU Transparansi Publik di Senayan"
        )
        assert len(results) >= 1
        assert results[0]["akd_name"] == "Baleg"

    def test_explicit_pimpinan_match(self) -> None:
        """Explicit 'Ketua DPR' in text should return a match."""
        agent = AnalysisAgent()
        results = agent._fast_explicit_akd_match(
            "Ketua DPR menyampaikan pidato pembukaan sidang paripurna"
        )
        assert len(results) >= 1
        assert results[0]["akd_name"] == "Ketua DPR"

    def test_no_match_for_implicit_text(self) -> None:
        """Text without explicit AKD names should return empty list."""
        agent = AnalysisAgent()
        results = agent._fast_explicit_akd_match(
            "Harga beras naik drastis di pasar tradisional"
        )
        assert results == []

    def test_multiple_komisi_matches(self) -> None:
        """Text mentioning two Komisi should return both."""
        agent = AnalysisAgent()
        results = agent._fast_explicit_akd_match(
            "Komisi I dan Komisi III DPR RI berkoordinasi soal keamanan siber"
        )
        assert len(results) >= 2
        matched_names = {r["akd_name"] for r in results}
        assert "Komisi I" in matched_names
        assert "Komisi III" in matched_names

    def test_max_three_matches(self) -> None:
        """Should return at most 3 matches even if more are found."""
        agent = AnalysisAgent()
        results = agent._fast_explicit_akd_match(
            "Komisi I, Komisi II, Komisi III, Komisi IV, dan Komisi V berkoordinasi lintas sektor"
        )
        assert len(results) <= 3


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
        assert results[0]["confidence_score"] == 0.98
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
        # Keyword matcher should find Komisi III via "hukum", "kejaksaan", "korupsi"
        assert results[0]["akd_name"] == "Komisi III"
        assert results[0]["confidence_score"] < 0.98  # Not from Tier 1

