import streamlit as st
from sibylapp import config
from sibylapp.view.utils import filtering, setup
from sibylapp.compute import model
from sibylapp.view import feature_contribution
from sibylapp.compute.context import get_term

setup.setup_page()

# Sidebar ------------------------------------
filtering.view_entity_select()

# Global options ------------------------------
filtering.view_filtering()


(tab1,) = st.tabs(
    [
        get_term("Feature Contributions"),
    ]
)
with tab1:
    feature_contribution.view(st.session_state["eid"])
