# pylint: disable=invalid-name

import streamlit as st

from sibylapp2.view import temporal_change
from sibylapp2.view.utils import display, filtering
from sibylapp2.config import SUPPORT_PROBABILITY


def main():
    # Sidebar ------------------------------------
    if SUPPORT_PROBABILITY:
        st.session_state["display_proba"] = True
    display.show_probability_select_box()
    filtering.view_selection(include_rows=False)
    temporal_change.view_instructions()
    eid = st.session_state["eid"]
    row_ids = st.session_state["row_id_dict"][eid]

    # Global options ------------------------------
    if len(row_ids) <= 1:
        st.warning("Your application does not support predicting over time.")
    else:
        temporal_change.view_change_over_time(eid, row_ids=row_ids)
