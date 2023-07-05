import streamlit as st

from sibylapp.compute import api


@st.cache_data(show_spinner="Computing importance scores...")
def compute_importance():
    return api.fetch_importance()
