# pylint: disable=invalid-name

import streamlit as st

from sibylapp.view import similar_entities
from sibylapp.view.utils import filtering, setup

setup.setup_page()

# Sidebar ------------------------------------
filtering.view_entity_select()
filtering.view_filtering()
similar_entities.view_instructions()

similar_entities.view(st.session_state["eid"])
