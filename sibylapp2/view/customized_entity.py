from __future__ import annotations

import pandas as pd
import streamlit as st

from sibylapp2.compute import contributions, features, model
from sibylapp2.compute.context import get_term
from sibylapp2.config import pred_format_func
from sibylapp2.view.compare_entities import sort_contributions, view_compare_cases_helper
from sibylapp2.view.utils import helpers
from sibylapp2.view.utils.formatting import format_two_contributions_to_view
from sibylapp2.view.utils.helpers import show_text_input_side_by_side


def view_feature_boxes(
    eid: str,
    use_row_id=False,
    eid_for_rows=None,
):
    if "options_dict" not in st.session_state:
        st.session_state["categorical_values_dict"] = features.get_categorical_values()
    if "changes" not in st.session_state:
        st.session_state["changes"] = {}
    if use_row_id:
        entity = features.get_entity(eid_for_rows, eid)
    else:
        entity = features.get_entity(eid)
    changes = {}
    features_df = features.get_features(include_type=True)
    selected_features = st.multiselect(
        "Select %s to change:" % get_term("feature", plural=True),
        features_df.index.tolist(),
        default=list(st.session_state["changes"].keys()),
        format_func=lambda feat: features_df.loc[feat, "Feature"],
        key="selected_features",
        placeholder="Select one or multiple %s" % get_term("feature", plural=True),
    )
    for feature in selected_features:
        # Sibyl-api expects the raw feature names as input for changes
        default_input = entity[feature]
        if feature in st.session_state["changes"].keys():
            default_input = st.session_state["changes"][feature]

        numeric = True
        options = None
        if features_df.loc[feature, "Type"] != "numeric":
            numeric = False
            options = st.session_state["categorical_values_dict"][feature]

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
            prediction=get_term("prediction"),
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
    neighbor_col = to_show["Value for %s %s" % (get_term("Entity"), eid)]
    selected_col = to_show["Value for modified %s" % (get_term("Entity"))]
    to_show_filtered = to_show[neighbor_col != selected_col]
    return to_show_filtered


def view(eid, changes, model_id, row_id=None):
    """
    eid is used as `row_id` when use_row_id is True
    """
    sort_by, show_number, show_contribution = view_compare_cases_helper()
    if row_id is not None:
        original_contribution_df, original_values_df = contributions.get_contributions_for_rows(
            eid, [row_id], model_id=model_id
        )
        other_contribution_df, other_values_df = contributions.get_contribution_for_modified_data(
            eid, changes, row_id=row_id, model_id=model_id
        )
    else:
        original_contribution_df, original_values_df = contributions.get_contributions(
            [eid], model_id=model_id
        )
        other_contribution_df, other_values_df = contributions.get_contribution_for_modified_data(
            eid, changes, model_id=model_id
        )

    original_df = pd.DataFrame(
        {"Contribution": original_contribution_df.iloc[0], "Value": original_values_df.iloc[0]}
    )
    other_df = pd.DataFrame(
        {"Contribution": other_contribution_df.iloc[0], "Value": other_values_df.iloc[0]}
    )
    feature_df = features.get_features()
    to_show = format_two_contributions_to_view(
        original_df,
        other_df,
        feature_df,
        lsuffix=" for %s %s" % (get_term("Entity"), eid),
        rsuffix=" for modified %s" % get_term("Entity"),
        show_number=show_number,
        show_contribution=show_contribution,
    )
    options = ["No filtering", "With filtering"]
    show_different = st.radio(
        "Filter out identical %s values?" % get_term("feature"),
        options,
        horizontal=True,
        help="Show only rows where %s values of two %s are different"
        % (get_term("feature"), get_term("entity", plural=True)),
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
        key="experiment_with_changes",
    )


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "This page presents the change in **prediction** and **{feature} contribution**"
            " by the selected_features you added to the selected {entity}.".format(
                feature=get_term("feature"), entity=get_term("Entity")
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
                a_entity=get_term("entity", with_a=True),
                entity=get_term("entity"),
                feature=get_term("feature"),
                features=get_term("feature", plural=True),
            )
        )
        st.markdown(
            "The layout and formatting functions in the following table are very similar to that"
            " in the **Compare Cases** page. However, we provide a different filter here. You can"
            " focus on the {features} that you have changed.".format(
                features=get_term("feature", plural=True),
            )
        )
