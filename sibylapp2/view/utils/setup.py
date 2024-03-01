from __future__ import annotations

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
                max_entities=config.get_max_entities(), return_row_ids=True
            )
    else:
        if "eids" not in st.session_state:
            st.session_state["eids"] = entities.get_eids(max_entities=config.get_max_entities())

    if "model_ids" not in st.session_state:
        # sort models in temporal order
        st.session_state["model_ids"] = sort_model_ids(model.get_models())

    if "model_id" not in st.session_state:
        st.session_state["model_id"] = st.session_state["model_ids"][0]

    if "dataset_eids" not in st.session_state:
        st.session_state["dataset_eids"] = entities.get_eids(
            max_entities=config.get_dataset_size()
        )

    if "all_features" not in st.session_state:
        st.session_state["all_features"] = features.get_features(include_type=True)

    # Global display options ---------------------
    if "display_proba" not in st.session_state:
        st.session_state["display_proba"] = False
    # Populate cache -----------------------------
    if config.get_load_upfront():
        model.get_dataset_predictions()
        contributions.get_dataset_contributions()
        importance.compute_importance()


def sort_model_ids(unsorted_model_ids: list[str]):
    """
    Designed for temporal models where model name is an integer followed by d. E.g. "10d"
    """
    return sorted(unsorted_model_ids, key=lambda name: (len(name), name))
