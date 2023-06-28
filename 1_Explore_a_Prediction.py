import streamlit as st
from sibylapp.view.utils import filtering, setup
from sibylapp.view import feature_contribution
from sibylapp.compute.context import get_term
import extra_streamlit_components as stx

setup.setup_page()

# Sidebar ------------------------------------
filtering.view_entity_select()

# Global options ------------------------------
filtering.view_filtering()

tab = stx.tab_bar(data=[
        stx.TabBarItemData(id=1, title=get_term("Feature Contributions"), description=""),
    ], default=1)

if tab == "1":
    feature_contribution.view(st.session_state["eid"])
