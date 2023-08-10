# pylint: disable=invalid-name

import extra_streamlit_components as stx
import streamlit as st

from sibylapp.compute.context import get_term
from sibylapp.view import customized_entity
from sibylapp.view.utils import filtering, setup

setup.setup_page()

# Sidebar ------------------------------------
filtering.view_entity_select()
customized_entity.view_instructions()

# Global options ------------------------------
customized_entity.view_feature_boxes(st.session_state["eid"], st.session_state["all_features"])

if st.button("Run model and explanations on customized data"):
    customized_entity.view_prediction(st.session_state["eid"], st.session_state["changes"])
    filtering.view_filtering()
    tab = stx.tab_bar(
        data=[
            stx.TabBarItemData(
                id=1, title=get_term("Compare Feature Contributions"), description=""
            ),
        ],
        default=1,
    )

    if tab == "1":
        customized_entity.view(st.session_state["eid"], st.session_state["changes"])
