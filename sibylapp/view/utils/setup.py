import streamlit as st
from sibylapp import config
from sibylapp.compute import importance, contributions, model, entities


def setup_page():
    st.set_page_config(layout="wide")
    st.title("Sibyl")

    # Selecting eids -----------------------------
    if "eids" not in st.session_state:
        st.session_state["eids"] = entities.get_eids(max_entities=config.MAX_ENTITIES)

    if "dataset_eids" not in st.session_state:
        st.session_state["dataset_eids"] = entities.get_eids(max_entities=config.DATASET_SIZE)

    # Populate cache -----------------------------
    if config.LOAD_UPFRONT:
        all_eids = list(set(st.session_state["eids"] + st.session_state["dataset_eids"]))
        model.get_predictions(all_eids)
        contributions.get_contributions(all_eids)
        importance.compute_importance()