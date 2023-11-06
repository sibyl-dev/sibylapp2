from __future__ import annotations

import pandas as pd
import streamlit as st

from sibylapp2.compute import contributions, model
from sibylapp2.compute.context import get_term
from sibylapp2.compute.features import get_entity
from sibylapp2.config import pred_format_func
from sibylapp2.view.entity_difference import sort_contributions, view_compare_cases_helper
from sibylapp2.view.utils import helpers
from sibylapp2.view.utils.formatting import format_two_contributions_to_view
from sibylapp2.view.utils.helpers import show_text_input_side_by_side


def view_feature_boxes(
    eid: str,
    features_df: pd.DataFrame,
    options_dict: dict[str, list[str | int | float]],
    use_row_id: bool = False,
    eid_for_rows: str | None = None,
):
    if "changes" not in st.session_state:
        st.session_state["changes"] = {}

    if use_row_id:
        entity = get_entity(eid_for_rows, eid)
    else:
        entity = get_entity(eid)
    changes = {}

    selected_features = st.multiselect(
        "Select %s to change:" % get_term("Feature", lower=True, plural=True),
        features_df.index.tolist(),
        default=list(st.session_state["changes"].keys()),
        format_func=lambda feat: features_df.loc[feat, "Feature"],
        key="selected_features",
        placeholder="Select one or multiple %s" % get_term("Feature", lower=True, plural=True),
    )
    for feature in selected_features:
        # Sibyl-api expects the raw feature names as input for changes
        default_input = entity[feature]
        if feature in st.session_state["changes"].keys():
            default_input = st.session_state["changes"][feature]

        numeric = True
        options = None
        if features_df.loc[feature, "type"] != "numeric":
            numeric = False
            options = options_dict[feature]

        changes[feature] = show_text_input_side_by_side(
            f"New value for **{features_df.loc[feature, 'Feature'].strip()}**",
            options=options,
            default_input=default_input,
            numeric=numeric,
        )
    return changes


def view_prediction(eid, changes, model_id, use_row_id=False, eid_for_rows=None):
    if use_row_id:
        pred = model.get_modified_prediction(eid_for_rows, changes, row_id=eid, model_id=model_id)
    else:
        pred = model.get_modified_prediction(eid, changes, model_id=model_id)
    if st.session_state["display_proba"]:
        if use_row_id:
            pred_proba = model.get_modified_prediction(
                eid_for_rows,
                changes,
                row_id=eid,
                model_id=model_id,
                return_proba=True,
            )
        else:
            pred_proba = model.get_modified_prediction(
                eid, changes, model_id=model_id, return_proba=True
            )
        pred_display = (
            pred_format_func(pred) + " (" + pred_format_func(pred_proba, display_proba=True) + ")"
        )
    else:
        pred_display = pred_format_func(pred)
    st.metric(
        "Model's {prediction} of modified {entity}:".format(
            prediction=get_term("Prediction", lower=True),
            entity=get_term("Entity"),
        ),
        pred_display,
    )


def highlight_differences(to_show, changes, columns=None):
    if columns is None:
        columns = to_show.columns

    def highlight_row(row):
        style = "background-color: yellow" if str(row.name) in changes.keys() else ""
        return [style if col in columns else "" for col in to_show.columns]

    to_show = to_show.style.apply(highlight_row, axis=1)

    return to_show


def filter_different_rows(eid, to_show):
    neighbor_col = to_show["%s Value for %s %s" % (get_term("Feature"), get_term("Entity"), eid)]
    selected_col = to_show["%s Value for modified %s" % (get_term("Feature"), get_term("Entity"))]
    to_show_filtered = to_show[neighbor_col != selected_col]
    return to_show_filtered


def view(eid, changes, model_id, use_row_id=False, eid_for_rows=None, save_space=False):
    """
    eid is used as `row_id` when use_row_id is True
    """
    sort_by, show_number, show_contribution = view_compare_cases_helper(save_space=save_space)
    if use_row_id:
        original_df = contributions.get_contributions_for_rows(
            eid_for_rows, [eid], model_id=model_id
        )[eid]
        other_df = contributions.get_contribution_for_modified_data(
            eid_for_rows, changes, eid, model_id=model_id
        )
    else:
        original_df = contributions.get_contributions([eid], model_id=model_id)[eid]
        other_df = contributions.get_contribution_for_modified_data(
            eid, changes, model_id=model_id
        )
    to_show = format_two_contributions_to_view(
        original_df,
        other_df,
        lsuffix=" for %s %s" % (get_term("Entity"), eid),
        rsuffix=" for modified %s" % get_term("Entity"),
        show_number=show_number,
        show_contribution=show_contribution,
    )
    options = ["No filtering", "With filtering"]
    show_different = st.radio(
        "Filter out identical %s values?" % get_term("Feature", lower=True),
        options,
        horizontal=True,
        help="Show only rows where %s values of two %s are different"
        % (get_term("Feature", lower=True), get_term("Entity", lower=True, plural=True)),
    )
    if show_different == "With filtering":
        to_show = filter_different_rows(eid, to_show)

    to_show = sort_contributions(to_show, sort_by).drop(
        "Contribution Change Value", axis="columns"
    )

    helpers.show_table(
        to_show,
        style_function=lambda df: highlight_differences(
            df,
            changes,
            columns=["%s Value for modified %s" % (get_term("Feature"), get_term("Entity"))],
        ),
    )


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "This page presents the change in **prediction** and **{feature} contribution**"
            " by the selected_features you added to the selected {entity}.".format(
                feature=get_term("Feature", lower=True), entity=get_term("Entity")
            )
        )
        st.markdown(
            "First, you **select {a_entity}** from the dropdown on the sidebar as a **baseline for"
            " comparison**. Next, you can **select {features}** from the selection bar and **enter"
            " new values** for these {features}. Keep in mind that the {feature} values must be"
            " valid; otherwise, the server will throw an internal error. Finally, when you are"
            " happy with your edits, you can **press the button** right below to see the model's"
            " prediction and the {feature} contribution of the {entity} you just created. The"
            " {features} that have a different value from that of the original will be highlighted"
            " in the table.".format(
                a_entity=get_term("Entity", with_a=True, lower=True),
                entity=get_term("Entity", lower=True),
                feature=get_term("Feature", lower=True),
                features=get_term("Feature", lower=True, plural=True),
            )
        )
        st.markdown(
            "The layout and formatting functions in the following table are very similar to that"
            " in the **Compare Cases** page. However, we provide a different filter here. You can"
            " focus on the {features} that you have changed.".format(
                features=get_term("Feature", lower=True, plural=True),
            )
        )
