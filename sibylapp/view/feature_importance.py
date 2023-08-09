import streamlit as st

from sibylapp.compute import importance, model
from sibylapp.compute.context import get_term
from sibylapp.view.utils import helpers, filtering
from sibylapp.view import explore_feature


@st.cache_data
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
    to_show = filtering.process_options(to_show)
    to_show = filtering.add_select(to_show)
    edited_df = helpers.show_table(to_show.drop("Importance Value", axis="columns"), key="importance", editable = ["View Graph"])
    graph_placeholder = st.container()


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "**{feature_up} Importance** refers to how much the model uses a specific"
            " {feature} overall in its predictions. A large importance bar means this {feature} is"
            " used frequently, while a smaller bar means it is used less.".format(
                feature_up=get_term("Feature"), feature=get_term("Feature", lower=True)
            )
        )
        st.markdown(
            "You can also **filter** and **search** the {feature} table or adjust the **sort"
            " order**.".format(feature=get_term("Feature", lower=True))
        )
