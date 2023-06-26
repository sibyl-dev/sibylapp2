import streamlit as st

from sibylapp.view.utils import setup, filtering
from sibylapp.view import similar_entities


setup.setup_page()

# Sidebar ------------------------------------
filtering.view_entity_select()
filtering.view_filtering()

similar_entities.view(st.session_state["eid"])
