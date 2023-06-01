from sibylapp import api
import streamlit as st


@st.cache_data(show_spinner="Fetching data...")
def get_eids(max_entities=None):
    eids = api.fetch_eids()
    if max_entities is not None:
        eids = eids[:max_entities]
    return eids
