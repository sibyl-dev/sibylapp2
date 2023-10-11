import streamlit as st

from sibylapp.compute import api, entities


@st.cache_data(show_spinner="Getting model predictions...")
def get_predictions(eids, return_proba=False):
    predictions = api.fetch_predictions(eids, return_proba=return_proba)
    return predictions


@st.cache_data(show_spinner="Getting model predictions...")
def get_predictions_for_rows(eid, row_ids, return_proba=False):
    predictions = api.fetch_predictions([eid], row_ids, return_proba=return_proba)
    return predictions


@st.cache_data(show_spinner="Getting model predictions...")
def get_dataset_predictions(return_proba=False):
    if "dataset_eids" not in st.session_state:
        st.session_state["dataset_eids"] = entities.get_eids(1000)
    return get_predictions(st.session_state["dataset_eids"], return_proba)


@st.cache_data(show_spinner="Getting predictions for your data...")
def get_modified_prediction(eid, changes, return_proba=False):
    return api.fetch_modified_prediction(eid, changes, return_proba=return_proba)
