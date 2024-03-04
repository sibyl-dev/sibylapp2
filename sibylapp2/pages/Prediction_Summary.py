import streamlit as st
from sibylapp2.compute import model
from sibylapp2.view.utils import display, filtering
from sibylapp2.view.utils.helpers import show_table, generate_bars
import plotly.express as px
from sibylapp2.compute.context import get_term
import pandas as pd
import extra_streamlit_components as stx
from sibylapp2 import config


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
        marker_color="#b57ae6",
    )
    st.plotly_chart(fig, use_container_width=True)


def multi_row_plot(predictions, proba_predictions=None):
    if proba_predictions:
        df = pd.DataFrame.from_dict({
            (i, j): [
                proba_predictions[i][j]
                if predictions[i][j] == 1
                else (1 - proba_predictions[i][j])
            ]
            for i in proba_predictions.keys()
            for j in proba_predictions[i].keys()
        }).T.reset_index()
    else:
        df = pd.DataFrame.from_dict({
            (i, j): [predictions[i][j]] for i in predictions.keys() for j in predictions[i].keys()
        }).T.reset_index()
    df.columns = ["EID", config.ROW_LABEL, "Value"]
    df[config.ROW_LABEL] = pd.to_datetime(df[config.ROW_LABEL])  # Convert time to datetime format

    # Create the line plot
    fig = px.line(
        df,
        x=config.ROW_LABEL,
        y="Value",
        color="EID",
        markers=True,
        color_discrete_sequence=px.colors.qualitative.G10,
    )

    # Update layout for better readability
    fig.update_layout(
        title="Values Over Time by EID",
        xaxis_title=config.ROW_LABEL,
        yaxis_title=get_term("Prediction"),
        legend_title="EID",
    )
    if proba_predictions:
        fig.update_layout(yaxis_range=[0, 1], yaxis_title="Probability")
    st.plotly_chart(fig, use_container_width=True)


def prediction_table(predictions):
    df = pd.DataFrame(predictions.items(), columns=["EID", "Prediction"])
    df["%s Visualized" % get_term("Prediction")] = generate_bars(df["Prediction"], neutral=True)
    show_table(df, key="prediction_table", enable_editing=False)


def main():
    display.show_probability_select_box(sidebar=False)
    eids = st.session_state["eids"]

    tab = stx.tab_bar(
        data=[
            stx.TabBarItemData(id=1, title=get_term(f"Summary"), description=""),
            stx.TabBarItemData(
                id=2,
                title="Interactive Table",
                description="",
            ),
        ],
        default=1,
    )
    if config.USE_ROWS:
        predictions = {
            item[0]: model.get_predictions_for_rows(item[0], item[1])
            for item in st.session_state["row_id_dict"].items()
        }
        proba_predictions = None
        if "display_proba" in st.session_state and st.session_state["display_proba"]:
            proba_predictions = {
                item[0]: model.get_predictions_for_rows(item[0], item[1], return_proba=True)
                for item in st.session_state["row_id_dict"].items()
            }
        if tab == "1":
            col1, col2 = st.columns((2, 1))
            with col1:
                multi_row_plot(predictions, proba_predictions)
        if tab == "2":
            st.warning("not implemented")
    else:
        predictions = model.get_predictions(eids)
        predictions = {eid: predictions[eid] for eid in eids}
        if tab == "1":
            col1, col2 = st.columns((2, 1))
            with col1:
                single_row_plot(predictions)
        if tab == "2":
            prediction_table(predictions)
