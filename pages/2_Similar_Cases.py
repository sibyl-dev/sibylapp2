# pylint: disable=invalid-name

import streamlit as st

from sibylapp2.view import similar_entities
from sibylapp2.view.utils import filtering, setup

setup.setup_page()

st.warning("This page is temporarily disabled for fixes")
st.stop()

# Sidebar ------------------------------------
filtering.view_entity_select()
filtering.view_filtering()
similar_entities.view_instructions()

similar_entities.view(st.session_state["eid"])
