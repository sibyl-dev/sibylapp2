import streamlit as st

from sibylapp.compute import contributions, model
from sibylapp.compute.context import get_term
from sibylapp.config import POSITIVE_TERM, PREDICTION_TYPE, PredType, pred_format_func
from sibylapp.view.utils import filtering, helpers
from sibylapp.view.utils.formatting import format_two_contributions_to_view


def view_prediction_difference(eid, eid_comp, use_row_ids=False, row_ids=None, eid_for_rows=None):
    """
    If use_row_ids is set to True, this function looks at the difference between two rows
    within a single entity.

    `row_ids` and `eid_for_rows` are only used when `use_row_ids` == True.
    `eid` and `eid_comp` are used as row_id when `use_row_ids` == True
    """
    if use_row_ids:
        predictions = model.get_predictions_for_rows(eid_for_rows, row_ids)
    else:
        predictions = model.get_predictions(st.session_state["eids"])
    old_prediction = predictions[eid]
    new_prediction = predictions[eid_comp]
    if PREDICTION_TYPE == PredType.NUMERIC:
        difference = new_prediction - old_prediction
        output_text = pred_format_func(difference)
        if difference > 0:
            output_text = "+" + output_text

    elif st.session_state["display_proba"]:
        if use_row_ids:
            predictions_proba = model.get_predictions_for_rows(
                eid_for_rows, row_ids, return_proba=True
            )
        else:
            predictions_proba = model.get_predictions(st.session_state["eids"], return_proba=True)
        old_prediction_proba = predictions_proba[eid]
        new_prediction_proba = predictions_proba[eid_comp]
        # Invert the probabilities if prediction is False
        if not old_prediction:
            old_prediction_proba = 1 - old_prediction_proba
        if not new_prediction:
            new_prediction_proba = 1 - new_prediction_proba
        difference = new_prediction_proba - old_prediction_proba
        output_text = pred_format_func(difference, display_proba=True) + " " + POSITIVE_TERM
        if difference > 0:
            output_text = "+" + output_text

    else:
        if pred_format_func(new_prediction) == pred_format_func(old_prediction):
            output_text = "No Change"
        else:
            output_text = (
                f"From {pred_format_func(old_prediction)} to {pred_format_func(new_prediction)}"
            )
    if use_row_ids:
        st.metric(
            f"{get_term('Prediction')} Change from {eid} to {eid_comp}:",
            output_text,
        )
    else:
        st.metric(
            (
                f"{get_term('Prediction')} Change from {get_term('Entity')} {eid} to"
                f" {get_term('Entity')} {eid_comp}:"
            ),
            output_text,
        )


def view_compare_cases_helper(save_space=False):
    show_number = False
    show_contribution = False
    if not save_space:
        cols = st.columns(2)
        with cols[0]:
            sort_by = helpers.show_sort_options(
                ["Absolute Difference", "Positive Difference", "Negative Difference"]
            )
        with cols[1]:
            show_number = st.checkbox(
                "Show numeric contributions?",
                help="Show the exact amount this feature contributes to the model prediction",
            )
            show_contribution = st.checkbox(
                "Show original contributions?",
                help="Show the original %s contributions for both %s"
                % (get_term("Feature"), get_term("Entity", plural=True)),
            )
    else:
        cols = st.columns(1)
        with cols[0]:
            sort_by = helpers.show_sort_options(
                ["Absolute Difference", "Positive Difference", "Negative Difference"]
            )
    return sort_by, show_number, show_contribution


def sort_contributions(to_show, sort_by):
    helpers.show_legend(similar_entities=True)
    if sort_by == "Absolute Difference":
        to_show = to_show.reindex(
            to_show["Contribution Change Value"].abs().sort_values(ascending=False).index
        )
    if sort_by == "Positive Difference":
        to_show = to_show.sort_values(
            by="Contribution Change Value", axis="index", ascending=False
        )
    if sort_by == "Negative Difference":
        to_show = to_show.sort_values(by="Contribution Change Value", axis="index")

    to_show = filtering.process_options(to_show)
    return to_show


