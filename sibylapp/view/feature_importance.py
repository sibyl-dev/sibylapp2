import streamlit as st

import sibylapp.view.utils.filtering
from sibylapp.compute import importance
from sibylapp.view.utils import helpers
from sibylapp.compute.context import get_term
from st_aggrid import AgGrid


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
    importance_df["Importance"] = helpers.generate_bars(
        importance_df["Importance"], neutral=True
    )

    return importance_df


def show_table(df):
    df = df.drop("Importance Value", axis="columns").rename(
        columns={
            "Importance": get_term("Importance"),
            "Feature": get_term("Feature"),
        }
    )
    AgGrid(df, fit_columns_on_grid_load=True)


def view():
    to_show = format_importance_to_view(importance.compute_importance())
    to_show = to_show.sort_values(by="Importance Value", axis="index", ascending=False)
    to_show = sibylapp.view.utils.filtering.process_options(to_show)
    show_table(to_show)
    return to_show["Feature"]


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "**"
            + get_term("Feature")
            + " Importance** refers to how much the model uses a specific "
            + get_term("Feature").lower()
            + " overall in its predictions. A large importance bar means this "
            + get_term("Feature").lower()
            + " is used frequently,"
            " while a smaller bar means it is used less."
        )
        st.markdown(
            "You can also **filter** and **search** "
            "the "
            + get_term("Feature").lower()
            + " table shown or adjust the **sort order**."
        )
        st.markdown(
            "The **Explor a %s** tab let's you see how the model uses a specific %s in more detail. The "
            "generated plot shows how much each value for the chosen %s contributes to the model's "
            "prediction across the training set, as well as the corresponding model predictions."
            % (
                get_term("Feature"),
                get_term("Feature").lower(),
                get_term("Feature").lower(),
            )
        )
