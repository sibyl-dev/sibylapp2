import pandas as pd
import streamlit as st

from sibylapp2.compute import contributions, model
from sibylapp2.compute.context import get_term
from sibylapp2.config import MAX_FEATURES, TIME_UNIT, pred_format_func
from sibylapp2.view.plots import charts
from sibylapp2.view.utils import filtering, helpers


def filter_contributions(to_show, sort_by, lead=0):
    # filter by the contribution values at 0 lead
    if sort_by == "Absolute":
        to_show = to_show.reindex(to_show[lead].abs().sort_values(ascending=False).index, axis=0)
    if sort_by == f"Most {get_term('Positive')}":
        to_show = to_show.sort_values(by=lead, axis=0, ascending=False)
    if sort_by == f"Most {get_term('Negative')}":
        to_show = to_show.sort_values(by=lead, axis=0)
    to_show = filtering.process_options(to_show)
    return to_show.iloc[0:MAX_FEATURES, :]


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
    feature_name = None
    for model_id in model_ids:
        contribution_df, _ = contributions.get_contributions_for_rows(
            eid, [row_id], model_id=model_id
        )
        if feature_name is None:
            feature_name = contribution_df.columns

        contributions_list.append(contribution_df.iloc[0].rename(int(model_id[:-1])))
    contributions_table = pd.concat(contributions_list, axis=1)
    contributions_table["Feature"] = feature_name

    return contributions_table


def plot_prediction_variation(
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

            predictions.append(pred_format_func(prediction))
        else:
            predictions.append(pred_format_func(prediction_value))

        timeindex.append(int(model_id[:-1]))
        probs.append(prediction_value)

    df = pd.DataFrame({"time": timeindex, "value": probs, "labels": predictions})
    # output_label = get_term("Prediction")
    # if st.session_state["display_proba"]:
    #     output_label = f"{POSITIVE_TERM} probability"
    fig = charts.plot_scatter_chart(df)
    return fig


def plot_contributions_variation(eid, row_id, model_ids, figure=None):
    """
    This function displays the feature contributions over time (different models).
    """
    filtering.view_filtering()
    sort_by = helpers.show_filter_options(
        ["Absolute", f"Most {get_term('Positive')}", f"Most {get_term('Negative')}"]
    )
    wide_df = get_contributions_variation(eid, row_id, model_ids)
    wide_df = filter_contributions(wide_df, sort_by)

    fig = charts.plot_temporal_line_charts(wide_df, figure)
    return fig


def view(eid, row_id, model_ids):
    """
    `row_ids` and `eid_for_rows` are only used when `use_row_ids` == True.
    `eid` and `eid_comp` are used as row_id when `use_row_ids` == True
    """
    figure = plot_prediction_variation(eid, row_id, model_ids)
    contribution_figure = plot_contributions_variation(eid, row_id, model_ids, figure)
    # combine two figures
    final_figure = charts.update_figure(
        contribution_figure,
        xaxis_label=f"Lead time ({TIME_UNIT})",
        yaxis_label=get_term("Prediction"),
        yaxis2_label="Feature contribution",
    )

    st.plotly_chart(final_figure, use_container_width=True)


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
