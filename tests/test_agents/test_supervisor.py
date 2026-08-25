# -*- coding: utf-8 -*-
"""Unit tests for LangGraph SupervisorAgent (src/agents/supervisor.py)."""

import pytest
from unittest.mock import AsyncMock, patch

from src.agents.supervisor import SupervisorAgent


class TestSupervisorAgent:
    """Test suite for SupervisorAgent LangGraph StateGraph orchestration."""

    def test_supervisor_initialization(self) -> None:
        """Verify Supervisor initializes with graph and sub-agents."""
        supervisor = SupervisorAgent()
        assert supervisor.graph is not None
        assert supervisor.collection_agent is not None
        assert supervisor.analysis_agent is not None
        assert supervisor.trend_agent is not None
        assert supervisor.insight_agent is not None
        assert supervisor.recommendation_agent is not None

    @pytest.mark.asyncio
    async def test_full_workflow_with_injected_articles(self) -> None:
        """Verify end-to-end execution of the stategraph when articles are passed."""
        supervisor = SupervisorAgent(z_threshold=5.0)  # High threshold to test standard flow

        mock_articles = [
            {
                "title": "Komisi I Bahas Anggaran Alutsista TNI",
                "content": "Komisi I DPR RI menggelar rapat kerja dengan Kementerian Pertahanan membahas kesiapan alutsista.",
                "url": "https://example.com/komisi-1-alutsista",
                "published_at": "2026-08-24T10:00:00+07:00",
                "source_type": "news_online",
                "source_name": "Antara",
            },
            {
                "title": "Komisi III Evaluasi Reformasi Hukum Nasional",
                "content": "Komisi III DPR bersama Kejaksaan Agung dan Kepolisian RI membahas RUU Hukum Acara Perdata.",
                "url": "https://example.com/komisi-3-hukum",
                "published_at": "2026-08-24T11:00:00+07:00",
                "source_type": "news_online",
                "source_name": "Detik",
            },
        ]

        result = await supervisor.run({"type": "full_analysis", "articles": mock_articles})

        assert result["status"] == "completed"
        assert len(result["analyzed_items"]) == 2
        assert "akd_counts" in result["trends"]
        assert len(result["insights"]) > 0
        assert len(result["recommendations"]) > 0
        assert result["critique_score"] >= 0.75

    @pytest.mark.asyncio
    async def test_anomaly_conditional_routing(self) -> None:
        """Verify that detected volume spikes trigger the anomaly critique node."""
        # Set low z-threshold to trigger anomaly
        supervisor = SupervisorAgent(z_threshold=1.0)

        # Create skewed distribution (Komisi I has 10 articles, other has 1)
        mock_articles = [
            {
                "title": f"Komisi I Isu Pertahanan Siber #{i}",
                "content": "Komisi I DPR membahas kebocoran data strategis nasional.",
                "url": f"https://example.com/komisi-1-{i}",
                "published_at": "2026-08-24T10:00:00+07:00",
                "source_type": "news_online",
                "source_name": "Tempo",
            }
            for i in range(10)
        ] + [
            {
                "title": "Komisi X Pendidikan Nasional",
                "content": "Komisi X meninjau kurikulum sekolah.",
                "url": "https://example.com/komisi-10-1",
                "published_at": "2026-08-24T10:00:00+07:00",
                "source_type": "news_online",
                "source_name": "Kompas",
            }
        ]

        result = await supervisor.run({"type": "full_analysis", "articles": mock_articles})

        assert result["status"] == "completed"
        assert len(result["anomalies"]) > 0
        assert "anomaly_review_result" in result
        assert result["anomaly_review_result"]["audited_count"] > 0
        assert any(
            v["akd_name"] == "Komisi I"
            for v in result["anomaly_review_result"]["verified_details"]
        )

    @pytest.mark.asyncio
    async def test_critique_self_correction_loop(self) -> None:
        """Verify that recommendation critique loop refines the output."""
        supervisor = SupervisorAgent()

        # Mock recommendation generator returning basic unrefined text
        with patch.object(
            supervisor.recommendation_agent,
            "generate",
            new_callable=AsyncMock,
        ) as mock_gen:
            mock_gen.return_value = {
                "akd_name": "Komisi I",
                "summary": "Isu pertahanan siber",
                "recommendation": "",  # Empty recommendation to trigger critique refinement
                "status": "draft",
            }

            mock_articles = [
                {
                    "title": "Komisi I Bahas Pertahanan",
                    "content": "Komisi I DPR menggelar rapat pertahanan.",
                    "url": "https://example.com/komisi-1-test",
                    "published_at": "2026-08-24T10:00:00+07:00",
                    "source_type": "news_online",
                    "source_name": "Antara",
                }
            ]

            result = await supervisor.run({"type": "full_analysis", "articles": mock_articles})

            assert result["status"] == "completed"
            assert result["critique_iterations"] >= 1
            assert len(result["recommendations"]) > 0
            # Ensure refinement content is present
            assert any(
                "RDP" in rec["recommendation"] or "Pokja" in rec["recommendation"]
                for rec in result["recommendations"]
            )

    @pytest.mark.asyncio
    async def test_error_fault_tolerance(self) -> None:
        """Verify graph handles node exceptions gracefully without crashing."""
        supervisor = SupervisorAgent()

        with patch.object(
            supervisor.analysis_agent,
            "classify_akd",
            side_effect=RuntimeError("Simulated NLP failure"),
        ):
            mock_articles = [
                {
                    "title": "Uji Coba Error Handling",
                    "content": "Konten berita simulasi error.",
                    "url": "https://example.com/error-test",
                    "published_at": "2026-08-24T10:00:00+07:00",
                    "source_type": "news_online",
                    "source_name": "Detik",
                }
            ]

            result = await supervisor.run({"type": "full_analysis", "articles": mock_articles})

            # Graph completes with warnings instead of throwing an unhandled crash
            assert result["status"] in ["completed", "completed_with_warnings"]
            assert len(result["errors"]) > 0
            assert any("analyze_item_error" in err for err in result["errors"])
