# pylint: disable=invalid-name

import streamlit as st

from sibylapp2.view import customized_entity
from sibylapp2.view.utils import display, filtering, setup


def main():
    # Sidebar ------------------------------------
    display.show_probability_select_box()
    filtering.view_model_select()
    filtering.view_selection()
    customized_entity.view_instructions()

    # Global options ------------------------------
    eid = st.session_state["eid"]
    if "use_rows" in st.session_state and st.session_state["use_rows"]:
        changes = customized_entity.view_feature_boxes(
            st.session_state["row_id"],
            use_row_id=True,
            eid_for_rows=eid,
        )
    else:
        changes = customized_entity.view_feature_boxes(
            eid,
        )

    if len(changes) > 0:
        if "use_rows" in st.session_state and st.session_state["use_rows"]:
            customized_entity.view_prediction(
                st.session_state["row_id"],
                changes,
                st.session_state["model_id"],
                use_row_id=True,
                eid_for_rows=eid,
            )
            filtering.view_filtering()
            customized_entity.view(
                st.session_state["eid"],
                changes,
                st.session_state["model_id"],
                st.session_state["row_id"],
            )

        else:
            customized_entity.view_prediction(
                st.session_state["eid"],
                changes,
                st.session_state["model_id"],
            )
            filtering.view_filtering()
            customized_entity.view(
                st.session_state["eid"],
                changes,
                st.session_state["model_id"],
                None,
            )
    else:
        st.info("Select features to change to see modified explanation")
