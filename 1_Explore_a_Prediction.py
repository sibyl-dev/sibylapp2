# pylint: disable=invalid-name

import extra_streamlit_components as stx
import streamlit as st

from sibylapp.compute.context import get_term
from sibylapp.view import feature_contribution
from sibylapp.view.utils import filtering, formatting, setup

setup.setup_page()

# Sidebar ------------------------------------
formatting.show_probability_select_box()
filtering.view_entity_select()
feature_contribution.view_instructions()

# Global options ------------------------------
filtering.view_filtering()

tab = stx.tab_bar(
    data=[
        stx.TabBarItemData(id=1, title=get_term("Feature Contributions"), description=""),
    ],
    default=1,
)

if tab == "1":
    feature_contribution.view(st.session_state["eid"])
