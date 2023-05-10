import numpy as np
import streamlit as st
from sibylapp.config import BAR_LENGTH
from sibylapp.helpers import process_search, process_show_more
from sibylapp import api


def show_table(df):
    st.table(df.drop("Contribution Value", axis="columns").set_index("Category", verify_integrity=False))


@st.cache_data
def compute_contributions(eids):
    contributions = api.fetch_contributions(eids)
    for eid in contributions:
        contributions[eid] = contributions[eid].rename(columns={"contributions": "Contribution", "category": "Category", "description": "Feature"})
        contributions[eid] = contributions[eid][["Category", "Feature", "Contribution"]]#contributions[eid].drop(["type", "negated_description"], axis="columns")
        contributions[eid]["Contribution Value"] = contributions[eid]["Contribution"]
        num_to_show = (
            contributions[eid]["Contribution"]
            / max(contributions[eid]["Contribution"].abs())
            * BAR_LENGTH
        )
        num_to_show = num_to_show.apply(np.ceil).astype("int")
        contributions[eid]["Contribution"] = [
            ("🟦" * n + "⬜" * (BAR_LENGTH - n) + "⬆")
            if n > 0
            else ("⬇" + "⬜" * (BAR_LENGTH + n) + "🟥" * -n)
            for n in num_to_show
        ]

    return contributions


def view(to_show, search):
    sort_by = st.selectbox(
        "Sort order", ["Absolute", "Ascending", "Descending", "Side-by-side"]
    )

    if sort_by == "Side-by-side":
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Negative features")
            to_show_neg = to_show[to_show["Contribution Value"] < 0].sort_values(
                by="Contribution", axis="index", ascending=False
            )
            to_show_neg = process_search(
                process_show_more(to_show_neg, st.session_state["show_more"]), search
            )
            show_table(to_show_neg)
        with col2:
            st.subheader("Positive features")
            to_show_pos = to_show[to_show["Contribution Value"] >= 0].sort_values(
                by="Contribution", axis="index", ascending=False
            )
            to_show_pos = process_search(
                process_show_more(to_show_pos, st.session_state["show_more"]), search
            )
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
        to_show = process_search(
            process_show_more(to_show, st.session_state["show_more"]), search
        )
        show_table(to_show)
