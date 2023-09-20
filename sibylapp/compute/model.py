import streamlit as st

from sibylapp.compute import api, entities


@st.cache_data(show_spinner="Computing model predictions...")
def compute_predictions(eids):
    predictions = api.fetch_predictions(eids)
    if "predictions" not in st.session_state:
        st.session_state["predictions"] = predictions
    else:
        st.session_state["predictions"] = dict(st.session_state["predictions"], **predictions)
    return predictions


@st.cache_data(show_spinner="Getting predictions...")
def get_predictions(eids):
    if "predictions" not in st.session_state:
        predictions = compute_predictions(eids)
    else:
        predictions = st.session_state["predictions"]
    missing_eids = list(set(eids) - predictions.keys())
    if len(missing_eids) > 0:
        predictions = {**predictions, **compute_predictions(missing_eids)}
    return {eid: predictions[eid] for eid in eids}


@st.cache_data(show_spinner="Getting predictions...")
def get_predictions_for_rows(eid, row_ids):
    if "predictions_rows" not in st.session_state:
        predictions = api.fetch_predictions([eid], row_ids)
    else:
        predictions = st.session_state["predictions_rows"]
    return predictions


@st.cache_data(show_spinner="Getting contributions...")
def get_dataset_predictions():
    if "dataset_eids" not in st.session_state:
        st.session_state["dataset_eids"] = entities.get_eids(1000)
    return get_predictions(st.session_state["dataset_eids"])


@st.cache_data(show_spinner="Getting predictions for your data...")
def get_modified_prediction(eid, changes):
    st.session_state["modified_prediction"] = api.fetch_modified_prediction(eid, changes)
    return st.session_state["modified_prediction"]
