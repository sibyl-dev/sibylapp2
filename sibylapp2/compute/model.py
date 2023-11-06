import streamlit as st

from sibylapp2.compute import api, entities


def get_models():
    models = api.fetch_models()
    return models


@st.cache_data(show_spinner="Getting model predictions...")
def get_predictions(eids, model_id=api.fetch_model_id(), return_proba=False):
    predictions = api.fetch_predictions(eids, model_id=model_id, return_proba=return_proba)
    return predictions


@st.cache_data(show_spinner="Getting model predictions...")
def get_predictions_for_rows(eid, row_ids, model_id=api.fetch_model_id(), return_proba=False):
    predictions = api.fetch_predictions(
        [eid], row_ids, model_id=model_id, return_proba=return_proba
    )
    return predictions


@st.cache_data(show_spinner="Getting model predictions...")
def get_dataset_predictions(model_id=api.fetch_model_id(), return_proba=False):
    if "dataset_eids" not in st.session_state:
        st.session_state["dataset_eids"] = entities.get_eids(1000)
    return get_predictions(
        st.session_state["dataset_eids"], model_id=model_id, return_proba=return_proba
    )


@st.cache_data(show_spinner="Getting predictions for your data...")
def get_modified_prediction(
    eid, changes, row_id=None, model_id=api.fetch_model_id(), return_proba=False
):
    return api.fetch_modified_prediction(
        eid, changes, row_id=row_id, model_id=model_id, return_proba=return_proba
    )
