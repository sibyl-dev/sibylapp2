import numpy as np
import streamlit as st
from sibylapp.config import BAR_LENGTH
from sibylapp.helpers import process_options
from sibylapp import api, helpers
from sibylapp.context import get_term
from st_aggrid import AgGrid


def show_table(df):
    df = df.drop("Importance Value", axis="columns").rename(
            columns={
                "Importance": get_term("Importance"),
                "Feature": get_term("Feature"),
            }
        )
    AgGrid(df, fit_columns_on_grid_load=True)


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
    importance["Importance Value"] = importance["Importance"].copy()
    importance["Importance"] = helpers.generate_bars(
        importance["Importance"], neutral=True
    )

    return importance


def view(to_show):
    to_show = to_show.sort_values(by="Importance Value", axis="index", ascending=False)
    to_show = process_options(to_show)
    show_table(to_show)
