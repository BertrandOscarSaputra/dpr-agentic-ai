"""Insight Agent — Gemini-powered summarization of analysis results."""

import logging

logger = logging.getLogger(__name__)


class InsightAgent:
    """Generates narrative summaries from analysis results using Gemini."""

    async def summarize(self, akd_name: str, analysis_data: list[dict]) -> str:
        """Generate a summary insight for the given AKD's analysis data."""
        logger.info(
            "Generating insight summary",
            extra={"akd_name": akd_name, "data_count": len(analysis_data)},
        )
        # TODO: Call Gemini API to summarize sentiment trends and key topics
        return ""
