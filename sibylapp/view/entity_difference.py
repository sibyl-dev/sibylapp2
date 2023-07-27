import streamlit as st

from sibylapp.compute import contributions, model
from sibylapp.compute.context import get_term
from sibylapp.config import PREDICTION_TYPE, PredType, pred_format_func
from sibylapp.view.utils import filtering, helpers
from sibylapp.view.utils.helpers import NEG_EM, POS_EM


def view_prediction_difference():
    predictions = model.get_predictions(st.session_state["eids"])
    old_prediction = predictions[st.session_state["eid"]]
    new_prediction = predictions[st.session_state["eid_comp"]]
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
            eid=st.session_state["eid"],
            eid_comp=st.session_state["eid_comp"],
        ),
        output_text,
    )


def show_legend():
    modelPred = get_term("Prediction", l=True)
    separator = "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;"
    posChange = " Increase in %s's contribution to" % get_term("Feature", l=True)
    negChange = " Decrease in %s's contribution to" % get_term("Feature", l=True)

    st.write(
        (NEG_EM + negChange + " " + modelPred) + separator + (POS_EM + posChange + " " + modelPred)
    )


def show_sorted_contributions(to_show, sort_by):
    show_legend()
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
    helpers.show_table(to_show.drop("Contribution Change Value", axis="columns"))


def format_single_contributions_df(df, show_number=False):
    formatted_df = df.rename(
        columns={
            "category": "Category",
            "Feature Value": "%s Value" % get_term("Feature"),
        }
    )
    formatted_df = formatted_df[
        ["Category", "Feature", "%s Value" % get_term("Feature"), "Contribution"]
    ]
    formatted_df["Contribution Value"] = formatted_df["Contribution"].copy()
    formatted_df["Contribution"] = helpers.generate_bars(
        formatted_df["Contribution"], show_number=show_number
    )
    return formatted_df


def format_two_contributions_to_view(df1, df2, show_number=False, show_contribution=False):
    original_df = format_single_contributions_df(df1)
    other_df = format_single_contributions_df(df2)

    other_df = other_df.drop(["Category", "Feature"], axis="columns")
    compare_df = original_df.join(
        other_df,
        lsuffix=" for %s %s" % (get_term("Entity"), st.session_state["eid"]),
        rsuffix=" for %s %s" % (get_term("Entity"), st.session_state["eid_comp"]),
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
                "Contribution for %s %s" % (get_term("Entity"), st.session_state["eid"]),
                "Contribution for %s %s" % (get_term("Entity"), st.session_state["eid_comp"]),
                "Contribution Value for %s %s" % (get_term("Entity"), st.session_state["eid"]),
                "Contribution Value for %s %s"
                % (get_term("Entity"), st.session_state["eid_comp"]),
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
    show_number = False

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
            show_contriubtion = st.checkbox(
                "Show original contributions?",
                help="Show the original %s contributions for both %s"
                % (get_term("Feature"), get_term("Entity", p=True)),
            )
    else:
        cols = st.columns(1)
        with cols[0]:
            sort_by = helpers.show_sort_options(
                ["Absolute Difference", "Positive Difference", "Negative Difference"]
            )

    contributions_dict = contributions.get_contributions([eid, eid_comp])
    contribution_original = contributions_dict[eid]
    contribution_compare = contributions_dict[eid_comp]
    to_show = format_two_contributions_to_view(
        contribution_original,
        contribution_compare,
        show_number=show_number,
        show_contribution=show_contriubtion,
    )

    options = ["No filtering", "With filtering"]
    show_different = st.radio(
        "Apply filtering by identical %s values?" % get_term("Feature", l=True),
        options,
        horizontal=True,
        help="Show only rows where %s values of two %s are identical"
        % (get_term("Feature", l=True), get_term("Entity", l=True, p=True)),
    )
    if show_different == "With filtering":
        to_show = filter_different_rows(to_show)

    show_sorted_contributions(to_show, sort_by)


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "This page compares the **{feature} values** and **{feature} contributions**"
            " of two distinct {entities}."
            " You can select two {entities} you want to compare from the dropdown above.".format(
                entities=get_term("Entity", p=True, l=True),
                feature=get_term("Feature", l=True),
            )
        )
        positive, negative = helpers.get_pos_neg_names()
        st.markdown(
            "The **Contribution Change** column refers to the difference between the {feature}"
            " contribution of the two {entities}. A large **{positive}** bar means that this"
            " {feature}'s value has a much more positive contribution to the model's prediction on"
            " the second {entity} than on the first {entity}. A large **{negative}** bar means"
            " that this {feature}'s value has a much more negative contribution to the model's"
            " prediction on the second {entity} than on the first {entity}. A lack of a bar"
            " suggests this {feature} has a similar effect on the model's prediction for both"
            " cases.".format(
                positive=positive,
                negative=negative,
                feature=get_term("Feature", l=True),
                entity=get_term("Entity", l=True),
                entities=get_term("Entity", l=True, p=True),
            )
        )
        st.markdown(
            "You can **filter** and **search** the {feature} table or adjust"
            " the **sort order**. You can also look at {features} with identical"
            " {feature} values.".format(
                feature=get_term("Feature", l=True),
                features=get_term("Feature", p=True, l=True),
            )
        )
