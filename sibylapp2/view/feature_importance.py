import streamlit as st

import sibylapp2.view.utils.filtering
from sibylapp2.compute import importance
from sibylapp2.compute.context import get_term
from sibylapp2.view.utils import helpers


def format_importance_to_view(importance_df):
    importance_df = importance_df.rename(
        columns={
            "importances": "Importance",
            "category": "Category",
        }
    )
    importance_df = importance_df[["Category", "Feature", "Importance"]]  # reorder
    importance_df["Importance Value"] = importance_df["Importance"].copy()
    importance_df["Importance"] = helpers.generate_bars(importance_df["Importance"], neutral=True)

    return importance_df


def view():
    to_show = format_importance_to_view(importance.compute_importance())
    to_show = to_show.sort_values(by="Importance Value", axis="index", ascending=False)
    to_show = sibylapp2.view.utils.filtering.process_options(to_show)
    helpers.show_table(to_show.drop("Importance Value", axis="columns"), key="importance")
    return to_show["Feature"]


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "**{feature_up} Importance** refers to how much the model uses a specific"
            " {feature} overall in its predictions. A large importance bar means this {feature} is"
            " used frequently, while a smaller bar means it is used less.".format(
                feature_up=get_term("Feature"), feature=get_term("feature")
            )
        )
        st.markdown(
            "You can also **filter** and **search** the {feature} table or adjust the **sort"
            " order**.".format(feature=get_term("feature"))
        )
