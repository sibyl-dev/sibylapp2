import streamlit as st
from sibylapp.config import FLIP_COLORS
from sibylapp.helpers import process_options
from sibylapp import api, helpers, entities
from sibylapp.context import get_term
from st_aggrid import AgGrid

if FLIP_COLORS:
    pos_em = "🟥"
    neg_em = "🟦"
else:
    pos_em = "🟦"
    neg_em = "🟥"


@st.cache_data(show_spinner="Computing contribution scores...")
def compute_contributions(eids):
    contributions = api.fetch_contributions(eids)
    if "contributions" not in st.session_state:
        st.session_state["contributions"] = contributions
    else:
        st.session_state["contributions"] = dict(st.session_state["contributions"], **contributions)
    return contributions


def get_contributions(eids):
    if "contributions" not in st.session_state:
        compute_contributions(eids)
    else:
        missing_eids = list(set(eids) - st.session_state["contributions"].keys())
        if len(missing_eids) > 0:
            compute_contributions(missing_eids)
    return {eid: st.session_state["contributions"][eid] for eid in eids}


def show_table(df):
    df = df.drop("Contribution Value", axis="columns").rename(
        columns={
            "Contribution": get_term("Contribution"),
            "Feature": get_term("Feature"),
        }
    )
    AgGrid(df, fit_columns_on_grid_load=True)


@st.cache_data(show_spinner=False)
def format_contributions_for_details(contributions):
    contributions = contributions.rename(
        columns={
            "category": "Category",
            "Feature Name": "Feature",
            "Feature Value": "Value",
            "Average/Mode": "Average/Mode Value",
        }
    )
    contributions = contributions[
        ["Category", "Feature", "Value", "Average/Mode Value", "Contribution"]
    ]  # reorder
    contributions["Contribution Value"] = contributions[
        "Contribution"
    ].copy()
    contributions["Contribution"] = helpers.generate_bars(
        contributions["Contribution"]
    )
    return contributions


def view(eid):
    to_show = format_contributions_for_details(get_contributions(eid)[eid])
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
