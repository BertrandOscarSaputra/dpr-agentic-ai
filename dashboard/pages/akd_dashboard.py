"""AKD Dashboard page — per-AKD analysis breakdown."""

import streamlit as st

st.header("📊 Dashboard per AKD")

akd_list = [
    "BURT", "MKD", "Baleg", "BAKN", "BKSAP", "BPKPH",
    "Komisi I", "Komisi II", "Komisi III", "Komisi IV",
    "Komisi V", "Komisi VI", "Komisi VII", "Komisi VIII",
    "Komisi IX", "Komisi X", "Komisi XI",
    "Pimpinan DPR",
]

selected_akd = st.selectbox("Pilih AKD:", akd_list)

st.markdown(f"### Analisis untuk: **{selected_akd}**")

# TODO: Fetch data from API and display charts
st.info("Data analisis akan ditampilkan di sini setelah sistem berjalan.")
