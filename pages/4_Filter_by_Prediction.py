import streamlit as st
from sibylapp.view.utils import filtering, setup
from sibylapp.view import by_prediction
from sibylapp.compute import entities, model, contributions
from sibylapp import config
import numpy as np
import pandas as pd


@st.cache_data(show_spinner="Getting relevant entries...")
def get_relevant_contributions(preds, _predictions, _contribution_results):
    eids = [eid for eid in _predictions if _predictions[eid] in preds]
    return {eid: _contribution_results[eid] for eid in eids}


@st.cache_data(show_spinner="Getting relevant entries...")
def get_relevant_contributions_range(pred_range, _predictions, _contribution_results):
    eids = [
        eid
        for eid in _predictions
        if pred_range[0] <= _predictions[eid] <= pred_range[1]
    ]
    return {eid: _contribution_results[eid] for eid in eids}


setup.setup_page()


# Global options ------------------------------
filtering.view_filtering()

# Compute all data ----------------------------
if "dataset_eids" not in st.session_state:
    st.session_state["dataset_eids"] = entities.get_eids(config.DATASET_SIZE)
predictions = model.get_predictions(st.session_state["dataset_eids"])
contributions_results = contributions.get_contributions(
    st.session_state["dataset_eids"]
)

# Select predictions of interest --------------
pred_values = list(predictions.values())
if len(np.unique(pred_values)) <= 2:
    chosen_pred = st.selectbox(
        "Predictions to visualize",
        [pred for pred in np.unique(pred_values)],
        format_func=config.pred_format_func,
    )
    relevant_contributions = get_relevant_contributions(
        [chosen_pred], predictions, contributions_results
    )
elif len(np.unique(pred_values)) < 8:  # TODO: ensure non-numeric fall in this category
    chosen_preds = st.multiselect(
        "Predictions to visualize",
        [pred for pred in np.unique(pred_values)],
        default=[np.unique(pred_values)[0]],
        format_func=config.pred_format_func,
    )
    relevant_contributions = get_relevant_contributions(
        chosen_preds, predictions, contributions_results
    )
else:
    min_pred = min(pred_values)
    max_pred = max(pred_values)
    pred_range = st.slider(
        "Predictions to visualize", min_pred, max_pred, (min_pred, max_pred)
    )
    relevant_contributions = get_relevant_contributions_range(
        pred_range, predictions, contributions_results
    )


tab1, tab2, tab3 = st.tabs(
        ["Average Contribution Table", "Summary plot", "Feature Distributions"]
    )

with tab1:
    table = by_prediction.view_table(relevant_contributions)

with tab2:
    by_prediction.view_summary_plot(relevant_contributions)

with tab3:
    # Passing table in as a way of getting the features easily
    by_prediction.view_feature_plot(relevant_contributions, table)
