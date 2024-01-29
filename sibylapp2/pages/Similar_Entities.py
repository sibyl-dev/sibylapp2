# pylint: disable=invalid-name

import streamlit as st

from sibylapp2.view import similar_entities, filtering, sidebar


def main():
    # Sidebar ------------------------------------
    sidebar.view_model_select()
    sidebar.view_entity_select()
    filtering.view_filtering()
    similar_entities.view_instructions()

    similar_entities.view(st.session_state["eid"], model_id=st.session_state["model_id"])
