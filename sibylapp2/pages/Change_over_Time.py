# pylint: disable=invalid-name

import streamlit as st

from sibylapp2.view import temporal_change
from sibylapp2.view.utils import display, filtering


def main():
    # Sidebar ------------------------------------
    st.session_state["display_proba"] = True
    display.show_probability_select_box()
    filtering.view_selection()
    temporal_change.view_instructions()
    eid = st.session_state["eid"]
    row_ids = st.session_state["row_id_dict"][eid]
    model_ids = st.session_state["model_ids"]

    # Global options ------------------------------
    if len(row_ids) <= 1 or len(model_ids) <= 1:
        st.warning("Your application does not support predicting over time.")
    else:
        temporal_change.view(eid, st.session_state["row_id"], model_ids=model_ids)
