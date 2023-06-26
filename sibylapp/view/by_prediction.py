import streamlit as st
from sibylapp.compute import context
from sibylapp.view.utils.helpers import rename_for_pyreal_vis
from sibylapp.view.utils.filtering import process_options
from st_aggrid import AgGrid
import pandas as pd
from pyreal.visualize import swarm_plot
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


def show_table(df):
    df = df.drop("Contribution Value", axis="columns").rename(
        columns={
            "Contribution": context.get_term("Contribution"),
            "Feature": context.get_term("Feature"),
        }
    )
    AgGrid(df, fit_columns_on_grid_load=True)


def get_numeric_metrics(row):
    return "%.2f - %.2f - %.2f - %.2f - %.2f" % (
        row.min(),
        row.quantile(0.25),
        row.mean(),
        row.quantile(0.75),
        row.max(),
    )


def get_categorical_metrics(row):
    values, counts = np.unique(row, return_counts=True)
    counts = counts / sum(counts) * 100
    return ["%.2f%%: %s" % (count, value) for (value, count) in zip(values, counts)]


def aggregate(row):
    if pd.api.types.is_numeric_dtype(pd.to_numeric(row, errors="ignore")):
        return get_numeric_metrics(row)
    else:
        return get_categorical_metrics(row)


@st.cache_data(show_spinner="Generating plot...")
def generate_swarm_plot(contribution_dict):
    swarm_plot(contribution_dict, type="strip")
    return plt.gcf()


@st.cache_data(show_spinner="Generating plot...")
def generate_feature_plot(feature, contribution_dict):
    data = pd.DataFrame(
        [
            contribution_dict[eid][contribution_dict[eid]["Feature"] == feature][
                "Feature Value"
            ]
            for eid in contribution_dict
        ]
    ).squeeze()
    if pd.api.types.is_numeric_dtype(pd.to_numeric(data, errors="ignore")):
        trace1 = go.Box(x=data, boxpoints="all", name="")
        fig = go.Figure(data=[trace1])
        return fig
    else:
        fig = px.pie(
            data,
            values=data.value_counts().values,
            names=data.value_counts().index,
            title="",
        )
        return fig


def view_summary_plot(relevant_contributions):
    st.pyplot(generate_swarm_plot(rename_for_pyreal_vis(relevant_contributions)), clear_figure=True)


def view_feature_plot(relevant_contributions, table):
    feature = st.selectbox(
        "Select a %s" % context.get_term("feature"),
        process_options(table)["Feature"],
        key="feature distribution feature select",
    )
    st.plotly_chart(
        generate_feature_plot(feature, relevant_contributions),
        clear_figure=True,
        use_container_width=True,
    )
