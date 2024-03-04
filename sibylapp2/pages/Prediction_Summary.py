import streamlit as st
from sibylapp2.compute import model
from sibylapp2.view.utils import display
import plotly.express as px
from sibylapp2.compute.context import get_term
import pandas as pd


def single_row_plot(predictions):
    # predictions = dict(sorted(predictions.items(), key=lambda item: item[1]))
    fig = px.bar(
        x=list(predictions.values()),
        y=list(predictions.keys()),
        orientation="h",
    )
    fig.update_layout(
        xaxis_title=get_term("Prediction"),
        xaxis_title_font_size=20,
        yaxis_title="EID",
        yaxis_title_font_size=20,
        yaxis=dict(
            autorange="reversed",  # This reverses the Y-axis so that it's in ascending order
            tickmode="array",
            tickvals=list(predictions.keys()),
            ticktext=[f"{eid}" for eid in predictions.keys()],
            tickfont_size=16,
        ),
        xaxis=dict(tickfont_size=16),
    )
    fig.update_traces(
        hovertemplate="EID: %{y}<br>Prediction: %{x}<extra></extra>",  # Customize hover text
        marker_color="red",
    )
    st.plotly_chart(fig, use_container_width=True)


def main():
    display.show_probability_select_box(sidebar=False)
    eids = st.session_state["eids"]

    predictions = model.get_predictions(eids)

    col1, col2 = st.columns((2, 1))
    with col1:
        if "use_rows" in st.session_state and st.session_state["use_rows"]:
            st.warning("not yet enabled for multi row")
        else:
            single_row_plot(predictions)
