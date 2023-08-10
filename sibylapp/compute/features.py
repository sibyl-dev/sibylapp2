import streamlit as st

from sibylapp.compute import api


@st.cache_data(show_spinner="Fetching data...")
def get_features():
    features = api.fetch_features()
    return features


@st.cache_data(show_spinner="Fetching data...")
def get_entity(eid):
    feature_values = api.fetch_entity(eid)
    return feature_values
