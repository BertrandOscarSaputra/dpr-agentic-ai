# -*- coding: utf-8 -*-
"""Unit tests for TrendAgent — Sentiment-Weighted Z-Score and Anomaly Persistence."""

import pytest
from src.agents.trend import TrendAgent


class TestTrendAgent:
    """Test suite for TrendAgent."""

    def test_agent_initializes_with_default_threshold(self) -> None:
        """Trend agent should initialize with default z_threshold of 2.0."""
        agent = TrendAgent()
        assert agent.z_threshold == 2.0
        assert agent.damping_k == 1.5
        assert agent.neg_weight == 2.5

    def test_agent_initializes_with_custom_threshold(self) -> None:
        """Trend agent should accept a custom z_threshold and damping parameters."""
        agent = TrendAgent(z_threshold=3.0, damping_k=2.0, neg_weight=3.0)
        assert agent.z_threshold == 3.0
        assert agent.damping_k == 2.0
        assert agent.neg_weight == 3.0

    def test_calculate_sentiment_weighted_volume(self) -> None:
        """Verify negative articles receive 2.5x weight multiplier."""
        agent = TrendAgent(neg_weight=2.5)
        # 2 pos, 3 net, 4 neg -> 3 + 2.0 + (4 * 2.5 = 10.0) = 15.0
        vol = agent.calculate_sentiment_weighted_volume(pos_count=2, net_count=3, neg_count=4)
        assert vol == 15.0

    def test_compute_weighted_zscore_with_damping(self) -> None:
        """Verify damping factor prevents excessive Z-score on small baseline."""
        agent = TrendAgent(damping_k=1.5, z_threshold=2.0)
        # Baseline history of small values [1, 1, 2]
        res = agent.compute_weighted_zscore(current_effective=8.0, historical_counts=[1.0, 1.0, 2.0])
        assert "z_score" in res
        assert "mean" in res
        assert "std" in res
        # Without damping: (8 - 3) / 3.32 = 1.50
        # With damping 1.5: (8 - 3) / (3.32 + 1.5) = 1.04
        assert res["z_score"] < 2.0  # Damping prevents false positive

    def test_detect_anomalies_flags_negative_spike(self) -> None:
        """Verify that a surge of negative sentiment items triggers an anomaly."""
        agent = TrendAgent(z_threshold=2.0)
        items = [
            # 10 negative items on Komisi I
            {
                "title": f"Dugaan Korupsi Proyek Siber {i}",
                "content": "Temuan kebocoran data nasional",
                "sentiment": "Negatif",
                "akd_mappings": [{"akd_name": "Komisi I", "confidence_score": 0.95}],
            }
            for i in range(10)
        ] + [
            # 1 normal item on Komisi II
            {
                "title": "Rapat Prosedural Pilkada",
                "content": "Jadwal sidang",
                "sentiment": "Netral",
                "akd_mappings": [{"akd_name": "Komisi II", "confidence_score": 0.95}],
            }
        ]

        result = agent.detect_anomalies(items, baseline_pad_to_24=True)
        assert result["total_items"] == 11
        assert "anomalies" in result
        assert len(result["anomalies"]) >= 1
        anom = result["anomalies"][0]
        assert anom["akd_name"] == "Komisi I"
        assert anom["negative_ratio"] == 1.0
        assert anom["z_score"] >= 2.0
        assert anom["severity"] == "CRITICAL"
        assert anom["is_sentiment_driven"] is True

    @pytest.mark.asyncio
    async def test_detect_for_single_akd(self) -> None:
        """detect() should return expected structure for a single AKD query."""
        agent = TrendAgent()
        items = [
            {
                "title": "Rapat Komisi I",
                "content": "Evaluasi siber",
                "sentiment": "Netral",
                "akd_mappings": [{"akd_name": "Komisi I", "confidence_score": 0.9}],
            }
        ]
        result = await agent.detect("Komisi I", recent_items=items)
        assert result["akd_name"] == "Komisi I"
        assert "anomalies" in result
        assert isinstance(result["anomalies"], list)
        assert "stats" in result
