import streamlit as st

from sibylapp import config
from sibylapp.compute import contributions, entities, features, importance, model


def setup_page():
    st.set_page_config(layout="wide")
    st.title("Sibyl")

    # Selecting eids -----------------------------
    if "eids" not in st.session_state:
        st.session_state["eids"] = entities.get_eids(max_entities=config.MAX_ENTITIES)

    if "dataset_eids" not in st.session_state:
        st.session_state["dataset_eids"] = entities.get_eids(max_entities=config.DATASET_SIZE)

    if "all_features" not in st.session_state:
        st.session_state["all_features"] = features.get_features()

    # Populate cache -----------------------------
    if config.LOAD_UPFRONT:
        model.get_dataset_predictions()

        contributions.get_dataset_contributions()
        importance.compute_importance()
