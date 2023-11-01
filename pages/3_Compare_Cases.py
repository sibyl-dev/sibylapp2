# pylint: disable=invalid-name

import streamlit as st

from sibylapp.compute.context import get_term
from sibylapp.view import entity_difference
from sibylapp.view.utils import display, filtering, setup

setup.setup_page(return_row_ids=True)

# Sidebar ------------------------------------
display.show_probability_select_box()
filtering.view_entity_select(eid_text="eid")
eid = st.session_state["eid"]
row_ids = st.session_state["row_id_dict"][eid]
if len(row_ids) > 1:
    filtering.view_time_select(eid, row_ids, row_id_text="row_id", prefix="first", default=0)
    filtering.view_time_select(eid, row_ids, row_id_text="row_id_comp", prefix="second", default=1)
    entity_difference.view_instructions(use_row_ids=True)
else:
    filtering.view_entity_select(eid_text="eid_comp", prefix="another", default=1)
    display.view_prediction(st.session_state["eid_comp"])
    entity_difference.view_instructions()

# Global options ------------------------------
filtering.view_filtering()
if len(row_ids) > 1:
    if st.session_state["row_id"] == st.session_state["row_id_comp"]:
        st.warning("Please select two different rows!")
    else:
        entity_difference.view_prediction_difference(
            st.session_state["row_id"],
            st.session_state["row_id_comp"],
            use_row_ids=True,
            row_ids=row_ids,
            eid_for_rows=eid,
        )
        entity_difference.view(
            st.session_state["row_id"],
            st.session_state["row_id_comp"],
            use_row_ids=True,
            row_ids=row_ids,
            eid_for_rows=eid,
        )
else:
    if st.session_state["eid"] == st.session_state["eid_comp"]:
        st.warning("Please select two different %s!" % get_term("Entity", plural=True, lower=True))

    else:
        entity_difference.view_prediction_difference(
            st.session_state["eid"], st.session_state["eid_comp"]
        )

        entity_difference.view(st.session_state["eid"], st.session_state["eid_comp"])
