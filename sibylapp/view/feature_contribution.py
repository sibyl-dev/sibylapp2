import streamlit as st
from sibylapp.view.utils.helpers import process_options
from sibylapp.view.utils import helpers
from sibylapp.compute import contributions
from sibylapp.compute.context import get_term
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
