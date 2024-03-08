# pylint: disable=invalid-name

import extra_streamlit_components as stx
import streamlit as st

from sibylapp2.compute.context import get_term
from sibylapp2.view import feature_contribution
from sibylapp2.view.utils import display, filtering

import pandas as pd


def main():
    # Sidebar ------------------------------------
    display.show_probability_select_box()
    filtering.view_model_select()
    filtering.view_selection()
    feature_contribution.view_instructions()

    # Global options ------------------------------
    filtering.view_filtering()

    feature_contribution.view(
        st.session_state["eid"],
        st.session_state["model_id"],
        key="feature_contributions",
        row_id=st.session_state["row_id"],
    )
