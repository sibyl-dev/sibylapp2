import streamlit as st
from sibylapp.compute import api


@st.cache_data(show_spinner="Computing model predictions...")
def compute_predictions(eids):
    predictions = api.fetch_predictions(eids)
    if "predictions" not in st.session_state:
        st.session_state["predictions"] = predictions
    else:
        st.session_state["predictions"] = dict(
            st.session_state["predictions"], **predictions
        )
    return predictions


def get_predictions(eids):
    if "predictions" not in st.session_state:
        compute_predictions(eids)
    missing_eids = list(set(eids) - st.session_state["predictions"].keys())
    if len(missing_eids) > 0:
        compute_predictions(missing_eids)
    return {eid: st.session_state["predictions"][eid] for eid in eids}
