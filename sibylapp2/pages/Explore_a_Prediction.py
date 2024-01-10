# pylint: disable=invalid-name

import extra_streamlit_components as stx
import streamlit as st

from sibylapp2.compute.context import get_term
from sibylapp2.view import feature_contribution
from sibylapp2.view.utils import display, filtering, setup


def main():
    # Sidebar ------------------------------------
    display.show_probability_select_box()
    filtering.view_model_select()
    filtering.view_selection()
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
        row_id = None
        if "row_id" in st.session_state:
            row_id = st.session_state["row_id"]
        feature_contribution.view(
            st.session_state["eid"], st.session_state["model_id"], st.session_state["row_id"]
        )
