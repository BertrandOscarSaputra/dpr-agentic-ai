"""AKD Dashboard page — per-AKD analysis breakdown."""

import json
from pathlib import Path

import streamlit as st

AKD_MASTER_PATH = Path(__file__).resolve().parents[2] / "kamus" / "akd_master.json"


@st.cache_data
def load_akd_list() -> list[str]:
    """Load AKD names from the master JSON file."""
    with open(AKD_MASTER_PATH) as f:
        data = json.load(f)
    return [entry["name"] for entry in data["akd"]]


st.header("📊 Dashboard per AKD")

akd_list = load_akd_list()

selected_akd = st.selectbox("Pilih AKD:", akd_list)

st.markdown(f"### Analisis untuk: **{selected_akd}**")

# TODO: Fetch data from API and display charts
st.info("Data analisis akan ditampilkan di sini setelah sistem berjalan.")
