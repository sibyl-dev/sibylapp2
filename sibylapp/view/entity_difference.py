import streamlit as st

from sibylapp.compute import contributions, model
from sibylapp.compute.context import get_term
from sibylapp.config import PREDICTION_TYPE, PredType, pred_format_func
from sibylapp.view.utils import filtering, helpers
from sibylapp.view.utils.formatting import format_single_contributions_df


def view_prediction_difference(eid, eid_comp):
    predictions = model.get_predictions(st.session_state["eids"])
    old_prediction = predictions[eid]
    new_prediction = predictions[eid_comp]
    if PREDICTION_TYPE == PredType.NUMERIC:
        difference = new_prediction - old_prediction
        output_text = pred_format_func(difference)

    else:
        if pred_format_func(new_prediction) == pred_format_func(old_prediction):
            output_text = "No Change"
        else:
            output_text = (
                f"From {pred_format_func(old_prediction)} to {pred_format_func(new_prediction)}"
            )

    st.metric(
        "{prediction} Change from {entity} {eid} to {entity} {eid_comp}:".format(
            prediction=get_term("Prediction"),
            entity=get_term("Entity"),
            eid=eid,
            eid_comp=eid_comp,
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


def format_two_contributions_to_view(
    contributions, eid1, eid2, show_number=False, show_contribution=False
):
    original_df = format_single_contributions_df(contributions[eid1])
    other_df = format_single_contributions_df(contributions[eid2])

    other_df = other_df.drop(["Category", "Feature"], axis="columns")
    compare_df = original_df.join(
        other_df,
        lsuffix=" for %s %s" % (get_term("Entity"), eid1),
        rsuffix=" for %s %s" % (get_term("Entity"), eid2),
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
                "Contribution for %s %s" % (get_term("Entity"), eid1),
                "Contribution for %s %s" % (get_term("Entity"), eid2),
                "Contribution Value for %s %s" % (get_term("Entity"), eid1),
                "Contribution Value for %s %s" % (get_term("Entity"), eid2),
            ],
            axis="columns",
        )
    return compare_df


def filter_different_rows(to_show):
    neighbor_col = to_show[
        "%s Value for %s %s" % (get_term("Feature"), get_term("Entity"), st.session_state["eid"])
    ]
    selected_col = to_show[
        "%s Value for %s %s"
        % (get_term("Feature"), get_term("Entity"), st.session_state["eid_comp"])
    ]
    to_show_filtered = to_show[neighbor_col == selected_col]
    return to_show_filtered


def view(eid, eid_comp, save_space=False):
    sort_by, show_number, show_contribution = view_compare_cases_helper(save_space=save_space)
    contributions_dict = contributions.get_contributions([eid, eid_comp])
    to_show = format_two_contributions_to_view(
        contributions_dict,
        eid,
        eid_comp,
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
        to_show = filter_different_rows(to_show)

    to_show = sort_contributions(to_show, sort_by)
    helpers.show_table(to_show.drop("Contribution Change Value", axis="columns"))


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "This page compares the **{feature} values** and **{feature} contributions**"
            " of two distinct {entities}."
            " You can select two {entities} you want to compare from the dropdown above.".format(
                entities=get_term("Entity", plural=True, lower=True),
                feature=get_term("Feature", lower=True),
            )
        )
        positive, negative = helpers.get_pos_neg_names()
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
                entity=get_term("Entity", lower=True),
                entities=get_term("Entity", lower=True, plural=True),
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
