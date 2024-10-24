import streamlit as st

from sibylapp2.compute import context, model
from sibylapp2.config import SUPPORT_PROBABILITY, pred_format_func
from sibylapp2.log import log


def show_probability_select_box(sidebar=True):
    if sidebar:
        location = st.sidebar
    else:
        location = st
    if SUPPORT_PROBABILITY:
        location.checkbox(
            "Show probability",
            value=st.session_state["display_proba"],
            help="Display prediction in terms of probability",
            key="display_proba",
            on_change=lambda: log(
                action="toggle_probability",
                details={"display_proba": st.session_state["display_proba"]},
            ),
        )


def view_prediction(eid):
    predictions = model.get_predictions(
        st.session_state["eids"], model_id=st.session_state["model_id"]
    )
    if SUPPORT_PROBABILITY:
        predictions_proba = model.get_predictions(
            st.session_state["eids"], model_id=st.session_state["model_id"], return_proba=True
        )

    pred = predictions[eid]
    if st.session_state["display_proba"]:
        pred_proba = predictions_proba[eid]
        pred_display = (
            f"{pred_format_func(pred)} ({pred_format_func(pred_proba, display_proba=True)})"
        )
    else:
        pred_display = pred_format_func(pred)

    st.sidebar.metric(context.get_term("Prediction"), pred_display)
