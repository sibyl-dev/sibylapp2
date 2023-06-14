import streamlit as st
from sibylapp.view.utils import helpers
from sibylapp.compute import contributions
from sibylapp.compute.context import get_term
from sibylapp.config import FLIP_COLORS
from st_aggrid import AgGrid


def show_table(df):
    df = df.drop("Contribution Value", axis="columns").rename(
        columns={
            "Contribution": get_term("Contribution"),
            "Feature": get_term("Feature"),
        }
    )
    AgGrid(df, fit_columns_on_grid_load=True)


@st.cache_data(show_spinner=False)
def format_contributions_to_view(contribution_df):
    contribution_df = contribution_df.rename(
        columns={
            "category": "Category",
            "Feature Name": "Feature",
            "Feature Value": "Value",
            "Average/Mode": "Average/Mode Value",
        }
    )
    contribution_df = contribution_df[
        ["Category", "Feature", "Value", "Average/Mode Value", "Contribution"]
    ]  # reorder
    contribution_df["Contribution Value"] = contribution_df["Contribution"].copy()
    contribution_df["Contribution"] = helpers.generate_bars(
        contribution_df["Contribution"]
    )
    return contribution_df


def view(eid):
    to_show = format_contributions_to_view(contributions.get_contributions(eid)[eid])
    sort_by = st.selectbox(
        "Sort order", ["Absolute", "Ascending", "Descending", "Side-by-side"]
    )
    show_average = st.checkbox("Show average values?")
    if not show_average:
        to_show = to_show.drop("Average/Mode Value", axis="columns")

    helpers.show_sorted_contributions(to_show, sort_by, show_table)


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "*Feature Contributions* refer to the positive or negative affect a specific feature value had on the "
            "model's prediction."
        )
        st.markdown(
            "You can select a %s from the dropdown above, and see which features contributed most to "
            "the model's prediction in the table to the right. You can also **filter** and **search** "
            "the features shown in table or adjust the **sort order**."
            % (get_term("Entity").lower())
        )
        if FLIP_COLORS:
            positive, negative = "red", "blue"
        else:
            positive, negative = "blue", "red"
        st.markdown(
            "A large **%s** bar means that this %s's value significantly increased the model's prediction"
            "on this %s. A large **%s** bar means that this %s's value significantly decreased the model's prediction. "
            "A lack of a bar suggests this %s had little effect on the model's prediction in this case."
            % (
                positive,
                get_term("Feature").lower(),
                get_term("Entity").lower(),
                negative,
                get_term("Feature").lower(),
                get_term("Feature").lower(),
            )
        )
