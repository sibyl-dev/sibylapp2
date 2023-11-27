from __future__ import annotations

import pandas as pd
import streamlit as st

from sibylapp2 import config
from sibylapp2.compute import contributions, entities, features, importance, model


def setup_page(return_row_ids=False):
    st.set_page_config(layout="wide")
    st.title("Sibyl")

    # Selecting eids -----------------------------
    if return_row_ids:
        if "eids" not in st.session_state or "row_id_dict" not in st.session_state:
            st.session_state["eids"], st.session_state["row_id_dict"] = entities.get_eids(
                max_entities=config.MAX_ENTITIES, return_row_ids=True
            )
    else:
        if "eids" not in st.session_state:
            st.session_state["eids"] = entities.get_eids(max_entities=config.MAX_ENTITIES)

    if "model_ids" not in st.session_state:
        st.session_state["model_ids"] = model.get_models()

    if "model_id" not in st.session_state:
        st.session_state["model_id"] = st.session_state["model_ids"][0]

    if "dataset_eids" not in st.session_state:
        st.session_state["dataset_eids"] = entities.get_eids(max_entities=config.DATASET_SIZE)

    if "all_features" not in st.session_state:
        st.session_state["all_features"] = features.get_features(include_type=True)

    # Global display options ---------------------
    if "display_proba" not in st.session_state:
        st.session_state["display_proba"] = False
    # Populate cache -----------------------------
    if config.LOAD_UPFRONT:
        model.get_dataset_predictions()
        contributions.get_dataset_contributions()
        importance.compute_importance()


def generate_options_for_features(eids: list[str]):
    st.session_state["options_dict"] = features.get_options_for_categories(eids)
