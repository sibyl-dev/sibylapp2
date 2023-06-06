import streamlit as st
from sibylapp import config
from sibylapp.compute import importance, contributions, model, entities


def setup_page(page_title=None):
    st.set_page_config(layout="wide", page_title=page_title)
    st.title("Sibyl")

    # Selecting eids -----------------------------
    if "eids" not in st.session_state:
        st.session_state["eids"] = entities.get_eids(max_entities=config.MAX_ENTITIES)

    if "dataset_eids" not in st.session_state:
        st.session_state["dataset_eids"] = entities.get_eids(
            max_entities=config.DATASET_SIZE
        )

    # Populate cache -----------------------------
    if config.LOAD_UPFRONT:
        model.get_dataset_predictions()
        contributions.get_dataset_contributions()
        importance.compute_importance()
