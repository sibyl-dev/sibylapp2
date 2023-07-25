import streamlit as st
from sibylapp.view.utils import filtering, setup
from sibylapp.view import entity_difference
from sibylapp.compute.context import get_term
import extra_streamlit_components as stx

setup.setup_page()

# Sidebar ------------------------------------
filtering.view_entity_select()
entity_difference.view_other_entity_select()
entity_difference.view_instructions()

# Global options ------------------------------
filtering.view_filtering()
entity_difference.view_prediction_difference()

tab = stx.tab_bar(
    data=[
        stx.TabBarItemData(id=1, title=get_term("Feature Contributions"), description=""),
    ],
    default=1,
)

if tab == "1":
    entity_difference.view(st.session_state["eid"], st.session_state["eid_comp"])
