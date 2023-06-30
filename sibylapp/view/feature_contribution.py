import streamlit as st
from sibylapp.view.utils import helpers
from sibylapp.compute import contributions
from sibylapp.compute.context import get_term
from sibylapp.config import FLIP_COLORS
from st_aggrid import AgGrid, ColumnsAutoSizeMode
from st_aggrid.grid_options_builder import GridOptionsBuilder


def show_table(df):
    df = df.drop("Contribution Value", axis="columns").rename(
        columns={
            "Contribution": get_term("Contribution"),
            "Feature": get_term("Feature"),
        }
    ).reset_index()
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=10)
    AgGrid(df, fit_columns_on_grid_load=True, gridOptions=gb.build(), columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)


@st.cache_data(show_spinner=False)
def format_contributions_to_view(contribution_df):
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
        contribution_df["Contribution"]
    )
    return contribution_df


def view(eid):
    to_show = format_contributions_to_view(contributions.get_contributions([eid])[eid])
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
            "**{feature_contributions}** refer to the positive or negative affect a specific feature value had on the "
            "model's prediction.".format(
                feature_contributions=get_term("Feature Contributions")
            )
        )
        if FLIP_COLORS:
            positive, negative = "red", "blue"
        else:
            positive, negative = "blue", "red"
        st.markdown(
            "A large **{positive}** bar means that this {feature}'s value significantly increased the model's "
            "prediction on this {entity}. A large **{negative}** bar means that this {feature}'s value significantly "
            "decreased the model's prediction. "
            "A lack of a bar suggests this {feature} had little effect on the model's prediction in this case.".format(
                positive=positive,
                negative=negative,
                feature=get_term("Feature").lower(),
                entity=get_term("Entity").lower(),
            )
        )
        st.markdown(
            "You can select {a_entity} from the dropdown above, and see the {feature} contributions. "
            "You can also **filter** and **search** the {feature} table or adjust the **sort order**.".format(
                a_entity=get_term("Entity", a=True, l=True),
                feature=get_term("Feature", l=True),
            )
        )
