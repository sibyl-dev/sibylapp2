# pylint: disable=invalid-name

import extra_streamlit_components as stx
import streamlit as st

from sibylapp.compute.context import get_term
from sibylapp.view import entity_difference
from sibylapp.view.utils import filtering, formatting, setup

setup.setup_page(return_row_ids=True)


tab = stx.tab_bar(
    data=[
        stx.TabBarItemData(
            id=1,
            title=f"Difference within single {get_term('Entity', lower=True)}",
            description="",
        ),
        stx.TabBarItemData(
            id=2,
            title=f"Difference between {get_term('Entity', plural=True, lower=True)}",
            description="",
        ),
    ],
    default=1,
)


# Sidebar ------------------------------------
formatting.show_probability_select_box()
if tab == "1":
    filtering.view_entity_select(add_prediction=False)
    eid = st.session_state["eid"]
    row_ids = st.session_state["row_id_dict"][eid]
    if len(row_ids) < 2:
        st.warning(
            f"This {get_term('Entity', lower=True)} contains one or zero rows of data. Difference"
            " within this entity not well-defined."
        )
    else:
        filtering.view_time_select(eid, row_ids, row_id_text="row_id", prefix="first", default=0)
        filtering.view_time_select(
            eid, row_ids, row_id_text="row_id_comp", prefix="second", default=1
        )
        entity_difference.view_instructions(use_row_ids=True)
elif tab == "2":
    filtering.view_entity_select(eid_text="eid", prefix="first", default=0)
    filtering.view_entity_select(eid_text="eid_comp", prefix="second", default=1)
    entity_difference.view_instructions()

# Global options ------------------------------
filtering.view_filtering()
if tab == "1":
    if len(row_ids) >= 2:
        if st.session_state["row_id"] == st.session_state["row_id_comp"]:
            st.warning("Please select two different prediction times!")
        else:
            entity_difference.view_prediction_difference(
                st.session_state["row_id"],
                st.session_state["row_id_comp"],
                use_row_ids=True,
                row_ids=row_ids,
                eid_for_rows=st.session_state["eid"],
            )
            entity_difference.view(
                st.session_state["row_id"],
                st.session_state["row_id_comp"],
                use_row_ids=True,
                row_ids=row_ids,
                eid_for_rows=st.session_state["eid"],
            )
elif tab == "2":
    if st.session_state["eid"] == st.session_state["eid_comp"]:
        st.warning("Please select two different %s!" % get_term("Entity", plural=True, lower=True))

    else:
        entity_difference.view_prediction_difference(
            st.session_state["eid"], st.session_state["eid_comp"]
        )

        entity_difference.view(st.session_state["eid"], st.session_state["eid_comp"])
