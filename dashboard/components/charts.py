"""Reusable chart components for the Streamlit dashboard."""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def sentiment_pie_chart(data: dict[str, int], title: str = "Distribusi Sentimen") -> None:
    """Render a pie chart showing sentiment distribution."""
    fig = px.pie(
        names=list(data.keys()),
        values=list(data.values()),
        title=title,
        color_discrete_map={
            "Positif": "#2ecc71",
            "Negatif": "#e74c3c",
            "Netral": "#95a5a6",
        },
    )
    st.plotly_chart(fig, width="stretch")


def trend_line_chart(
    dates: list[str],
    counts: list[int],
    anomaly_flags: list[bool],
    title: str = "Tren Volume Konten",
) -> None:
    """Render a line chart with anomaly markers."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=counts, mode="lines+markers", name="Volume"))

    # Highlight anomalies
    anomaly_dates = [d for d, a in zip(dates, anomaly_flags) if a]
    anomaly_counts = [c for c, a in zip(counts, anomaly_flags) if a]
    fig.add_trace(
        go.Scatter(
            x=anomaly_dates,
            y=anomaly_counts,
            mode="markers",
            marker={"size": 12, "color": "red", "symbol": "x"},
            name="Anomali",
        )
    )

    fig.update_layout(title=title)
    st.plotly_chart(fig, width="stretch")
