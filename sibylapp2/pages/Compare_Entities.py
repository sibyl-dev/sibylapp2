# pylint: disable=invalid-name

import streamlit as st

from sibylapp2.compute.context import get_term
from sibylapp2.view import compare_entities, filtering, sidebar
from sibylapp2.view.utils import display


def main():
    # Sidebar ------------------------------------
    sidebar.set_up_sidebar(
        model_select=True,
        entity_select=True,
        row_select=True,
        prediction=True,
        probability_select=True,
    )
    # display.show_probability_select_box()
    # filtering.view_model_select()
    # filtering.view_entity_select(eid_text="eid")

    row_ids = st.session_state["row_id_dict"][st.session_state["eid"]]

    if len(row_ids) > 1:
        filtering.view_row_select(
            st.session_state["eid"], row_ids, row_id_text="row_id", prefix="first", default=0
        )
        filtering.view_row_select(
            st.session_state["eid"], row_ids, row_id_text="row_id_comp", prefix="second", default=1
        )
        compare_entities.view_instructions(use_row_ids=True)
    else:
        display.view_prediction(st.session_state["eid"])
        filtering.view_entity_select(eid_text="eid_comp", prefix="another", default=1)
        display.view_prediction(st.session_state["eid_comp"])
        compare_entities.view_instructions()

    # Global options ------------------------------
    filtering.view_filtering()
    if len(row_ids) > 1:
        if st.session_state["row_id"] == st.session_state["row_id_comp"]:
            st.warning("Please select two different rows!")
        else:
            compare_entities.view_prediction_difference(
                st.session_state["row_id"],
                st.session_state["row_id_comp"],
                st.session_state["model_id"],
                use_row_ids=True,
                row_ids=row_ids,
                eid_for_rows=st.session_state["eid"],
            )
            compare_entities.view(
                st.session_state["model_id"],
                st.session_state["eid"],
                eid_comp=None,
                row_id=st.session_state["row_id"],
                row_id_comp=st.session_state["row_id_comp"],
            )
    else:
        if st.session_state["eid"] == st.session_state["eid_comp"]:
            st.warning("Please select two different %s!" % get_term("entity", plural=True))

        else:
            compare_entities.view_prediction_difference(
                st.session_state["eid"], st.session_state["eid_comp"], st.session_state["model_id"]
            )
            compare_entities.view(
                st.session_state["model_id"],
                st.session_state["eid"],
                eid_comp=st.session_state["eid_comp"],
                row_id=None,
                row_id_comp=None,
            )
