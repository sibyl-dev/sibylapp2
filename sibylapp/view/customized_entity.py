import pandas as pd
import streamlit as st

from sibylapp.compute import contributions, model
from sibylapp.compute.context import get_term
from sibylapp.compute.features import get_entity
from sibylapp.config import pred_format_func
from sibylapp.view.entity_difference import sort_contributions, view_compare_cases_helper
from sibylapp.view.utils import helpers
from sibylapp.view.utils.formatting import format_single_contributions_df
from sibylapp.view.utils.helpers import show_text_input_side_by_side


def view_feature_boxes(eid, features_df):
    if "selected_features" not in st.session_state:
        st.session_state["selected_features"] = []
    if "changes" not in st.session_state:
        st.session_state["changes"] = {}

    feature_names = features_df["Feature"]
    entity = get_entity(eid)

    st.multiselect(
        "Select %s to change:" % get_term("Feature", lower=True, plural=True),
        feature_names,
        key="selected_features",
        default=st.session_state["selected_features"],
        placeholder="Select one or multiple %s" % get_term("Feature", lower=True, plural=True),
    )

    for feature in st.session_state["selected_features"]:
        # Sibyl-api expects the raw feature names as input for changes
        st.session_state["changes"][features_df.index[feature_names == feature][0]] = (
            show_text_input_side_by_side(
                f"New value for **{feature.strip()}**",
                default_input=entity[features_df.index[feature_names == feature][0]],
                numeric=(features_df[feature_names == feature]["type"][0] == "numeric"),
            )
        )


def view_prediction(eid, changes):
    prediction = model.get_modified_prediction(eid, changes)
    st.metric(
        "Model's {prediction} of modified {entity}:".format(
            prediction=get_term("Prediction", lower=True),
            entity=get_term("Entity"),
        ),
        pred_format_func(prediction),
    )


def format_compare_modified_contributions_to_view(
    eid, changes, show_number=False, show_contribution=False
):
    contribution_original = contributions.get_contributions([eid])[eid]
    contribution_custom = contributions.get_contribution_for_modified_data(eid, changes)
    original_df = format_single_contributions_df(contribution_original)
    other_df = format_single_contributions_df(contribution_custom)

    other_df = other_df.drop(["Category", "Feature"], axis="columns")
    compare_df = original_df.join(
        other_df,
        lsuffix=" for %s %s" % (get_term("Entity"), eid),
        rsuffix=" for modified %s" % get_term("Entity"),
    )
    compare_df["Contribution Change"] = (
        other_df["Contribution Value"] - original_df["Contribution Value"]
    )
    compare_df["Contribution Change Value"] = compare_df["Contribution Change"].copy()
    compare_df["Contribution Change"] = helpers.generate_bars(
        compare_df["Contribution Change"], show_number=show_number
    )

    if not show_contribution:
        compare_df = compare_df.drop(
            [
                "Contribution for %s %s" % (get_term("Entity"), eid),
                "Contribution for modified %s" % get_term("Entity"),
                "Contribution Value for %s %s" % (get_term("Entity"), eid),
                "Contribution Value for modified %s" % get_term("Entity"),
            ],
            axis="columns",
        )
    return compare_df


def highlight_differences(to_show, changes, columns=[]):
    def match_condition(feature, column, props=""):
        if feature in changes.keys() and column in columns:
            return props
        else:
            return None

    to_show = to_show.style.apply(
        lambda x: pd.DataFrame(x).style.apply(
            lambda y: match_condition(x.name, y.name), props="color:purple;", axis=1
        )
    )

    return to_show


def filter_different_rows(eid, to_show):
    neighbor_col = to_show["%s Value for %s %s" % (get_term("Feature"), get_term("Entity"), eid)]
    selected_col = to_show["%s Value for modified %s" % (get_term("Feature"), get_term("Entity"))]
    to_show_filtered = to_show[neighbor_col != selected_col]
    return to_show_filtered


def view(eid, changes, save_space=False):
    sort_by, show_number, show_contribution = view_compare_cases_helper(save_space=save_space)
    to_show = format_compare_modified_contributions_to_view(
        eid,
        changes,
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

    helpers.show_table(to_show)


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "This page presents the change in **prediction** and **{feature} contribution**"
            " by the selected_features you added to the selected {entity}.".format(
                feature=get_term("Feature", lower=True), entity=get_term("Entity")
            )
        )
        positive, negative = helpers.get_pos_neg_names()
        st.markdown(
            "A large **{positive}** bar means that this {feature}'s value significantly increased"
            " the model's prediction on this {entity}. A large **{negative}** bar means that this"
            " {feature}'s value significantly decreased the model's prediction. A lack of a"
            " bar suggests this {feature} had little effect on the model's prediction in this"
            " case.".format(
                positive=positive,
                negative=negative,
                feature=get_term("Feature", lower=True),
                entity=get_term("Entity", lower=True),
            )
        )
        st.markdown(
            "You can select {a_entity} from the dropdown above, and see the {feature}"
            " contributions. You can also **filter** and **search** the {feature} table or adjust"
            " the **sort order**.".format(
                a_entity=get_term("Entity", with_a=True, lower=True),
                feature=get_term("Feature", lower=True),
            )
        )
