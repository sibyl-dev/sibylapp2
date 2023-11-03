# pylint: disable=invalid-name

import extra_streamlit_components as stx
import streamlit as st

from sibylapp2.compute.context import get_term
from sibylapp2.view import feature_contribution
from sibylapp2.view.utils import filtering, setup

setup.setup_page(return_row_ids=True)

# Sidebar ------------------------------------
filtering.view_selection()
feature_contribution.view_instructions()

# Global options ------------------------------
filtering.view_filtering()

tab = stx.tab_bar(
    data=[
        stx.TabBarItemData(id=1, title=get_term("Feature Contributions"), description=""),
    ],
    default=1,
)

if tab == "1":
    if st.session_state["use_rows"]:
        feature_contribution.view(
            st.session_state["row_id"], use_row_id=True, eid_for_rows=st.session_state["eid"]
        )
    else:
        feature_contribution.view(st.session_state["eid"])
