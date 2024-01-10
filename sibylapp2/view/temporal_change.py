import pandas as pd
import streamlit as st

from sibylapp2.compute import contributions, model
from sibylapp2.compute.context import get_term
from sibylapp2.config import pred_format_func
from sibylapp2.view.plots import charts
from sibylapp2.view.utils import filtering, helpers


def view_prediction_variation(
    eid,
    row_id,
    model_ids,
):
    """
    This function displays the prediction change over time(different models).
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
    fig = charts.plot_scatter_chart(df)
    st.plotly_chart(fig, use_container_width=True)


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
        df = contributions.get_contributions_for_rows(eid, [row_id], model_id=model_id)[row_id]
        if feature_name is None:
            feature_name = df["Feature"]

        contributions_list.append(df["Contribution"].rename(int(model_id[:-1])))
    contributions_table = pd.concat(contributions_list, axis=1)

    contributions_table["Feature"] = feature_name

    return contributions_table


def filter_contributions(to_show, sort_by, num_options=5):
    if sort_by == "Absolute":
        to_show = to_show.reindex(to_show[0].abs().sort_values(ascending=False).index)
    if sort_by == "Ascending":
        to_show = to_show.sort_values(by=0, axis="index")
    if sort_by == "Descending":
        to_show = to_show.sort_values(by=0, axis="index", ascending=False)
    to_show = filtering.process_options(to_show)
    return to_show.iloc[0:num_options, :]


def view(eid, row_id, model_ids):
    """
    `row_ids` and `eid_for_rows` are only used when `use_row_ids` == True.
    `eid` and `eid_comp` are used as row_id when `use_row_ids` == True
    """
    sort_by = helpers.show_filter_options(["Absolute", "Ascending", "Descending"])

    view_prediction_variation(eid, row_id, model_ids)
    wide_df = get_contributions_variation(eid, row_id, model_ids)
    wide_df = filter_contributions(wide_df, sort_by)

    fig = charts.plot_temporal_line_charts(wide_df)
    st.plotly_chart(fig, use_container_width=True)


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "This page compares the **{feature} values**, **{feature} contributions**, "
            "and model predictions of the selected {entity} at different time horizons."
            " You can select the {entity} from the dropdown above.".format(
                entity=get_term("Entity", lower=True),
                feature=get_term("Feature", lower=True),
            )
        )
