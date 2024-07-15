# pylint: disable=invalid-name

import pandas as pd
import plotly.express as px
import streamlit as st
from pandas.errors import ParserError
from streamlit_plotly_events import plotly_events

from sibylapp2 import config
from sibylapp2.compute import model
from sibylapp2.compute.context import get_term
from sibylapp2.log import log
from sibylapp2.view.utils.helpers import generate_bars, show_filter_options, show_table


def single_row_plot(predictions):
    fig = px.bar(
        x=list(predictions.values()),
        y=list(predictions.keys()),
        orientation="h",
    )
    fig.update_layout(
        xaxis_title=get_term("Prediction"),
        xaxis_title_font_size=20,
        yaxis_title=get_term("Entity"),
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
        hovertemplate=get_term("Entity")
        + ": %{y}<br>Prediction: %{x}<extra></extra>",  # Customize hover text
        marker_color="#b57ae6",
    )
    st.plotly_chart(fig, use_container_width=True)


def multi_row_plot(predictions, proba_predictions=None, x_label="X"):
    col1, col2 = st.columns((2, 1))
    with col1:
        if proba_predictions:
            vals = proba_predictions
            label = "Probability of %s" % config.pred_format_func(1)
        else:
            vals = predictions
            label = get_term("Prediction")
        df = pd.DataFrame.from_dict(
            {(i, j): [vals[i][j]] for i in vals.keys() for j in vals[i].keys()}
        ).T.reset_index()
        df.columns = [get_term("Entity"), x_label, label]
        # If the x-axis has times, convert to datetime to sort correctly
        df[x_label] = pd.to_datetime(df[x_label], errors="ignore")
        # If the x-axis is numeric, convert to numeric to sort correctly
        df[x_label] = pd.to_numeric(df[x_label], errors="ignore")
        df.sort_values(by=x_label, inplace=True)
        # Create the line plot
        fig = px.line(
            df,
            x=x_label,
            y=label,
            color=get_term("Entity"),
            markers=True,
            color_discrete_sequence=px.colors.qualitative.G10,
        )

        # Update layout for better readability
        fig.update_layout(
            xaxis_title=x_label, legend_title=get_term("Entity"), hovermode="closest"
        )
        if proba_predictions:
            fig.update_layout(yaxis_range=[0, 1])

        selected = plotly_events(fig)
    with col2:
        if len(selected) > 0:
            eid = list(predictions.keys())[selected[0]["curveNumber"]]
            st.session_state["eid"] = eid
            prediction_table(
                predictions, proba_predictions, multirow=True, selected_eid=eid, save_space=True
            )
            log(
                action="show_table",
                details={"eid": eid},
                tracking_key="prediction_summary_last_eid_table",
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
        predictions = predictions[eid]
        if proba_predictions:
            proba_predictions = proba_predictions[eid]
        df = pd.DataFrame(predictions.items(), columns=[config.ROW_LABEL, "Prediction"])
    else:
        df = pd.DataFrame(predictions.items(), columns=[get_term("Entity"), "Prediction"])
    bar_col = "Prediction"
    if proba_predictions:
        label = "Probability of %s" % config.pred_format_func(1)
        df[label] = proba_predictions.values()
        bar_col = label
    df["%s visualized" % get_term(bar_col)] = generate_bars(df[bar_col], neutral=True)
    df["Prediction"] = df["Prediction"].apply(config.pred_format_func)
    if save_space:
        button_size_mod = 2
    else:
        button_size_mod = 4
    show_table(df, key="prediction_table", button_size_mod=button_size_mod)


def pred_prob_to_raw_prob(pred_prob, pred):
    # Returns pred_prob if pred==1, 1-pred_prob otherwise
    return (1 - pred) + (-1 + 2 * pred) * pred_prob


def main():
    eids = st.session_state["eids"]

    tab = "1"
    pred_filter = None
    if config.PREDICTION_TYPE == config.PredType.BOOLEAN:
        pred_filter = show_filter_options(
            ["all", 1, 0],
            format_func=lambda x: ("all" if x == "all" else config.pred_format_func(x)),
        )

    params = config.PREDICTIONS_PARAMS
    proba_predictions = None
    if params == "rows" or "models":
        if params == "rows":
            x_label = config.ROW_LABEL
            predictions = {
                item[0]: model.get_predictions_for_rows(item[0], item[1])
                for item in st.session_state["row_id_dict"].items()
            }
            if config.SUPPORT_PROBABILITY:
                proba_predictions = {
                    item[0]: model.get_predictions_for_rows(item[0], item[1], return_proba=True)
                    for item in st.session_state["row_id_dict"].items()
                }
        elif params == "models":
            x_label = config.MODEL_LABEL
            predictions = {
                model_id: model.get_predictions(eids, model_id=model_id)
                for model_id in model.get_models()
            }
            predictions = {
                eid: {model_id: predictions[model_id][eid] for model_id in predictions}
                for eid in predictions[next(iter(predictions))]
            }
            if config.SUPPORT_PROBABILITY:
                proba_predictions = {
                    model_id: model.get_predictions(eids, model_id=model_id, return_proba=True)
                    for model_id in model.get_models()
                }
                proba_predictions = {
                    eid: {
                        model_id: proba_predictions[model_id][eid]
                        for model_id in proba_predictions
                    }
                    for eid in proba_predictions[next(iter(proba_predictions))]
                }

            if proba_predictions is not None:
                # Convert the outcome probability to raw probability
                proba_predictions = {
                    eid: {
                        item: pred_prob_to_raw_prob(
                            proba_predictions[eid][item], predictions[eid][item]
                        )
                        for item in proba_predictions[eid]
                    }
                    for eid in proba_predictions
                }
            if pred_filter and pred_filter != "all":
                eids = [eid for eid in eids if any(predictions[eid].values()) == pred_filter]
                predictions = {
                    eid: {row_id: predictions[eid][row_id] for row_id in predictions[eid]}
                    for eid in eids
                }
                if proba_predictions:
                    proba_predictions = {
                        eid: {
                            row_id: proba_predictions[eid][row_id]
                            for row_id in proba_predictions[eid]
                        }
                        for eid in eids
                    }
            if tab == "1":
                multi_row_plot(predictions, proba_predictions, x_label)
            if tab == "2":
                prediction_table(predictions, proba_predictions, multirow=True)
    elif params is None:
        predictions = model.get_predictions(eids)
        if pred_filter and pred_filter != "all":
            eids = [eid for eid in eids if predictions[eid] == pred_filter]
        predictions = {eid: predictions[eid] for eid in eids}
        if tab == "1":
            single_row_plot(predictions)
        if tab == "2":
            prediction_table(predictions)

    log(
        action="change_tab",
        details={"tab": tab},
        tracking_key="prediction_summary_last_tab_logged",
    )
    if "eid" in st.session_state:
        st.sidebar.write(f"Selected {get_term('Entity')}: {st.session_state['eid']}")