def filter_different_rows(to_show, use_row_ids=False):
    if use_row_ids:
        neighbor_col = to_show[
            "%s Value for time %s" % (get_term("Feature"), st.session_state["row_id"])
        ]
        selected_col = to_show[
            "%s Value for time %s" % (get_term("Feature"), st.session_state["row_id_comp"])
        ]
    else:
        neighbor_col = to_show[
            "%s Value for %s %s"
            % (get_term("Feature"), get_term("Entity"), st.session_state["eid"])
        ]
        selected_col = to_show[
            "%s Value for %s %s"
            % (get_term("Feature"), get_term("Entity"), st.session_state["eid_comp"])
        ]
    to_show_filtered = to_show[neighbor_col == selected_col]
    return to_show_filtered


def view(eid, eid_comp, save_space=False, use_row_ids=False, row_ids=None, eid_for_rows=None):
    """
    `row_ids` and `eid_for_rows` are only used when `use_row_ids` == True.
    `eid` and `eid_comp` are used as row_id when `use_row_ids` == True
    """
    sort_by, show_number, show_contribution = view_compare_cases_helper(save_space=save_space)
    if use_row_ids:
        lsuffix = " for time %s" % eid
        rsuffix = " for time %s" % eid_comp
        contributions_dict = contributions.get_contributions_for_rows(eid_for_rows, row_ids)
    else:
        lsuffix = " for %s %s" % (get_term("Entity"), eid)
        rsuffix = " for %s %s" % (get_term("Entity"), eid_comp)
        contributions_dict = contributions.get_contributions([eid, eid_comp])
    original_df = contributions_dict[eid]
    other_df = contributions_dict[eid_comp]

    to_show = format_two_contributions_to_view(
        original_df,
        other_df,
        lsuffix=lsuffix,
        rsuffix=rsuffix,
        show_number=show_number,
        show_contribution=show_contribution,
    )

    options = ["No filtering", "With filtering"]
    show_different = st.radio(
        "Apply filtering by identical %s values?" % get_term("Feature", lower=True),
        options,
        horizontal=True,
        help="Show only rows where %s values of two %s are identical"
        % (get_term("Feature", lower=True), get_term("Entity", lower=True, plural=True)),
    )
    if show_different == "With filtering":
        to_show = filter_different_rows(to_show, use_row_ids=use_row_ids)

    to_show = sort_contributions(to_show, sort_by)
    helpers.show_table(to_show.drop("Contribution Change Value", axis="columns"))


def view_instructions(use_row_ids=False):
    expander = st.sidebar.expander("How to Use")
    with expander:
        if use_row_ids:
            st.markdown(
                "This page compares the **{feature} values** and **{feature} contributions**"
                " of the selected {entity} at the two selected times."
                " You can select the {entity} and the two time points from the dropdown above."
                .format(
                    entity=get_term("Entity", lower=True),
                    feature=get_term("Feature", lower=True),
                )
            )
        else:
            st.markdown(
                "This page compares the **{feature} values** and **{feature} contributions**"
                " of two distinct {entities}."
                " You can select two {entities} you want to compare from the dropdown above."
                .format(
                    entities=get_term("Entity", plural=True, lower=True),
                    feature=get_term("Feature", lower=True),
                )
            )
        positive, negative = helpers.get_pos_neg_names()
        if use_row_ids:
            entity = "prediction time"
            entities = "prediction times"
        else:
            entity = get_term("Entity", lower=True)
            entities = get_term("Entity", lower=True, plural=True)
        st.markdown(
            "The **Contribution Change** column refers to the difference between the {feature}"
            " contribution of the two {entities}. A large **{positive}** bar means that this"
            " {feature}'s value has a much more positive contribution to the model's"
            " prediction on the second {entity} than on the first {entity}. A large **{negative}**"
            " bar means that this {feature}'s value has a much more negative contribution to"
            " the model's prediction on the second {entity} than on the first {entity}. A lack of"
            " a bar suggests this {feature} has a similar effect on the model's"
            " prediction for both cases.".format(
                positive=positive,
                negative=negative,
                feature=get_term("Feature", lower=True),
                entity=entity,
                entities=entities,
            )
        )
        st.markdown(
            "You can **filter** and **search** the {feature} table or adjust"
            " the **sort order**. You can also look at {features} with identical"
            " {feature} values.".format(
                feature=get_term("Feature", lower=True),
                features=get_term("Feature", plural=True, lower=True),
            )
        )
