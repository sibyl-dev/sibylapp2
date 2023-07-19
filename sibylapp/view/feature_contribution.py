import streamlit as st

from sibylapp.compute import contributions
from sibylapp.compute.context import get_term
from sibylapp.config import NEGATIVE_TERM, POSITIVE_TERM, PREDICTION_TYPE, PredType
from sibylapp.view.utils import filtering, helpers
from sibylapp.view.utils.helpers import NEG_EM, POS_EM


def show_legend():
    modelPred = get_term("Prediction", l=True)
    posChange = ""
    negChange = ""
    separator = "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;"
    # *will add detail for categorical predictions after we figure this out
    if PREDICTION_TYPE == PredType.NUMERIC:
        posChange = " Increase in"
        negChange = " Decrease in"
    elif PREDICTION_TYPE == PredType.BOOLEAN:
        posChange = f" towards **{POSITIVE_TERM}** as"
        negChange = f" towards **{NEGATIVE_TERM}** as"
    st.write(
        (NEG_EM + negChange + " " + modelPred) + separator + (POS_EM + posChange + " " + modelPred)
    )


def show_sorted_contributions(to_show, sort_by):
    show_legend()

    if sort_by == "Side-by-side":
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(get_term("Negative"))
            to_show_neg = to_show[to_show["Contribution Value"] < 0].sort_values(
                by="Contribution", axis="index", ascending=False
            )
            to_show_neg = filtering.process_options(to_show_neg)
            helpers.show_table(to_show_neg.drop("Contribution Value", axis="columns"), key="neg")
        with col2:
            st.subheader(get_term("Positive"))
            to_show_pos = to_show[to_show["Contribution Value"] >= 0].sort_values(
                by="Contribution", axis="index", ascending=False
            )
            to_show_pos = filtering.process_options(to_show_pos)
            helpers.show_table(to_show_pos.drop("Contribution Value", axis="columns"), key="pos")
    else:
        if sort_by == "Absolute":
            to_show = to_show.reindex(
                to_show["Contribution Value"].abs().sort_values(ascending=False).index
            )
        if sort_by == "Ascending":
            to_show = to_show.sort_values(by="Contribution Value", axis="index")
        if sort_by == "Descending":
            to_show = to_show.sort_values(by="Contribution Value", axis="index", ascending=False)
        to_show = filtering.process_options(to_show)
        helpers.show_table(to_show.drop("Contribution Value", axis="columns"))


def format_contributions_to_view(contribution_df, show_number=False):
    contribution_df = contribution_df.rename(
        columns={
            "category": "Category",
            "Feature Value": "Value",
            "Average/Mode": "Average/Mode Value",
        }
    )
    contribution_df = contribution_df[
        ["Category", "Feature", "Value", "Average/Mode Value", "Contribution"]
    ]  # reorder
    contribution_df["Contribution Value"] = contribution_df["Contribution"].copy()
    contribution_df["Contribution"] = helpers.generate_bars(
        contribution_df["Contribution"], show_number=show_number
    )
    return contribution_df


def view(eid, save_space=False):
    show_number = False
    show_average = False
    if not save_space:
        cols = st.columns(2)
        with cols[0]:
            sort_by = helpers.show_sort_options(
                ["Absolute", "Ascending", "Descending", "Side-by-side"]
            )
        with cols[1]:
            show_average = st.checkbox(
                "Show average values?",
                help=(
                    "Contributions are based on the difference from the average value in the"
                    " training set"
                ),
            )
            show_number = st.checkbox(
                "Show numeric contributions?",
                help="Show the exact amount this feature contributes to the model prediction",
            )
    else:
        cols = st.columns(1)
        with cols[0]:
            sort_by = helpers.show_sort_options(["Absolute", "Ascending", "Descending"])
    to_show = format_contributions_to_view(
        contributions.get_contributions([eid])[eid], show_number=show_number
    )
    if not show_average:
        to_show = to_show.drop("Average/Mode Value", axis="columns")

    show_sorted_contributions(to_show, sort_by)


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "**{feature_contributions}** refer to the positive or negative affect a specific"
            " feature value had on the model's prediction.".format(
                feature_contributions=get_term("Feature Contributions")
            )
        )
        positive, negative = helpers.get_pos_neg_names()
        st.markdown(
            "A large **{positive}** bar means that this {feature}'s value significantly increased"
            " the model's prediction on this {entity}. A large **{negative}** bar means that this"
            " {feature}'s value significantly decreased the model's prediction. A lack of a bar"
            " suggests this {feature} had little effect on the model's prediction in this case."
            .format(
                positive=positive,
                negative=negative,
                feature=get_term("Feature").lower(),
                entity=get_term("Entity").lower(),
            )
        )
        st.markdown(
            "You can select {a_entity} from the dropdown above, and see the {feature}"
            " contributions. You can also **filter** and **search** the {feature} table or adjust"
            " the **sort order**.".format(
                a_entity=get_term("Entity", a=True, l=True),
                feature=get_term("Feature", l=True),
            )
        )
