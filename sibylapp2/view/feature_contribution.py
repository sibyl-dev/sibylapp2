import streamlit as st

from sibylapp2.compute import contributions, features
from sibylapp2.compute.context import get_term
from sibylapp2.view import filtering, helpers
from sibylapp2.view.helpers import show_legend


def show_sorted_contributions(to_show, sort_by, key):
    show_legend()

    if sort_by == "Side-by-side":
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(get_term("Negative"))
            to_show_neg = to_show[to_show["Contribution Value"] < 0].sort_values(
                by="Contribution", axis="index", ascending=False
            )
            to_show_neg = filtering.process_options(to_show_neg)
            helpers.show_table(
                to_show_neg.drop("Contribution Value", axis="columns"), key="%s%s" % (key, "_neg")
            )
        with col2:
            st.subheader(get_term("Positive"))
            to_show_pos = to_show[to_show["Contribution Value"] >= 0].sort_values(
                by="Contribution", axis="index", ascending=False
            )
            to_show_pos = filtering.process_options(to_show_pos)
            helpers.show_table(
                to_show_pos.drop("Contribution Value", axis="columns"), key="%s%s" % (key, "_pos")
            )
    else:
        if sort_by == "Absolute":
            to_show = to_show.reindex(
                to_show["Contribution Value"].abs().sort_values(ascending=False).index
            )
        if sort_by == get_term("Positive"):
            to_show = to_show.sort_values(by="Contribution Value", axis="index", ascending=False)
            to_show = to_show[to_show["Contribution Value"] > 0]
        if sort_by == get_term("Negative"):
            to_show = to_show.sort_values(by="Contribution Value", axis="index")
            to_show = to_show[to_show["Contribution Value"] < 0]
        to_show = filtering.process_options(to_show)
        helpers.show_table(to_show.drop("Contribution Value", axis="columns"), key=key)


def format_contributions_to_view(eid, model_id, row_id=None, show_number=False):
    if row_id is not None:
        contribution_df, value_df = contributions.get_contributions_for_rows(
            eid, [row_id], model_id=model_id
        )
    else:
        contribution_df, value_df = contributions.get_contributions([eid], model_id=model_id)
    full_df = features.get_features()
    full_df["Value"] = value_df.T
    full_df["Contribution"] = contribution_df.T
    full_df = full_df.rename(columns={"category": "Category"})

    full_df = full_df[["Category", "Feature", "Value", "Contribution"]]  # reorder
    full_df["Contribution Value"] = full_df["Contribution"].copy()
    full_df["Contribution"] = helpers.generate_bars(
        full_df["Contribution"], show_number=show_number
    )
    return full_df


def view(eid, model_id, key, row_id=None, save_space=False):
    """
    `eid_for_rows` is only used when `use_row_id` == True.
    `eid` are used as row_id when `use_row_id` == True
    """
    show_number = False
    if not save_space:
        cols = st.columns(2)
        with cols[0]:
            sort_by = helpers.show_sort_options(
                ["Absolute", get_term("Positive"), get_term("Negative"), "Side-by-side"]
            )
        with cols[1]:
            show_number = st.checkbox(
                "Show numeric contributions?",
                help="Show the exact amount this feature contributes to the model prediction",
            )
    else:
        sort_by = helpers.show_sort_options(
            ["Absolute", get_term("Positive"), get_term("Negative")]
        )

    to_show = format_contributions_to_view(eid, model_id, row_id=row_id, show_number=show_number)

    show_sorted_contributions(to_show, sort_by, key=key)
