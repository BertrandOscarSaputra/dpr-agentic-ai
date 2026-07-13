"""Home page for the Streamlit dashboard."""

import streamlit as st

st.header("🏠 Beranda")
st.markdown(
    """
    Selamat datang di **DPR Agentic AI Dashboard**.

    Sistem ini secara otomatis:
    1. **Mengumpulkan** konten dari Twitter/X dan berita online
    2. **Menganalisis** sentimen menggunakan IndoBERT
    3. **Mengklasifikasikan** ke AKD (Alat Kelengkapan Dewan) dengan Gemini
    4. **Mendeteksi** anomali tren per AKD
    5. **Menghasilkan** rekomendasi dan laporan PDF

    Gunakan sidebar untuk navigasi ke halaman detail.
    """
)
