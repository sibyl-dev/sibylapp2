import streamlit as st

from sibylapp.view.utils import setup, filtering
from sibylapp.view import similar_entities
from sibylapp.compute import context


setup.setup_page()

# Sidebar ------------------------------------
filtering.view_entity_select()

similar_entities.view(st.session_state["eid"])
