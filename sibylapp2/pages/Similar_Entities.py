# pylint: disable=invalid-name

import streamlit as st

from sibylapp2.view import similar_entities
from sibylapp2.view.utils import filtering


def main():
    # Sidebar ------------------------------------
    filtering.view_model_select()
    filtering.view_entity_select()
    filtering.view_filtering()
    similar_entities.view_instructions()

    similar_entities.view(st.session_state["eid"], model_id=st.session_state["model_id"])
