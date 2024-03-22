import pandas as pd
import streamlit as st
from plotly.subplots import make_subplots

from sibylapp2.compute import contributions, features, model
from sibylapp2.compute.context import get_term
from sibylapp2.config import TIME_UNIT, ROW_LABEL
from sibylapp2.view.plots import temporal_plots
from sibylapp2.view.utils import filtering, helpers


def filter_contributions(to_show, sort_by, num_features=8):
    sort_columns = to_show.drop(columns=["Feature", "Category"]).columns
    # filter by the contribution values at 0 lead
    if sort_by == "Absolute":
        to_show["Average_Abs"] = to_show[sort_columns].abs().mean(axis=1)
        to_show = to_show.sort_values(by="Average_Abs", axis=0, ascending=False)
        to_show = to_show.drop(columns="Average_Abs")
    if sort_by == f"Most {get_term('Positive')}":
        to_show["Average"] = to_show[sort_columns].mean(axis=1)
        to_show = to_show.sort_values(by="Average", axis=0, ascending=False)
        to_show = to_show.drop(columns="Average")
    if sort_by == f"Most {get_term('Negative')}":
        to_show["Average"] = to_show[sort_columns].mean(axis=1)
        to_show = to_show.sort_values(by="Average", axis=0, ascending=True)
        to_show = to_show.drop(columns="Average")
    if sort_by == "Greatest Change":
        to_show["Range"] = to_show[sort_columns].max(axis=1) - to_show[sort_columns].min(axis=1)
        to_show = to_show.sort_values(by="Range", axis=0, ascending=False)
        to_show = to_show.drop(columns="Range")
    to_show = filtering.process_options(to_show)
    return to_show.iloc[0:num_features, :]


def get_contributions_variation(
    eid,
    row_id,
    model_ids,
):
    """
    This function displays the contributions change over time(different models).

    The final contributions are stored in a pandas dataframe where the indices are the
    raw names of the features; the columns refer to different time points(models).
    """
    # store model predictions in the same order of the given models
    contributions_list = []
    values_list = []
    for model_id in model_ids:
        contribution_df, value_df = contributions.get_contributions_for_rows(
            eid, [row_id], model_id=model_id
        )

        contributions_list.append(contribution_df.iloc[0].rename(int(model_id[:-1])))
        values_list.append(value_df.iloc[0].rename(int(model_id[:-1])))
    contributions_table = pd.concat(contributions_list, axis=1)
    values_table = pd.concat(values_list, axis=1)
    feature_table = features.get_features()
    contributions_table = pd.concat([feature_table, contributions_table], axis=1)
    values_table = pd.concat([feature_table["Feature"], values_table], axis=1).set_index(
        "Feature", drop=True
    )

    return contributions_table, values_table


def prediction_plot_multimodel(
    fig,
    eid,
    row_id,
    model_ids,
):
    """
    This function displays the prediction change over time (different models).
    """
    # store model predictions in the same order of the given models
    timeindex = []
    probs = []
    predictions = []

    for model_id in model_ids:
        prediction_value = model.get_predictions_for_rows(
            eid, [row_id], model_id=model_id, return_proba=st.session_state["display_proba"]
        )[row_id]
        if st.session_state["display_proba"]:
            prediction = model.get_predictions_for_rows(
                eid,
                [row_id],
                model_id=model_id,
            )[row_id]
            # Invert the probabilities if prediction is False
            if not prediction:
                prediction_value = 1 - prediction_value

            predictions.append(prediction)
        else:
            predictions.append(prediction_value)

        timeindex.append(int(model_id[:-1]))
        probs.append(prediction_value)

    df = pd.DataFrame({"time": timeindex, "value": probs, "label": predictions})

    if st.session_state["display_proba"]:
        fig = temporal_plots.plot_prediction_regions(df, fig, yaxis_range=[0, 1])
    else:
        fig = temporal_plots.plot_prediction_regions(df, fig)
    return fig


def plot_contributions_multimodel(eid, row_id, model_ids, fig=None):
    """
    This function displays the feature contributions over time (different models).
    """
    filtering.view_filtering()
    sort_by = helpers.show_filter_options([
        "Absolute",
        f"Most {get_term('Positive')}",
        f"Most {get_term('Negative')}",
        "Greatest Change",
    ])
    wide_df, value_df = get_contributions_variation(eid, row_id, model_ids)
    wide_df = filter_contributions(wide_df, sort_by, 10)

    fig = temporal_plots.plot_temporal_line_charts(wide_df, value_df, fig, secondary_y=True)
    return fig


def view_future_predict(eid, row_id, model_ids):
    """
    If row_ids is not None, visualize change over row ids
    Else if model_ids is not None, visualize change over model ids
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig = prediction_plot_multimodel(fig, eid, row_id, model_ids)
    contribution_figure = plot_contributions_multimodel(eid, row_id, model_ids, fig)
    # combine two figures
    final_figure = temporal_plots.update_figure(
        contribution_figure,
        xaxis_label=f"Lead time ({TIME_UNIT})",
        yaxis_label=get_term("Prediction"),
        yaxis2_label="Feature contribution",
    )

    st.plotly_chart(final_figure, use_container_width=True)


def prediction_plot_multirow(fig, eid, row_ids):
    prediction_values = model.get_predictions_for_rows(
        eid, row_ids, return_proba=st.session_state["display_proba"]
    )
    if st.session_state["display_proba"]:
        predictions = model.get_predictions_for_rows(eid, row_ids)
        # TODO: convert to raw probabilities

    df = pd.DataFrame({"time": prediction_values.keys(), "value": prediction_values.values()})
    fig = temporal_plots.plot_prediction_regions(df, fig)
    return fig


def plot_contributions_multirow(eid, row_ids, fig=None):
    """
    This function displays the feature contributions over time (different models).
    """
    filtering.view_filtering()
    type = st.radio("Data to Show", ["Values", "Contributions to Prediction"], horizontal=True)
    sort_by = helpers.show_filter_options([
        "Absolute",
        f"Most {get_term('Positive')}",
        f"Most {get_term('Negative')}",
        "Greatest Change",
    ])
    contribution_df, value_df = contributions.get_contributions_for_rows(eid, row_ids)
    feature_df = features.get_features()

    if type == "Values":
        value_df = pd.concat([feature_df, value_df.T], axis=1)
        df = filter_contributions(value_df, sort_by, 10)
        value_df = None
        y_label = "Feature Value"
    else:
        contribution_df = pd.concat([feature_df, contribution_df.T], axis=1)
        value_df = pd.concat([feature_df["Feature"], value_df.T], axis=1).set_index(
            "Feature", drop=True
        )
        df = filter_contributions(contribution_df, sort_by, 10)
        y_label = "Feature contribution"

    fig = temporal_plots.plot_temporal_line_charts(
        df, value_df, fig=fig, secondary_y=True, y_label=y_label
    )
    return fig


def view_change_over_time(eid, row_ids):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig = prediction_plot_multirow(fig, eid, row_ids)
    fig = plot_contributions_multirow(eid, row_ids, fig)
    fig = temporal_plots.update_figure(
        fig,
        xaxis_label=ROW_LABEL,
        yaxis_label=get_term("Prediction"),
        # yaxis2_label="Feature contribution",
    )
    st.plotly_chart(fig, use_container_width=True)


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "This page compares the **{feature} values**, **{feature} contributions**, "
            "and model predictions of the selected {entity} at different time horizons."
            " You can select the {entity} from the dropdown above.".format(
                entity=get_term("entity"),
                feature=get_term("feature"),
            )
        )
