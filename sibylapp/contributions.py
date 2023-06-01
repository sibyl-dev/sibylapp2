import streamlit as st
from sibylapp.config import FLIP_COLORS
from sibylapp.helpers import process_options
from sibylapp import api, helpers, entities
from sibylapp.context import get_term
from st_aggrid import GridOptionsBuilder, AgGrid

if FLIP_COLORS:
    pos_em = "🟥"
    neg_em = "🟦"
else:
    pos_em = "🟦"
    neg_em = "🟥"


def show_table(df):
    df = df.drop("Contribution Value", axis="columns").rename(
            columns={
                "Contribution": get_term("Contribution"),
                "Feature": get_term("Feature"),
            }
        )
    builder = GridOptionsBuilder.from_dataframe(df)
    AgGrid(df, fit_columns_on_grid_load=True, gridOptions=builder.build())


@st.cache_data
def get_contributions(eids):
    return api.fetch_contributions(eids)


@st.cache_data
def format_contributions_for_details(eids):
    contributions = get_contributions(eids)
    for eid in contributions:
        contributions[eid] = contributions[eid].rename(
            columns={
                "category": "Category",
                "Feature Name": "Feature",
                "Feature Value": "Value",
                "Average/Mode": "Average/Mode Value"
            }
        )
        contributions[eid] = contributions[eid][
            ["Category", "Feature", "Value", "Average/Mode Value", "Contribution"]
        ]  # reorder
        contributions[eid]["Contribution Value"] = contributions[eid][
            "Contribution"
        ].copy()
        contributions[eid]["Contribution"] = helpers.generate_bars(
            contributions[eid]["Contribution"]
        )
    return contributions


def view(row):
    to_show = format_contributions_for_details(row)
    sort_by = st.selectbox(
        "Sort order", ["Absolute", "Ascending", "Descending", "Side-by-side"]
    )
    show_average = st.checkbox("Show average values?")
    if not show_average:
        to_show = to_show.drop("Average/Mode Value", axis="columns")

    if sort_by == "Side-by-side":
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(get_term("Negative"))
            to_show_neg = to_show[to_show["Contribution Value"] < 0].sort_values(
                by="Contribution", axis="index", ascending=False
            )
            to_show_neg = process_options(to_show_neg)
            show_table(to_show_neg)
        with col2:
            st.subheader(get_term("Positive"))
            to_show_pos = to_show[to_show["Contribution Value"] >= 0].sort_values(
                by="Contribution", axis="index", ascending=False
            )
            to_show_pos = process_options(to_show_pos)
            show_table(to_show_pos)
    else:
        if sort_by == "Absolute":
            to_show = to_show.reindex(
                to_show["Contribution Value"].abs().sort_values(ascending=False).index
            )
        if sort_by == "Ascending":
            to_show = to_show.sort_values(by="Contribution Value", axis="index")
        if sort_by == "Descending":
            to_show = to_show.sort_values(
                by="Contribution Value", axis="index", ascending=False
            )
        to_show = process_options(to_show)
        show_table(to_show)
