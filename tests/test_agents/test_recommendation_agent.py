# -*- coding: utf-8 -*-
"""Unit tests for RecommendationAgent, MemoryRepository, Schema, and Critique Loop (Sprint 6)."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.agents.recommendation import RecommendationAgent
from src.agents.supervisor import AgentState, SupervisorAgent
from src.main import app
from src.repositories.memory_repository import MemoryRepository
from src.schemas.recommendation_schema import RecommendationItem, UrgencyLevel


class TestRecommendationSchema:
    """Test suite for RecommendationItem Pydantic Schema."""

    def test_schema_valid_creation(self) -> None:
        """Verify valid data creates a RecommendationItem with expected defaults."""
        item = RecommendationItem(
            akd_name="Komisi XII",
            issue_title="Kelangkaan Gas 3 Kg",
            action_type="RDP",
            target_stakeholders=["Kementerian ESDM", "Pertamina"],
            action_summary="Jadwalkan RDP darurat untuk audit kuota subsidi.",
            policy_background="Kenaikan harga gas elpiji di 5 wilayah memicu antrean warga.",
            md3_legal_basis="UU MD3 Pasal 98",
        )
        assert item.akd_name == "Komisi XII"
        assert item.urgency == UrgencyLevel.MEDIUM
        assert item.status == "draft"
        assert item.critique_score == 0.0
        assert item.critique_iterations == 1
        assert len(item.target_stakeholders) == 2
        assert isinstance(item.created_at, datetime)

    def test_schema_urgency_enum(self) -> None:
        """Verify UrgencyLevel enum values."""
        assert UrgencyLevel.HIGH == "HIGH"
        assert UrgencyLevel.MEDIUM == "MEDIUM"
        assert UrgencyLevel.LOW == "LOW"


class TestRecommendationAgent:
    """Test suite for RecommendationAgent logic and fallback."""

    @pytest.mark.asyncio
    async def test_fallback_generation(self) -> None:
        """Verify agent returns structured rule-based fallback when Gemini is unavailable."""
        agent = RecommendationAgent()
        agent.client = None  # Force offline fallback

        rec = await agent.generate_recommendation(
            akd_name="Komisi XI",
            issue_summary="Fluktuasi nilai tukar rupiah dan inflasi pangan.",
        )

        assert rec["akd_name"] == "Komisi XI"
        assert rec["status"] == "draft"
        assert "action_summary" in rec
        assert "target_stakeholders" in rec
        assert "md3_legal_basis" in rec
        assert "policy_background" in rec
        assert rec["urgency"] == "MEDIUM"

    @pytest.mark.asyncio
    async def test_fallback_high_urgency_keyword(self) -> None:
        """Verify agent sets HIGH urgency when crisis keywords are present."""
        agent = RecommendationAgent()
        agent.client = None

        rec = await agent.generate_recommendation(
            akd_name="Komisi III",
            issue_summary="Krisis korupsi pengadaan barang dan demo warga di berbagai daerah.",
        )
        assert rec["urgency"] == "HIGH"

    @pytest.mark.asyncio
    async def test_backward_compatible_generate(self) -> None:
        """Verify generate() alias returns both new and legacy fields."""
        agent = RecommendationAgent()
        agent.client = None

        rec = await agent.generate("Komisi I", "Isu keamanan siber nasional.")
        assert rec["akd_name"] == "Komisi I"
        assert "summary" in rec
        assert "recommendation" in rec
        assert "action_summary" in rec

    @pytest.mark.asyncio
    async def test_gemini_client_success(self) -> None:
        """Verify agent parses Gemini JSON response correctly."""
        agent = RecommendationAgent()
        mock_client = MagicMock()
        mock_payload = {
            "akd_name": "Komisi XII",
            "issue_title": "Kelangkaan Gas Elpiji 3 Kg",
            "action_type": "Rapat Dengar Pendapat (RDP)",
            "urgency": "HIGH",
            "target_stakeholders": ["Kementerian ESDM", "PT Pertamina"],
            "action_summary": "Jadwalkan RDP darurat dengan Pertamina.",
            "policy_background": "Sentimen negatif publik melonjak tajam.",
            "md3_legal_basis": "UU MD3 Pasal 98",
        }
        mock_client.generate_async = AsyncMock(
            return_value=f"```json\n{json.dumps(mock_payload)}\n```"
        )
        agent.client = mock_client

        rec = await agent.generate_recommendation("Komisi XII", "Kelangkaan Gas 3 Kg")
        assert rec["akd_name"] == "Komisi XII"
        assert rec["action_type"] == "Rapat Dengar Pendapat (RDP)"
        assert rec["status"] == "draft"
        assert rec["urgency"] == "HIGH"


class TestMemoryRepository:
    """Test suite for MemoryRepository SQLite operations."""

    def test_context_memory_and_30_day_history(self, tmp_path) -> None:
        """Verify 30-day window query filters properly."""
        db_file = tmp_path / "test_memory.db"
        repo = MemoryRepository(db_path=db_file)

        # Insert historical data
        repo.save_context_memory("Komisi XII", "2026-08-01", -0.4, 5, "Isu BBM")
        repo.save_context_memory("Komisi XII", "2026-08-15", -0.7, 12, "Isu Gas 3 Kg")
        repo.save_context_memory("Komisi XII", "2026-08-25", -0.8, 20, "Kelangkaan Gas")
        # Older than 30 days relative to 2026-08-25
        repo.save_context_memory("Komisi XII", "2026-07-01", -0.1, 2, "Isu lama")
        # Different AKD
        repo.save_context_memory("Komisi I", "2026-08-20", 0.2, 4, "Isu Siber")

        history = repo.get_30_day_history("Komisi XII", "2026-08-25")
        assert len(history) == 3
        dates = [h["date_key"] for h in history]
        assert "2026-08-01" in dates
        assert "2026-08-15" in dates
        assert "2026-08-25" in dates
        assert "2026-07-01" not in dates

    def test_save_and_list_recommendations(self, tmp_path) -> None:
        """Verify recommendation saving and retrieval with filter."""
        db_file = tmp_path / "test_memory.db"
        repo = MemoryRepository(db_path=db_file)

        rec1 = {
            "akd_name": "Komisi XII",
            "issue_title": "Subsidi Gas",
            "action_type": "RDP",
            "urgency": "HIGH",
            "target_stakeholders": ["ESDM", "Pertamina"],
            "action_summary": "Panggil Dirut Pertamina untuk audit distribusi.",
            "policy_background": "Harga melonjak.",
            "md3_legal_basis": "UU MD3 Pasal 98",
            "status": "draft",
            "critique_score": 0.9,
            "critique_iterations": 1,
        }
        rec2 = {
            "akd_name": "Komisi XI",
            "issue_title": "Suku Bunga BI",
            "action_type": "RDP",
            "urgency": "MEDIUM",
            "target_stakeholders": ["Bank Indonesia"],
            "action_summary": "Rapat kerja evaluasi moneter.",
            "policy_background": "Inflasi stabil.",
            "md3_legal_basis": "UU MD3 Pasal 98",
            "status": "draft",
            "critique_score": 0.85,
            "critique_iterations": 1,
        }

        id1 = repo.save_recommendation(rec1)
        id2 = repo.save_recommendation(rec2)
        assert id1 > 0
        assert id2 > 0

        all_recs = repo.list_recommendations()
        assert len(all_recs) == 2

        komisi12_recs = repo.list_recommendations(akd_name="Komisi XII")
        assert len(komisi12_recs) == 1
        assert komisi12_recs[0]["akd_name"] == "Komisi XII"
        assert isinstance(komisi12_recs[0]["target_stakeholders"], list)
        assert "Pertamina" in komisi12_recs[0]["target_stakeholders"]


class TestSupervisorCritiqueLoop:
    """Test suite for supervisor self-correction critique loop."""

    @pytest.mark.asyncio
    async def test_critique_scoring_calculation(self) -> None:
        """Verify 4 criteria scoring logic in _critique_validator_node."""
        supervisor = SupervisorAgent()

        # 1. Perfect recommendation (should score 1.0)
        perfect_state: AgentState = {
            "recommendations": [
                {
                    "action_summary": "Jadwalkan RDP darurat dengan Dirut Pertamina untuk audit distribusi.",
                    "target_stakeholders": ["Kementerian ESDM", "Pertamina"],
                    "md3_legal_basis": "UU MD3 Pasal 98 wewenang pengawasan",
                    "policy_background": "Sentimen publik negatif akibat kelangkaan gas di 5 wilayah perkotaan.",
                }
            ],
            "critique_iterations": 0,
        }
        res = await supervisor._critique_validator_node(perfect_state)
        assert res["critique_score"] == 1.0
        assert res["critique_iterations"] == 1
        assert "lolos audit" in res["critique_feedback"]

        # 2. Deficient recommendation (no verbs, no stakeholders, no MD3, short bg)
        deficient_state: AgentState = {
            "recommendations": [
                {
                    "action_summary": "isu harga",
                    "target_stakeholders": [],
                    "md3_legal_basis": "",
                    "policy_background": "singkat",
                }
            ],
            "critique_iterations": 0,
        }
        res_def = await supervisor._critique_validator_node(deficient_state)
        assert res_def["critique_score"] == 0.0
        assert "Perbaikan diperlukan" in res_def["critique_feedback"]

    def test_route_after_critique(self) -> None:
        """Verify conditional routing logic after critique."""
        supervisor = SupervisorAgent(critique_threshold=0.75, max_critique_iterations=3)

        # Low score, iteration 1 -> retry
        route1 = supervisor._route_after_critique({
            "critique_score": 0.60,
            "critique_iterations": 1,
        })
        assert route1 == "recommend"

        # High score -> pass
        route2 = supervisor._route_after_critique({
            "critique_score": 0.85,
            "critique_iterations": 1,
        })
        assert route2 == "end" or route2 == "__end__"

        # Low score but reached max iterations (3) -> end anyway
        route3 = supervisor._route_after_critique({
            "critique_score": 0.60,
            "critique_iterations": 3,
        })
        assert route3 == "end" or route3 == "__end__"


class TestRecommendationRoutes:
    """Test suite for FastAPI recommendation endpoints."""

    def test_get_recommendations_endpoint(self, tmp_path) -> None:
        """Verify GET /api/v1/recommendations returns 200 with success status."""
        test_client = TestClient(app)
        resp = test_client.get("/api/v1/recommendations")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "total" in data
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_patch_recommendation_status(self) -> None:
        """Verify PATCH /api/v1/recommendations/{id}/status updates status."""
        test_client = TestClient(app)
        resp = test_client.patch(
            "/api/v1/recommendations/1/status",
            json={"status": "reviewed", "reviewed_by": "Tenaga Ahli 1"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["new_status"] == "reviewed"
