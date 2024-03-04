import streamlit as st
from sibylapp2.compute import model
from sibylapp2.view.utils import display, filtering
from sibylapp2.view.utils.helpers import show_table, generate_bars
import plotly.express as px
from sibylapp2.compute.context import get_term
import pandas as pd
import extra_streamlit_components as stx
from sibylapp2 import config
from streamlit_plotly_events import plotly_events


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
    col1, col2 = st.columns((2, 1))
    with col1:
        if proba_predictions:
            vals = proba_predictions
            label = "Probability"
        else:
            vals = predictions
            label = get_term("Prediction")
        df = pd.DataFrame.from_dict(
            {(i, j): [vals[i][j]] for i in vals.keys() for j in vals[i].keys()}
        ).T.reset_index()
        df.columns = ["EID", config.ROW_LABEL, label]
        df[config.ROW_LABEL] = pd.to_datetime(
            df[config.ROW_LABEL]
        )  # Convert time to datetime format

        # Create the line plot
        fig = px.line(
            df,
            x=config.ROW_LABEL,
            y=label,
            color="EID",
            markers=True,
            color_discrete_sequence=px.colors.qualitative.G10,
        )

        # Update layout for better readability
        fig.update_layout(xaxis_title=config.ROW_LABEL, legend_title="EID", hovermode="closest")
        if proba_predictions:
            fig.update_layout(yaxis_range=[0, 1])
        # st.plotly_chart(fig, use_container_width=True)
        selected = plotly_events(fig)
    with col2:
        if len(selected) > 0:
            eid = list(predictions.keys())[selected[0]["curveNumber"]]
            prediction_table(
                predictions, proba_predictions, multirow=True, selected_eid=eid, save_space=True
            )


def prediction_table(
    predictions, proba_predictions=None, multirow=False, selected_eid=None, save_space=False
):
    if multirow:
        if not selected_eid:
            eid = st.selectbox(
                "Select %s" % get_term("Entity", with_a=True), list(predictions.keys())
            )
        else:
            eid = selected_eid
            st.write(eid)
        predictions = predictions[eid]
        if proba_predictions:
            proba_predictions = proba_predictions[eid]
        df = pd.DataFrame(predictions.items(), columns=[config.ROW_LABEL, "Prediction"])
    else:
        df = pd.DataFrame(predictions.items(), columns=["EID", "Prediction"])
    if proba_predictions:
        df["Probability"] = proba_predictions.values()
    bar_col = "Probability" if proba_predictions else "Prediction"
    df["%s Visualized" % get_term(bar_col)] = generate_bars(df[bar_col], neutral=True)
    df["Prediction"] = df["Prediction"].apply(config.pred_format_func)
    if save_space:
        button_size_mod = 2
    else:
        button_size_mod = 4
    show_table(df, key="prediction_table", enable_editing=False, button_size_mod=button_size_mod)


def pred_prob_to_raw_prob(pred_prob, pred):
    # Returns pred_prob if pred==1, 1-pred_prob otherwise
    return (1 - pred) + (-1 + 2 * pred) * pred_prob


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
            # Convert the outcome probability to raw probability
            proba_predictions = {
                eid: {
                    row_id: pred_prob_to_raw_prob(
                        proba_predictions[eid][row_id], predictions[eid][row_id]
                    )
                    for row_id in proba_predictions[eid]
                }
                for eid in proba_predictions
            }
        if tab == "1":
            multi_row_plot(predictions, proba_predictions)
        if tab == "2":
            prediction_table(predictions, proba_predictions, multirow=True)
    else:
        predictions = model.get_predictions(eids)
        predictions = {eid: predictions[eid] for eid in eids}
        if tab == "1":
            single_row_plot(predictions)
        if tab == "2":
            prediction_table(predictions)
