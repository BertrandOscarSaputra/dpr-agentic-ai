"""Reusable table components for the Streamlit dashboard."""

import pandas as pd
import streamlit as st


def content_items_table(items: list[dict]) -> None:
    """Display a table of content items."""
    if not items:
        st.warning("Belum ada data konten.")
        return

    df = pd.DataFrame(items)
    st.dataframe(df, width="stretch")


def recommendations_table(recommendations: list[dict]) -> None:
    """Display a table of recommendations with status badges."""
    if not recommendations:
        st.warning("Belum ada rekomendasi.")
        return

    df = pd.DataFrame(recommendations)
    st.dataframe(df, width="stretch")
