import pandas as pd
import streamlit as st
from plotly.subplots import make_subplots

from sibylapp2.compute import contributions, features, model
from sibylapp2.compute.context import get_term
from sibylapp2.config import TIME_UNIT
from sibylapp2.log import log
from sibylapp2.view.plots import charts
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


def get_contributions_variation(eid, row_id, model_ids, bounds=None):
    """
    This function displays the contributions change over time(different models).

    The final contributions are stored in a pandas dataframe where the indices are the
    raw names of the features; the columns refer to different time points(models).
    """
    # store model predictions in the same order of the given models
    contributions_list = []
    values_list = []
    feature_name = None
    for model_id in model_ids:
        if int(model_id[:-1]) < bounds[0] or int(model_id[:-1]) > bounds[1]:
            continue
        contribution_df, value_df = contributions.get_contributions_for_rows(
            eid, [row_id], model_id=model_id
        )
        if feature_name is None:
            feature_name = contribution_df.columns

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


def plot_prediction_variation(fig, eid, row_id, model_ids, bounds=None):
    """
    This function displays the prediction change over time (different models).
    """
    # store model predictions in the same order of the given models
    timeindex = []
    probs = []
    predictions = []

    for model_id in model_ids:
        if int(model_id[:-1]) < bounds[0] or int(model_id[:-1]) > bounds[1]:
            continue
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
        fig = charts.plot_prediction_regions(df, fig, yaxis_range=[0, 1])
    else:
        fig = charts.plot_prediction_regions(df, fig)
    return fig


def plot_contributions_variation(eid, row_id, model_ids, sort_by, fig=None, bounds=None):
    """
    This function displays the feature contributions over time (different models).
    """
    wide_df, value_df = get_contributions_variation(eid, row_id, model_ids, bounds)
    wide_df = filter_contributions(wide_df, sort_by, 10)

    fig = charts.plot_temporal_line_charts(wide_df, value_df, fig, secondary_y=True)
    return fig


def view(eid, row_id, model_ids):
    """
    `row_ids` and `eid_for_rows` are only used when `use_row_ids` == True.
    `eid` and `eid_comp` are used as row_id when `use_row_ids` == True
    """
    filtering.view_filtering()
    sort_by = helpers.show_filter_options([
        "Absolute",
        f"Most {get_term('Positive')}",
        f"Most {get_term('Negative')}",
        "Greatest Change",
    ])
    fig_spot = st.empty()
    times = []
    for model_id in model_ids:
        times.append(int(model_id[:-1]))
    bounds_form = st.form("bounds_form")
    bounds = bounds_form.select_slider(
        "Lead times", options=times, key="log_lead_time_bounds", value=(times[0], times[-1])
    )
    bounds_form.form_submit_button(
        "Update",
        on_click=lambda: log(
            action="filter_lead_times",
            details={"bounds": st.session_state["log_lead_time_bounds"]},
        ),
    )
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig = plot_prediction_variation(fig, eid, row_id, model_ids, bounds)
    contribution_figure = plot_contributions_variation(
        eid, row_id, model_ids, sort_by, fig, bounds
    )
    # combine two figures
    final_figure = charts.update_figure(
        contribution_figure,
        xaxis_label=f"Lead time ({TIME_UNIT})",
        yaxis_label=get_term("Prediction"),
        yaxis2_label="Feature contribution",
    )

    fig_spot.plotly_chart(final_figure, use_container_width=True)


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
