# pylint: disable=invalid-name

import copy

import streamlit as st

from sibylapp.view import customized_entity
from sibylapp.view.utils import filtering, formatting, setup

setup.setup_page()
setup.generate_options_for_features(
    st.session_state["dataset_eids"], st.session_state["all_features"]
)
# Sidebar ------------------------------------
formatting.show_probability_select_box()
filtering.view_entity_select()
customized_entity.view_instructions()

# Global options ------------------------------
changes = customized_entity.view_feature_boxes(
    st.session_state["eid"], st.session_state["all_features"], st.session_state["options_dict"]
)

# Update displayed table only when user press the button
if st.button("Run model and explanations on customized data"):
    st.session_state["show_changes"] = copy.deepcopy(changes)

if "show_changes" in st.session_state:
    customized_entity.view_prediction(st.session_state["eid"], st.session_state["show_changes"])
    filtering.view_filtering()

    customized_entity.view(st.session_state["eid"], st.session_state["show_changes"])
