import streamlit as st
from sibylapp import api


@st.cache_data
def predictions(eids):
    return api.fetch_predictions(eids)
