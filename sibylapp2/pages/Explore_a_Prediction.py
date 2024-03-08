# pylint: disable=invalid-name

import extra_streamlit_components as stx
import streamlit as st

from sibylapp2.compute.context import get_term
from sibylapp2.view import feature_contribution
from sibylapp2.view.utils import display, filtering

import pandas as pd


def get_selected_features(feature_names):
    features = []
    if "changes_to_table_feature_contributions" in st.session_state:
        changes = st.session_state["changes_to_table_feature_contributions"]["edited_rows"]
        for row in changes:
            if "Show feature plot?" in changes[row] and changes[row]["Show feature plot?"]:
                features.append(feature_names.iloc[row])
    return features


def main():
    # Sidebar ------------------------------------
    display.show_probability_select_box()
    filtering.view_model_select()
    filtering.view_selection()
    feature_contribution.view_instructions()

    tab = stx.tab_bar(
        data=[
            stx.TabBarItemData(
                id=1, title=get_term(f"{get_term('Feature')} Contributions"), description=""
            ),
            stx.TabBarItemData(
                id=2,
                title="Explore Selected %s" % get_term("Feature", plural=True),
                description="",
            ),
        ],
        default=1,
    )

    # Global options ------------------------------
    if tab == "1":
        filtering.view_filtering()

        selected_features = feature_contribution.view(
            st.session_state["eid"],
            st.session_state["model_id"],
            key="feature_contributions",
            row_id=st.session_state["row_id"],
        )
        st.write(selected_features)
    if tab == "2":
        st.write(st.session_state["changes_to_table_feature_contributions"])
