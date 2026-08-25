# -*- coding: utf-8 -*-
"""DPR Agentic AI — Streamlit Executive Dashboard.

Reads real analyzed data from data/analysis/analysis_output.json
and data/news/news_output.json to display live metrics,
sentiment distributions, AKD breakdowns, and exact daily time-series counts.
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ANALYSIS_PATH = PROJECT_ROOT / "data" / "analysis" / "analysis_output.json"
NEWS_PATH = PROJECT_ROOT / "data" / "news" / "news_output.json"
AKD_MASTER_PATH = PROJECT_ROOT / "kamus" / "akd_master.json"

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DPR Agentic AI — Executive Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Data Loaders ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_analysis() -> list[dict]:
    """Load analysis output JSON from all daily partitions or combined file."""
    analysis_dir = PROJECT_ROOT / "data" / "analysis"
    daily_files = sorted(analysis_dir.glob("analysis_2026-*.json"))
    if daily_files:
        items = []
        seen = set()
        for f in daily_files:
            try:
                with open(f, encoding="utf-8") as fp:
                    for item in json.load(fp):
                        key = (item.get("url", ""), str(item.get("published_at", ""))[:10])
                        if key not in seen:
                            seen.add(key)
                            items.append(item)
            except Exception:
                continue
        if items:
            return items

    if ANALYSIS_PATH.exists():
        with open(ANALYSIS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


@st.cache_data(ttl=60)
def load_news() -> list[dict]:
    """Load news output JSON from all daily partitions or combined file."""
    news_dir = PROJECT_ROOT / "data" / "news"
    daily_files = sorted(news_dir.glob("news_2026-*.json"))
    if daily_files:
        items = []
        seen = set()
        for f in daily_files:
            try:
                with open(f, encoding="utf-8") as fp:
                    for item in json.load(fp):
                        key = (item.get("url", ""), str(item.get("published_at", ""))[:10])
                        if key not in seen:
                            seen.add(key)
                            items.append(item)
            except Exception:
                continue
        if items:
            return items

    if NEWS_PATH.exists():
        with open(NEWS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


@st.cache_data(ttl=3600)
def load_akd_master() -> list[str]:
    """Load 24 AKD master names."""
    if not AKD_MASTER_PATH.exists():
        return []
    with open(AKD_MASTER_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return [entry["name"] for entry in data.get("akd", [])]


def build_analysis_df(items: list[dict]) -> pd.DataFrame:
    """Flatten analysis items into a DataFrame with primary AKD."""
    rows = []
    for item in items:
        primary_akd = "Tidak Terklasifikasi"
        primary_confidence = 0.0
        mappings = item.get("akd_mappings", [])
        if mappings:
            rank1 = min(mappings, key=lambda m: m.get("rank", 99))
            primary_akd = rank1.get("akd_name", primary_akd)
            primary_confidence = rank1.get("confidence_score", 0.0)

        pub_str = item.get("published_at", "")
        rows.append({
            "title": item.get("title", ""),
            "source_name": item.get("source_name", ""),
            "source_type": item.get("source_type", ""),
            "sentiment": item.get("sentiment", "Netral"),
            "sentiment_score": item.get("sentiment_score", 0.0),
            "primary_akd": primary_akd,
            "confidence": primary_confidence,
            "published_at": pub_str,
            "url": item.get("url", ""),
        })
    df = pd.DataFrame(rows)
    if not df.empty and "published_at" in df.columns:
        # Extract clean YYYY-MM-DD string
        df["date_str"] = df["published_at"].astype(str).str[:10]
        df["date"] = pd.to_datetime(df["date_str"], errors="coerce").dt.date
    return df


# ── Load Data ────────────────────────────────────────────────────────────────
analysis_items = load_analysis()
news_items = load_news()
akd_list = load_akd_master()
df = build_analysis_df(analysis_items)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main .block-container { padding-top: 1.5rem; }
    [data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; }
    [data-testid="stMetricLabel"] { font-size: 0.85rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("## 🏛️ DPR Agentic AI — Executive Dashboard")
st.caption("Sistem Monitoring Isu AKD & Analisis Sentimen Publik — Periode 1 s.d. 17 Agustus 2026")
st.markdown("---")

# ── Sidebar Filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filter Data")

    # Date filter
    available_dates = ["Semua Tanggal"]
    if not df.empty and "date_str" in df.columns:
        available_dates += sorted(df["date_str"].dropna().unique().tolist())
    selected_date = st.selectbox("Pilih Tanggal Spesifik", available_dates)

    # Sentiment filter
    sentiment_options = ["Semua", "Positif", "Negatif", "Netral"]
    selected_sentiment = st.selectbox("Sentimen", sentiment_options)

    # AKD filter
    akd_options = ["Semua AKD"] + sorted(df["primary_akd"].unique().tolist()) if not df.empty else ["Semua AKD"]
    selected_akd = st.selectbox("Alat Kelengkapan Dewan (AKD)", akd_options)

    # Source type filter
    source_options = ["Semua Sumber", "news_online", "twitter"]
    selected_source = st.selectbox("Jenis Sumber", source_options)

    st.markdown("---")
    st.markdown(f"**Total Data Teranalisis**: `{len(analysis_items):,}` artikel")
    st.markdown(f"**Total Berita Terkumpul**: `{len(news_items):,}` artikel")

# Apply filters
filtered_df = df.copy()
if selected_date != "Semua Tanggal" and not filtered_df.empty:
    filtered_df = filtered_df[filtered_df["date_str"] == selected_date]
if selected_sentiment != "Semua" and not filtered_df.empty:
    filtered_df = filtered_df[filtered_df["sentiment"] == selected_sentiment]
if selected_akd != "Semua AKD" and not filtered_df.empty:
    filtered_df = filtered_df[filtered_df["primary_akd"] == selected_akd]
if selected_source != "Semua Sumber" and not filtered_df.empty:
    filtered_df = filtered_df[filtered_df["source_type"] == selected_source]

# ── KPI Metrics Row ─────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📰 Total Berita", f"{len(filtered_df):,}")
with col2:
    st.metric("🔬 Teranalisis", f"{len(filtered_df):,}")
with col3:
    pos_count = len(filtered_df[filtered_df["sentiment"] == "Positif"]) if not filtered_df.empty else 0
    st.metric("😊 Positif", f"{pos_count:,}")
with col4:
    neg_count = len(filtered_df[filtered_df["sentiment"] == "Negatif"]) if not filtered_df.empty else 0
    st.metric("😠 Negatif", f"{neg_count:,}")
with col5:
    net_count = len(filtered_df[filtered_df["sentiment"] == "Netral"]) if not filtered_df.empty else 0
    st.metric("😐 Netral", f"{net_count:,}")

st.markdown("---")

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_overview, tab_akd, tab_sentiment, tab_data = st.tabs([
    "📊 Ringkasan Umum",
    "🏛️ Breakdown per AKD",
    "📈 Analisis Sentimen",
    "📋 Data Mentah",
])

# ── TAB 1: Overview ─────────────────────────────────────────────────────────
with tab_overview:
    if filtered_df.empty:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")
    else:
        # Top 2 columns: Sentiment pie + Top 10 AKD
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("#### Distribusi Sentimen (Jumlah & Persentase)")
            sentiment_counts = filtered_df["sentiment"].value_counts().reset_index()
            sentiment_counts.columns = ["Sentimen", "Jumlah"]
            color_map = {"Positif": "#22c55e", "Negatif": "#ef4444", "Netral": "#94a3b8"}
            fig_pie = px.pie(
                sentiment_counts,
                values="Jumlah",
                names="Sentimen",
                color="Sentimen",
                color_discrete_map=color_map,
                hole=0.45,
            )
            # Display exact article count + percentage directly on slices
            fig_pie.update_traces(
                textinfo="label+value+percent",
                texttemplate="%{label}<br><b>%{value} artikel</b> (%{percent})",
                hovertemplate="<b>%{label}</b><br>Jumlah: %{value} artikel<br>Proporsi: %{percent}<extra></extra>",
            )
            fig_pie.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.15),
                height=380,
            )
            st.plotly_chart(fig_pie, width="stretch")

        with c2:
            st.markdown("#### Top 10 AKD Paling Disorot Media")
            akd_counts = filtered_df["primary_akd"].value_counts().head(10).reset_index()
            akd_counts.columns = ["AKD", "Jumlah"]
            fig_bar = px.bar(
                akd_counts,
                x="Jumlah",
                y="AKD",
                orientation="h",
                text="Jumlah",
                color="Jumlah",
                color_continuous_scale="Teal",
            )
            fig_bar.update_traces(
                texttemplate="<b>%{text}</b> artikel",
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Jumlah Berita: %{x} artikel<extra></extra>",
            )
            fig_bar.update_layout(
                margin=dict(t=20, b=20, l=20, r=40),
                showlegend=False,
                yaxis=dict(autorange="reversed"),
                height=380,
            )
            st.plotly_chart(fig_bar, width="stretch")

        # ── EXACT DAILY VOLUME BAR & SENTIMENT BREAKDOWN CHART ─────────────────
        st.markdown("---")
        st.markdown("#### 📅 Volume Berita per Tanggal Pasti (Exact Daily Article Count)")

        if "date_str" in filtered_df.columns:
            # Build daily summary with sentiment breakdown
            daily_sentiment = (
                filtered_df.groupby(["date_str", "sentiment"])
                .size()
                .reset_index(name="Jumlah")
                .sort_values("date_str")
            )
            daily_total = (
                filtered_df.groupby("date_str")
                .size()
                .reset_index(name="Total")
                .sort_values("date_str")
            )

            fig_daily = px.bar(
                daily_sentiment,
                x="date_str",
                y="Jumlah",
                color="sentiment",
                color_discrete_map={"Positif": "#22c55e", "Negatif": "#ef4444", "Netral": "#94a3b8"},
                barmode="stack",
                labels={"date_str": "Tanggal Publikasi", "Jumlah": "Jumlah Artikel", "sentiment": "Sentimen"},
            )

            # Add total count label above each bar
            for _, row in daily_total.iterrows():
                fig_daily.add_annotation(
                    x=row["date_str"],
                    y=row["Total"],
                    text=f"<b>{row['Total']}</b>",
                    showarrow=False,
                    yshift=12,
                    font=dict(size=12, color="#1e293b"),
                )

            fig_daily.update_traces(
                hovertemplate="<b>Tanggal:</b> %{x}<br><b>Sentimen:</b> %{fullData.name}<br><b>Jumlah:</b> %{y} artikel<extra></extra>"
            )
            fig_daily.update_layout(
                margin=dict(t=30, b=40, l=20, r=20),
                height=380,
                xaxis=dict(type="category", tickangle=-30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_daily, width="stretch")

            # Quick summary table for exact daily counts
            with st.expander("📋 Lihat Tabel Rincian Jumlah Artikel per Tanggal"):
                pivot_daily = pd.crosstab(filtered_df["date_str"], filtered_df["sentiment"], margins=True, margins_name="Total")
                st.dataframe(pivot_daily, width="stretch")

# ── TAB 2: Per-AKD Breakdown ────────────────────────────────────────────────
with tab_akd:
    if filtered_df.empty:
        st.warning("Tidak ada data yang sesuai.")
    else:
        st.markdown("#### Distribusi Sentimen per AKD (Heatmap & Matriks Angka)")

        # Build pivot: AKD vs Sentiment counts
        pivot = pd.crosstab(filtered_df["primary_akd"], filtered_df["sentiment"])
        for col in ["Positif", "Negatif", "Netral"]:
            if col not in pivot.columns:
                pivot[col] = 0
        pivot = pivot[["Positif", "Netral", "Negatif"]]
        pivot["Total"] = pivot.sum(axis=1)
        pivot = pivot.sort_values("Total", ascending=False).head(20)
        display_pivot = pivot[["Positif", "Netral", "Negatif"]]

        fig_heatmap = go.Figure(data=go.Heatmap(
            z=display_pivot.values,
            x=display_pivot.columns.tolist(),
            y=display_pivot.index.tolist(),
            colorscale="RdYlGn",
            reversescale=True,
            text=display_pivot.values,
            texttemplate="<b>%{text}</b> artikel",
            hovertemplate="<b>AKD:</b> %{y}<br><b>Sentimen:</b> %{x}<br><b>Jumlah:</b> %{z} artikel<extra></extra>",
        ))
        fig_heatmap.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            height=520,
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig_heatmap, width="stretch")

        # Per-AKD detail selector
        st.markdown("---")
        detail_akd = st.selectbox("Pilih AKD untuk Rincian Detail:", sorted(filtered_df["primary_akd"].unique().tolist()))
        akd_df = filtered_df[filtered_df["primary_akd"] == detail_akd]

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total Artikel AKD Ini", f"{len(akd_df)} artikel")
        with col_b:
            avg_score = akd_df["sentiment_score"].mean() if not akd_df.empty else 0
            st.metric("Rata-rata Skor Sentimen", f"{avg_score:.2f}")
        with col_c:
            akd_pos = len(akd_df[akd_df["sentiment"] == "Positif"])
            akd_neg = len(akd_df[akd_df["sentiment"] == "Negatif"])
            st.metric("Sentimen Positif vs Negatif", f"{akd_pos} / {akd_neg}")

        if not akd_df.empty:
            st.dataframe(
                akd_df[["date_str", "title", "sentiment", "sentiment_score", "source_name", "url"]].sort_values(
                    "date_str", ascending=False
                ),
                width="stretch",
                height=300,
            )

# ── TAB 3: Sentiment Analysis ───────────────────────────────────────────────
with tab_sentiment:
    if filtered_df.empty:
        st.warning("Tidak ada data yang sesuai.")
    else:
        st.markdown("#### Distribusi Skor Sentimen (-1.0 s.d. +1.0)")
        fig_hist = px.histogram(
            filtered_df,
            x="sentiment_score",
            nbins=30,
            color="sentiment",
            color_discrete_map={"Positif": "#22c55e", "Negatif": "#ef4444", "Netral": "#94a3b8"},
            labels={"sentiment_score": "Skor Sentimen", "count": "Jumlah Artikel"},
        )
        fig_hist.update_traces(
            hovertemplate="<b>Skor:</b> %{x}<br><b>Jumlah:</b> %{y} artikel<extra></extra>",
            opacity=0.75
        )
        fig_hist.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            height=350,
            barmode="stack",
        )
        st.plotly_chart(fig_hist, width="stretch")

        # Sentiment by media source with exact numbers
        st.markdown("#### Jumlah Artikel Berdasarkan Portal Media")
        source_sentiment = (
            filtered_df.groupby(["source_name", "sentiment"])
            .size()
            .reset_index(name="Jumlah")
        )
        fig_source = px.bar(
            source_sentiment,
            x="source_name",
            y="Jumlah",
            color="sentiment",
            color_discrete_map={"Positif": "#22c55e", "Negatif": "#ef4444", "Netral": "#94a3b8"},
            text="Jumlah",
            labels={"source_name": "Portal Media", "Jumlah": "Jumlah Artikel"},
        )
        fig_source.update_traces(
            textposition="auto",
            hovertemplate="<b>Portal:</b> %{x}<br><b>Sentimen:</b> %{fullData.name}<br><b>Jumlah:</b> %{y} artikel<extra></extra>"
        )
        fig_source.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            height=400,
            xaxis_tickangle=-45,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_source, width="stretch")

        # Top negative articles
        st.markdown("#### 🚨 Berita dengan Sentimen Paling Negatif")
        neg_df = filtered_df[filtered_df["sentiment"] == "Negatif"].sort_values("sentiment_score").head(10)
        if not neg_df.empty:
            for _, row in neg_df.iterrows():
                st.markdown(
                    f"- `[{row['date_str']}]` **[{row['title']}]({row['url']})** "
                    f"(Skor: `{row['sentiment_score']:.2f}` | AKD: **{row['primary_akd']}** | "
                    f"Sumber: {row['source_name']})"
                )
        else:
            st.info("Tidak ada berita negatif dalam filter ini.")

# ── TAB 4: Raw Data Table ───────────────────────────────────────────────────
with tab_data:
    if filtered_df.empty:
        st.warning("Belum ada data.")
    else:
        st.markdown(f"#### Data Mentah ({len(filtered_df)} artikel)")

        search_query = st.text_input("🔍 Cari kata kunci dalam judul berita:", "")
        display_df = filtered_df.copy()
        if search_query:
            display_df = display_df[display_df["title"].str.contains(search_query, case=False, na=False)]

        st.dataframe(
            display_df[["date_str", "title", "primary_akd", "sentiment", "sentiment_score", "source_name", "url"]].sort_values(
                "date_str", ascending=False
            ),
            width="stretch",
            height=500,
        )

        # Download button
        csv = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download CSV",
            csv,
            "dpr_analysis_export.csv",
            "text/csv",
        )
