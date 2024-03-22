import streamlit as st

from sibylapp2.compute import api, entities
from sibylapp2.config import get_dataset_size


def get_models():
    models = api.fetch_models()
    return models


@st.cache_data(show_spinner="Getting model predictions...")
def get_predictions(eids, row_ids=None, model_id=api.fetch_model_id(), return_proba=False):
    """
    Get predictions for the given IDs

    Args:
        eids (list): eids to get predictions for
        row_ids (list): row_ids to get predictions for
        model_id (str): model to predict with
        return_proba (bool): whether to return probabilities or not

    Returns:
        dict: dictionary of predictions given as {eid: {row_id: prediction}}
    """
    predictions = {}
    for eid in eids:
        predictions[eid] = api.fetch_predictions(
            [eid], row_ids, model_id=model_id, return_proba=return_proba
        )
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
        st.session_state["dataset_eids"] = entities.get_eids(get_dataset_size())
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
