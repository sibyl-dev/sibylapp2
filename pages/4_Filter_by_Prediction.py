import streamlit as st
from sibylapp.view.utils import filtering, setup
from sibylapp.view import by_prediction, global_contributions
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
predictions = model.get_dataset_predictions()
all_contributions = contributions.get_dataset_contributions()
eids = filtering.view_prediction_selection(predictions)
filtered_contributions = filtering.filter_eids(eids, all_contributions)


tab1, tab2, tab3 = st.tabs(
    ["Average Contribution Table", "Summary plot", "Feature Distributions"]
)

with tab1:
    table = global_contributions.view(filtered_contributions)

with tab2:
    by_prediction.view_summary_plot(filtered_contributions)

with tab3:
    # Passing table in as a way of getting the features easily
    by_prediction.view_feature_plot(filtered_contributions, table)
