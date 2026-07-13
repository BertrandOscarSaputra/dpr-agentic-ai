"""DPR Agentic AI — Streamlit Dashboard."""

import streamlit as st

st.set_page_config(
    page_title="DPR Agentic AI Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏛️ DPR Agentic AI Dashboard")
st.markdown("**Klasifikasi AKD & Analisis Sentimen DPR RI**")

st.markdown("---")

# Overview metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Konten", "0", help="Total content items collected")
with col2:
    st.metric("Sudah Dianalisis", "0", help="Content items analyzed")
with col3:
    st.metric("Anomali Aktif", "0", help="Active trend anomalies")
with col4:
    st.metric("Rekomendasi Draft", "0", help="Recommendations pending review")

st.markdown("---")
st.info("👈 Gunakan sidebar untuk navigasi ke halaman detail.")
