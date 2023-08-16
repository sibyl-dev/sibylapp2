# pylint: disable=invalid-name

import streamlit as st

from sibylapp.compute.context import get_term
from sibylapp.view import entity_difference
from sibylapp.view.utils import filtering, setup

setup.setup_page()

# Sidebar ------------------------------------
filtering.view_entity_select(eid_text="eid", prefix="first", default=0)
filtering.view_entity_select(eid_text="eid_comp", prefix="second", default=1)
entity_difference.view_instructions()

# Global options ------------------------------
if st.session_state["eid"] == st.session_state["eid_comp"]:
    st.subheader("Please select two different %s!" % get_term("Entity", plural=True, lower=True))

else:
    filtering.view_filtering()
    entity_difference.view_prediction_difference(
        st.session_state["eid"], st.session_state["eid_comp"]
    )

    entity_difference.view(st.session_state["eid"], st.session_state["eid_comp"])
