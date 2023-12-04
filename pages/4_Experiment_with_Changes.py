# pylint: disable=invalid-name

import copy

import streamlit as st

from sibylapp2.view import customized_entity
from sibylapp2.view.utils import display, filtering, setup

setup.setup_page(return_row_ids=True)
setup.generate_options_for_features(st.session_state["dataset_eids"])
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
        st.session_state["options_dict"],
        use_row_id=True,
        eid_for_rows=eid,
    )
else:
    changes = customized_entity.view_feature_boxes(
        eid,
        st.session_state["options_dict"],
    )

# Update displayed table after user presses the button
if st.button("Run model and explanations on customized data"):
    st.session_state["changes_to_show"] = copy.deepcopy(changes)

if "changes_to_show" in st.session_state:
    if "use_rows" in st.session_state and st.session_state["use_rows"]:
        customized_entity.view_prediction(
            st.session_state["row_id"],
            st.session_state["changes_to_show"],
            st.session_state["model_id"],
            use_row_id=True,
            eid_for_rows=eid,
        )
        filtering.view_filtering()
        customized_entity.view(
            st.session_state["eid"],
            st.session_state["changes_to_show"],
            st.session_state["model_id"],
            st.session_state["row_id"],
        )

    else:
        customized_entity.view_prediction(
            st.session_state["eid"],
            st.session_state["changes_to_show"],
            st.session_state["model_id"],
        )
        filtering.view_filtering()
        customized_entity.view(
            st.session_state["eid"],
            st.session_state["changes_to_show"],
            st.session_state["model_id"],
            None,
        )
