import numpy as np
import streamlit as st
from sibylapp.config import BAR_LENGTH
from sibylapp.helpers import process_options
from sibylapp import api
from sibylapp.context import get_term


def show_table(df):
    st.table(
        df.drop("Importance Value", axis="columns").set_index(
            "Category", verify_integrity=False
        ).rename(columns={"Importance": get_term("Importance"), "Feature": get_term("Feature")})
    )


@st.cache_data
def compute_importance():
    importance = api.fetch_importance()
    importance = importance.rename(
        columns={
            "importances": "Importance",
            "category": "Category",
            "description": "Feature",
        }
    )
    importance = importance[["Category", "Feature", "Importance"]]  # reorder
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


def view(to_show):
    to_show = to_show.sort_values(by="Importance Value", axis="index", ascending=False)
    to_show = process_options(to_show)
    show_table(to_show)
