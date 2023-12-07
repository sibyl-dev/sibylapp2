import altair as alt
import pandas as pd
import streamlit as st

from sibylapp2.compute import context, model
from sibylapp2.config import SUPPORT_PROBABILITY, pred_format_func


def show_probability_select_box():
    if SUPPORT_PROBABILITY:
        st.sidebar.checkbox(
            "Show probability",
            value=st.session_state["display_proba"],
            help="Display prediction in terms of probability",
            key="display_proba",
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


def plot_temporal_line_charts(df: pd.DataFrame):
    """
    Transform dataframe from wide form to long form for streamlit visualizations.
    """
    df = df.set_index("Feature").transpose().reset_index(names=["time"])

    df = df.melt(
        id_vars=["time"],
        value_vars=set(df.columns) - set(["time"]),
        var_name="feature",
        value_name="contribution",
    )
    chart = (
        alt.Chart(df).mark_line(point=True).encode(x="time", y="contribution:Q", color="feature:N")
    )
    st.altair_chart(chart, use_container_width=True)
