# pylint: disable=invalid-name

import extra_streamlit_components as stx
import streamlit as st

from sibylapp import config
from sibylapp.compute.context import get_term
from sibylapp.view import feature_contribution
from sibylapp.view.utils import filtering, setup

setup.setup_page()

# Sidebar ------------------------------------
if config.USE_ROWS:
    filtering.view_entity_select(add_prediction=False)
    eid = st.session_state["eid"]
    row_ids = st.session_state["row_id_dict"][eid]
    filtering.view_time_select(eid, row_ids, row_id_text="row_id")
else:
    filtering.view_entity_select()

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
    if config.USE_ROWS:
        feature_contribution.view(st.session_state["row_id"], use_row_id=True, eid_for_rows=eid)
    else:
        feature_contribution.view(st.session_state["eid"])
