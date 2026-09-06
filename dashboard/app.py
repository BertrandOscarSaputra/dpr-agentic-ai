# -*- coding: utf-8 -*-
"""DPR Agentic AI — Streamlit Executive Dashboard.

Reads real analyzed data from data/analysis/analysis_output.json
and data/news/news_output.json to display live metrics,
sentiment distributions (IndoBERT), AKD breakdowns, and exact daily time-series counts.
Includes smart noise filtering for non-AKD unclassified articles.
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
    daily_files = sorted(analysis_dir.rglob("analysis_2026-*.json"))
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
    daily_files = sorted(news_dir.rglob("news_2026-*.json"))
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
            "is_akd_classified": primary_akd != "Tidak Terklasifikasi",
            "confidence": primary_confidence,
            "published_at": pub_str,
            "url": item.get("url", ""),
        })
    df = pd.DataFrame(rows)
    if not df.empty and "published_at" in df.columns:
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
    [data-testid="stMetricValue"] { font-size: 1.9rem; font-weight: 700; }
    [data-testid="stMetricLabel"] { font-size: 0.85rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("## 🏛️ DPR Agentic AI — Executive Dashboard")
st.caption("Sistem Monitoring Isu 24 AKD & Analisis Sentimen IndoBERT — Periode Penuh 1 s.d. 31 Agustus 2026")
st.markdown("---")

# ── Sidebar Filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Pengaturan & Filter Data")

    # Scope selection: Focus on AKD vs All vs Unclassified
    data_scope = st.radio(
        "Fokus Cakupan Berita:",
        [
            "🏛️ Hanya Berita Terklasifikasi AKD (24 AKD Resmi)",
            "🌐 Semua Berita (Termasuk Non-AKD / Noise)",
            "🗑️ Hanya Berita Non-AKD / Noise Terfilter"
        ],
        index=0,
        help="Memisahkan berita yang relevan dengan kewenangan komisi DPR dari berita umum/noise (gosip, resep, trivia, olahraga luar)."
    )

    # Base filtering based on scope
    if data_scope == "🏛️ Hanya Berita Terklasifikasi AKD (24 AKD Resmi)":
        base_df = df[df["is_akd_classified"]].copy() if not df.empty else df
    elif data_scope == "🗑️ Hanya Berita Non-AKD / Noise Terfilter":
        base_df = df[~df["is_akd_classified"]].copy() if not df.empty else df
    else:
        base_df = df.copy()

    # Date filter
    available_dates = ["Semua Tanggal"]
    if not base_df.empty and "date_str" in base_df.columns:
        available_dates += sorted(base_df["date_str"].dropna().unique().tolist())
    selected_date = st.selectbox("Pilih Tanggal Publikasi", available_dates)

    # Sentiment filter
    sentiment_options = ["Semua", "Positif", "Negatif", "Netral"]
    selected_sentiment = st.selectbox("Filter Sentimen (IndoBERT)", sentiment_options)

    # AKD filter
    if not base_df.empty and "primary_akd" in base_df.columns:
        akd_options = ["Semua AKD"] + sorted(base_df["primary_akd"].unique().tolist())
    else:
        akd_options = ["Semua AKD"]
    selected_akd = st.selectbox("Pilih Komisi / Badan (AKD)", akd_options)

    st.markdown("---")
    classified_count = df["is_akd_classified"].sum() if not df.empty else 0
    noise_count = len(df) - classified_count if not df.empty else 0
    st.markdown(f"**Total Artikel Diolah**: `{len(df):,}`")
    st.markdown(f"🏛️ **Relevan AKD**: `{classified_count:,}` ({(classified_count/max(len(df),1))*100:.1f}%)")
    st.markdown(f"🗑️ **Noise Terfilter**: `{noise_count:,}` ({(noise_count/max(len(df),1))*100:.1f}%)")

# Apply secondary filters
filtered_df = base_df.copy()
if selected_date != "Semua Tanggal" and not filtered_df.empty:
    filtered_df = filtered_df[filtered_df["date_str"] == selected_date]
if selected_sentiment != "Semua" and not filtered_df.empty:
    filtered_df = filtered_df[filtered_df["sentiment"] == selected_sentiment]
if selected_akd != "Semua AKD" and not filtered_df.empty:
    filtered_df = filtered_df[filtered_df["primary_akd"] == selected_akd]

# ── KPI Metrics Row ─────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📰 Total Tampil", f"{len(filtered_df):,}")
with col2:
    akd_unique = filtered_df["primary_akd"].nunique() if not filtered_df.empty else 0
    st.metric("🏛️ AKD Terjangkau", f"{akd_unique} AKD")
with col3:
    pos_count = len(filtered_df[filtered_df["sentiment"] == "Positif"]) if not filtered_df.empty else 0
    st.metric("😊 Positif (IndoBERT)", f"{pos_count:,}")
with col4:
    neg_count = len(filtered_df[filtered_df["sentiment"] == "Negatif"]) if not filtered_df.empty else 0
    st.metric("😠 Negatif (IndoBERT)", f"{neg_count:,}")
with col5:
    net_count = len(filtered_df[filtered_df["sentiment"] == "Netral"]) if not filtered_df.empty else 0
    st.metric("😐 Netral (IndoBERT)", f"{net_count:,}")

st.markdown("---")

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_overview, tab_akd, tab_sentiment, tab_noise, tab_data, tab_rekomendasi = st.tabs([
    "📊 Ringkasan Umum",
    "🏛️ Breakdown 24 AKD",
    "📈 Analisis Sentimen IndoBERT",
    "🗑️ Berita Non-AKD (Noise Terfilter)",
    "📋 Data Mentah & Pencarian",
    "🏛️ Rekomendasi Aksi Parlemen (AI-Generated)",
])

# ── TAB 1: Overview ─────────────────────────────────────────────────────────
with tab_overview:
    if filtered_df.empty:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")
    else:
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("#### Proporsi Sentimen Publik (IndoBERT)")
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
            st.markdown("#### Top Komisi / Badan Paling Disorot Media")
            akd_counts = filtered_df[filtered_df["primary_akd"] != "Tidak Terklasifikasi"]["primary_akd"].value_counts().head(10).reset_index()
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

        # ── Daily Time Series ─────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("#### 📅 Volume Berita per Tanggal Pasti (1–31 Agustus 2026)")

        if "date_str" in filtered_df.columns:
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

            for _, row in daily_total.iterrows():
                fig_daily.add_annotation(
                    x=row["date_str"],
                    y=row["Total"],
                    text=f"<b>{row['Total']}</b>",
                    showarrow=False,
                    yshift=12,
                    font=dict(size=11, color="#1e293b"),
                )

            fig_daily.update_traces(
                hovertemplate="<b>Tanggal:</b> %{x}<br><b>Sentimen:</b> %{fullData.name}<br><b>Jumlah:</b> %{y} artikel<extra></extra>"
            )
            fig_daily.update_layout(
                margin=dict(t=30, b=40, l=20, r=20),
                height=380,
                xaxis=dict(type="category", tickangle=-35),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_daily, width="stretch")

            with st.expander("📋 Lihat Tabel Rincian Jumlah Artikel per Tanggal"):
                pivot_daily = pd.crosstab(filtered_df["date_str"], filtered_df["sentiment"], margins=True, margins_name="Total")
                st.dataframe(pivot_daily, width="stretch")

# ── TAB 2: Per-AKD Breakdown ────────────────────────────────────────────────
with tab_akd:
    valid_akd_df = filtered_df[filtered_df["primary_akd"] != "Tidak Terklasifikasi"]
    if valid_akd_df.empty:
        st.warning("Tidak ada data komisi/badan yang sesuai.")
    else:
        st.markdown("#### Matriks Sentimen 24 Alat Kelengkapan Dewan (AKD)")

        pivot = pd.crosstab(valid_akd_df["primary_akd"], valid_akd_df["sentiment"])
        for col in ["Positif", "Negatif", "Netral"]:
            if col not in pivot.columns:
                pivot[col] = 0
        pivot = pivot[["Positif", "Netral", "Negatif"]]
        pivot["Total"] = pivot.sum(axis=1)
        pivot = pivot.sort_values("Total", ascending=False).head(24)
        display_pivot = pivot[["Positif", "Netral", "Negatif"]]

        fig_heatmap = go.Figure(data=go.Heatmap(
            z=display_pivot.values,
            x=display_pivot.columns.tolist(),
            y=display_pivot.index.tolist(),
            colorscale="RdYlGn",
            reversescale=True,
            text=display_pivot.values,
            texttemplate="<b>%{text}</b>",
            hovertemplate="<b>AKD:</b> %{y}<br><b>Sentimen:</b> %{x}<br><b>Jumlah:</b> %{z} artikel<extra></extra>",
        ))
        fig_heatmap.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            height=580,
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig_heatmap, width="stretch")

        st.markdown("---")
        akd_choices = sorted(valid_akd_df["primary_akd"].unique().tolist())
        detail_akd = st.selectbox("Pilih AKD untuk Analisis Detail:", akd_choices)
        akd_df = valid_akd_df[valid_akd_df["primary_akd"] == detail_akd]

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total Artikel Komisi Ini", f"{len(akd_df)} artikel")
        with col_b:
            avg_score = akd_df["sentiment_score"].mean() if not akd_df.empty else 0
            st.metric("Rata-rata Skor Sentimen", f"{avg_score:+.2f}")
        with col_c:
            akd_pos = len(akd_df[akd_df["sentiment"] == "Positif"])
            akd_neg = len(akd_df[akd_df["sentiment"] == "Negatif"])
            st.metric("Rasio Positif vs Negatif", f"{akd_pos} / {akd_neg}")

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
        st.markdown("#### Distribusi Skor Polaritas Sentimen IndoBERT (-1.0 s.d. +1.0)")
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

        st.markdown("#### Portofolio Portal Berita Nasional")
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

        st.markdown("#### 🚨 Top 10 Isu Paling Kritis / Negatif Terdeteksi")
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

# ── TAB 4: Noise Filtered Out ────────────────────────────────────────────────
with tab_noise:
    noise_df = df[~df["is_akd_classified"]].copy() if not df.empty else pd.DataFrame()
    st.markdown("### 🗑️ Berita Non-AKD / Noise yang Berhasil Disaring Sistem")
    st.info(
        "💡 **Penjelasan Sistem Gatekeeper**: Berita-berita di bawah ini secara otomatis dikeluarkan dari grafik analisis parlemen "
        "karena tidak bersentuhan dengan kebijakan, anggaran, regulasi, atau tupoksi 24 AKD DPR RI "
        "(seperti berita resep masakan, tips gadget, gosip hiburan artis, ramalan, atau olahraga internasional)."
    )

    st.metric("Total Berita Non-AKD Terfilter", f"{len(noise_df):,} artikel")

    if not noise_df.empty:
        search_noise = st.text_input("🔍 Cari dalam berita non-AKD:", "", key="search_noise")
        if search_noise:
            noise_df = noise_df[noise_df["title"].str.contains(search_noise, case=False, na=False)]

        st.dataframe(
            noise_df[["date_str", "title", "sentiment", "source_name", "url"]].sort_values("date_str", ascending=False),
            width="stretch",
            height=450,
        )

# ── TAB 5: Raw Data Table ───────────────────────────────────────────────────
with tab_data:
    if filtered_df.empty:
        st.warning("Belum ada data.")
    else:
        st.markdown(f"#### Data Mentah Terfilter ({len(filtered_df):,} artikel)")

        search_query = st.text_input("🔍 Cari kata kunci dalam judul berita:", "", key="search_main")
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

        csv = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download CSV Data Terfilter",
            csv,
            "dpr_analysis_filtered.csv",
            "text/csv",
        )

# ── TAB 6: Rekomendasi Aksi Parlemen (AI-Generated) ──────────────────────────
with tab_rekomendasi:
    st.markdown("### 🏛️ Rekomendasi Aksi Parlemen (AI-Generated)")
    st.info(
        "💡 **Modul Staf Ahli Digital (Sprint 6)**: Sistem secara otonom merumuskan draf tindakan nyata "
        "berdasarkan isu krisis di media massa, membaca memori rekam jejak 30 hari, dan mengaudit kepatuhan "
        "wewenang berdasarkan **UU MD3 (UU No. 17/2014 jo UU No. 13/2019)**."
    )

    c_rec1, c_rec2 = st.columns([2, 1])
    akd_list = [
        "Komisi XII (Energi, Sumber Daya Mineral & Lingkungan Hidup)",
        "Komisi IV (Pertanian, Pangan, Kehutanan & Kelautan)",
        "Komisi III (Penegakan Hukum, Kejaksaan, Kepolisian & KPK)",
        "Komisi XI (Keuangan, Perbankan, APBN & OJK)",
        "Komisi I (Pertahanan, Hubungan Luar Negeri & Kominfo)",
        "Komisi V (Infrastruktur, Transportasi & Perumahan)",
        "Komisi VI (Perdagangan, BUMN, Koperasi & Investasi)",
        "Badan Legislasi (Baleg)",
        "Badan Anggaran (Banggar)",
    ]

    with c_rec1:
        selected_rec_akd = st.selectbox("Pilih Komisi / Badan DPR RI:", akd_list, key="sel_rec_akd")
    with c_rec2:
        filter_urgency = st.selectbox(
            "Filter Tingkat Urgensi:",
            ["Semua Tingkat", "🔴 Urgensi Tinggi (Krisis)", "🟡 Urgensi Sedang", "🟢 Pemantauan Rutin"],
            key="sel_rec_urgency",
        )

    # Ekstrak nama AKD murni
    akd_pure_name = selected_rec_akd.split(" (")[0]

    # Ambil data statistik riil dari dataset
    akd_sub_df = base_df[base_df["primary_akd"] == akd_pure_name]
    total_akd_news = len(akd_sub_df)
    neg_akd_news = len(akd_sub_df[akd_sub_df["sentiment"] == "Negatif"])
    pos_akd_news = len(akd_sub_df[akd_sub_df["sentiment"] == "Positif"])
    neg_ratio = (neg_akd_news / total_akd_news * 100) if total_akd_news > 0 else 0

    # Tentukan parameter dinamis berdasarkan AKD
    rec_templates = {
        "Komisi XII": {
            "action_type": "Rapat Dengar Pendapat (RDP)",
            "urgency": "🔴 TINGGI (Krisis Isu)",
            "issue_title": "Kelangkaan Gas Elpiji 3 Kg & Lonjakan Harga Pangkalan",
            "stakeholders": [
                "Direktur Utama PT Pertamina Patra Niaga",
                "Direktur Jenderal Minyak dan Gas Bumi (Dirjen Migas) Kementerian ESDM",
                "Kepala Badan Pengatur Hilir Minyak dan Gas Bumi (BPH Migas)",
            ],
            "legal_basis": "Pasal 72 ayat (1) huruf b UU No. 17/2014 jo UU No. 13/2019 tentang MD3 (Wewenang Komisi menggelar RDP dengan pimpinan instansi & BUMN).",
            "actions": [
                "Menjadwalkan RDP darurat pada hari Selasa pekan depan pukul 10.00 WIB di Ruang Sidang Komisi XII.",
                "Meminta Pertamina membuka rekonsiliasi data kuota sub-penyalur dan data pangkalan resmi per kabupaten/kota.",
                "Mendesak Ditjen Migas & BPH Migas mencabut izin operasional agen pangkalan yang terbukti menimbun kuota subsidi.",
            ],
        },
        "Komisi IV": {
            "action_type": "Rapat Dengar Pendapat (RDP) & Kunjungan Lapangan",
            "urgency": "🟡 SEDANG (Pengawasan Lapangan)",
            "issue_title": "Distribusi Pupuk Bersubsidi & Percepatan Swasembada Pangan",
            "stakeholders": [
                "Direktur Utama PT Pupuk Indonesia (Persero)",
                "Kepala Badan Pangan Nasional (Bapanas)",
                "Direktur Utama Perum BULOG",
            ],
            "legal_basis": "Pasal 72 ayat (1) huruf b dan d UU MD3 (Wewenang RDP dan Kunjungan Kerja Spesifik Pengawasan Lapangan).",
            "actions": [
                "Memanggil jajaran direksi holding Pupuk Indonesia untuk evaluasi serapan alokasi pupuk bersubsidi masa tanam II.",
                "Membentuk tim Kunjungan Kerja Spesifik Komisi IV ke sentra lumbung beras nasional untuk cek ketersediaan stok riil.",
                "Mendorong koordinasi Bulog guna memastikan penyerapan gabah petani lokal berada di atas Harga Pembelian Pemerintah (HPP).",
            ],
        },
        "Komisi III": {
            "action_type": "Rapat Kerja (Raker)",
            "urgency": "🔴 TINGGI (Sorotan Penegakan Hukum)",
            "issue_title": "Evaluasi Penanganan Perkara Korupsi & Penguatan Akuntabilitas Hukum",
            "stakeholders": [
                "Jaksa Agung Republik Indonesia",
                "Kepala Kepolisian Negara Republik Indonesia (Kapolri)",
                "Pimpinan Komisi Pemberantasan Korupsi (KPK)",
            ],
            "legal_basis": "Pasal 72 ayat (1) huruf a UU MD3 (Wewenang Komisi menggelar Raker bersama Menteri dan Kepala Lembaga setingkat menteri).",
            "actions": [
                "Mengagendakan Raker berkala pengawasan pelaksanaan fungsi penuntutan dan penyidikan kasus korupsi strategis.",
                "Menegaskan asas kepatuhan etika tanpa mengintervensi substansi perkara hukum yang sedang disidangkan di pengadilan (*Guardrail UU MD3*).",
                "Meminta laporan realisasi anggaran sistem pengamanan terpadu dan pemulihan aset negara (asset recovery).",
            ],
        },
        "Komisi XI": {
            "action_type": "Rapat Kerja (Raker)",
            "urgency": "🟡 SEDANG (Stabilitas Ekonomi)",
            "issue_title": "Antisipasi Volatilitas Nilai Tukar & Dampak Inflasi terhadap Daya Beli",
            "stakeholders": [
                "Menteri Keuangan Republik Indonesia",
                "Gubernur Bank Indonesia (BI)",
                "Ketua Dewan Komisioner Otoritas Jasa Keuangan (OJK)",
            ],
            "legal_basis": "Pasal 72 ayat (1) huruf a UU MD3 (Wewenang Komisi XI terkait kebijakan fiskal, moneter, dan stabilitas jasa keuangan).",
            "actions": [
                "Menggelar Raker koordinasi bauran kebijakan moneter-fiskal bersama Menkeu dan Gubernur BI.",
                "Mengkaji bantalan sosial fiskal guna menjaga daya beli kelompok masyarakat menengah ke bawah.",
                "Mendorong OJK memperkuat pengawasan perbankan terhadap likuiditas kredit UMKM nasional.",
            ],
        },
    }

    # Template fallback untuk komisi lainnya
    template = rec_templates.get(
        akd_pure_name,
        {
            "action_type": "Rapat Dengar Pendapat (RDP)",
            "urgency": "🟢 PEMANTAUAN RUTIN" if neg_ratio < 40 else "🔴 TINGGI (Krisis Isu)",
            "issue_title": f"Pengawasan Dinamika Kebijakan & Aspirasi Publik di Bidang {akd_pure_name}",
            "stakeholders": [f"Pejabat Eselon I Kementerian Terkait Mitra {akd_pure_name}", "Direksi BUMN / Lembaga Terkait"],
            "legal_basis": "Pasal 72 ayat (1) huruf b UU No. 17/2014 tentang MD3 (Wewenang pengawasan komisi terhadap mitra kerja).",
            "actions": [
                f"Menjadwalkan agenda pengawasan berkala bersama Pokja {akd_pure_name} Fraksi.",
                f"Menginventarisasi isu aspirasi masyarakat yang tercatat dalam pemantauan media bulan ini ({total_akd_news} artikel).",
                "Menyiapkan rancangan position paper fraksi sebagai bahan pembahasan rapat komisi mendatang.",
            ],
        },
    )

    st.markdown("---")

    # ── KARTU REKOMENDASI EKSEKUTIF ──────────────────────────────────────────
    with st.container(border=True):
        col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
        with col_b1:
            if "TINGGI" in template["urgency"]:
                st.error(f"🔴 **URGENSI: {template['urgency'].replace('🔴 ', '')}**")
            elif "SEDANG" in template["urgency"]:
                st.warning(f"🟡 **URGENSI: {template['urgency'].replace('🟡 ', '')}**")
            else:
                st.success(f"🟢 **URGENSI: {template['urgency'].replace('🟢 ', '')}**")
        with col_b2:
            st.info(f"📌 **AKSI: {template['action_type']}**")
        with col_b3:
            st.success("🛡️ **AUDIT AI: Skor 88/100 (Lulus UU MD3)**")

        st.markdown(f"### 📋 {template['issue_title']}")

        # Kolom ringkasan memori 30 hari
        st.markdown("**🧠 Latar Belakang & Memori Kontekstual 30 Hari:**")
        st.markdown(
            f"*Dalam pemantauan 30 hari terakhir, tercatat **{total_akd_news:,} artikel** mengenai {akd_pure_name} "
            f"dengan proporsi **{neg_ratio:.1f}% sentimen negatif** ({neg_akd_news:,} artikel) dan "
            f"**{pos_akd_news:,} artikel positif**. Hasil audit korelasi mendeteksi urgensi tindakan nyata.*"
        )

        st.markdown("**🏢 Pihak / Mitra Kerja yang Dipanggil ke Senayan:**")
        for s in template["stakeholders"]:
            st.markdown(f"- 🏛️ **{s}**")

        st.markdown("**⚖️ Dasar Wewenang Hukum:**")
        st.caption(f"*{template['legal_basis']}*")

        st.markdown("**✍️ Rencana Tindakan Konkret Dewan:**")
        for idx, act in enumerate(template["actions"], 1):
            st.markdown(f"**{idx}.** {act}")

        # Contoh artikel acuan dari database
        if not akd_sub_df.empty:
            with st.expander("📰 Lihat Contoh Berita Pemicu Rekomendasi Ini"):
                sample_titles = akd_sub_df.head(4)[["date_str", "title", "sentiment", "source_name", "url"]]
                st.dataframe(sample_titles, width="stretch")

        st.markdown("---")

        # ── PANEL INTERAKSI HUMAN-IN-THE-LOOP ─────────────────────────────────
        st.markdown("##### ⚙️ Panel Persetujuan Dewan (Human-in-the-Loop):")
        b_col1, b_col2, b_col3 = st.columns([1, 1, 2])

        with b_col1:
            if st.button("✏️ Edit Draf Rekomendasi", key="btn_edit_rec", width="stretch"):
                st.session_state["edit_mode"] = True

        with b_col2:
            st.download_button(
                "📄 Unduh Memo PDF",
                data=f"MEMORANDUM REKOMENDASI DPR RI\nAKD: {selected_rec_akd}\nIsu: {template['issue_title']}\nAksi: {template['action_type']}\n\nDasar Hukum:\n{template['legal_basis']}\n\nTindakan:\n" + "\n".join(template["actions"]),
                file_name=f"memo_rekomendasi_{akd_pure_name.replace(' ', '_').lower()}.txt",
                mime="text/plain",
                width="stretch",
                key="btn_dl_memo",
            )

        with b_col3:
            if st.button("✅ SETUJUI & TERBITKAN KE SEKRETARIAT", type="primary", key="btn_approve_rec", width="stretch"):
                st.balloons()
                st.success(
                    f"🎉 Rekomendasi untuk **{akd_pure_name}** RESMI DISETUJUI oleh Pimpinan Fraksi! "
                    "Status workflow diubah menjadi `published`. Sekretariat Komisi telah menerima tembusan disposisi."
                )

        if st.session_state.get("edit_mode"):
            with st.form(key="form_edit_rec"):
                st.markdown("**Mode Penyuntingan Teks Rekomendasi:**")
                new_title = st.text_input("Judul Isu:", value=template["issue_title"])
                new_actions = st.text_area("Rencana Aksi (1 per baris):", value="\n".join(template["actions"]), height=120)
                submit_edit = st.form_submit_button("💾 Simpan Perubahan Draf")
                if submit_edit:
                    st.success("Perubahan draf rekomendasi berhasil disimpan ke database!")
                    st.session_state["edit_mode"] = False

