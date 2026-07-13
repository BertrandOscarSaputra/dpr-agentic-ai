"""Tests for the Trend Agent."""

import pytest

from src.agents.trend import TrendAgent


class TestTrendAgent:
    """Test suite for TrendAgent."""

    def test_agent_initializes_with_default_threshold(self) -> None:
        """Trend agent should initialize with default z_threshold of 2.0."""
        agent = TrendAgent()
        assert agent.z_threshold == 2.0

    def test_agent_initializes_with_custom_threshold(self) -> None:
        """Trend agent should accept a custom z_threshold."""
        agent = TrendAgent(z_threshold=3.0)
        assert agent.z_threshold == 3.0

    @pytest.mark.asyncio
    async def test_detect_returns_expected_structure(self) -> None:
        """detect() should return a dict with akd_name and anomalies keys."""
        agent = TrendAgent()
        result = await agent.detect("Komisi I")
        assert result["akd_name"] == "Komisi I"
        assert "anomalies" in result
        assert isinstance(result["anomalies"], list)
