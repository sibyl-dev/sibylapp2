import numpy as np
import streamlit as st
from sibylapp.config import BAR_LENGTH
from sibylapp.helpers import process_search, process_show_more


@st.cache_data
def compute_importance(_app):
    importance = _app.produce_feature_importance()
    importance.set_index("Feature Name", inplace=True)
    importance["Importance Value"] = importance["Importance"]
    num_to_show = (
        importance["Importance Value"]
        / max(importance["Importance Value"].abs())
        * BAR_LENGTH
    )
    num_to_show = num_to_show.apply(np.ceil).astype("int")
    importance["Importance"] = [
        ("🟪" * n + "⬜" * (BAR_LENGTH - n) + "⬆") for n in num_to_show
    ]

    return importance


def view(to_show, search):
    to_show = to_show.sort_values(by="Importance Value", axis="index", ascending=False)
    to_show = process_search(
        process_show_more(to_show, st.session_state["show_more"]), search
    )
    st.table(to_show.drop("Importance Value", axis="columns"))
