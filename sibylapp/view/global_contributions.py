import pandas as pd
import streamlit as st
from sibylapp.compute import contributions
from sibylapp.view.utils.helpers import (
    generate_bars_bidirectional,
    process_options,
    rename_for_pyreal_vis,
)
from st_aggrid import AgGrid
import plotly.graph_objects as go
import plotly.express as px
from pyreal.visualize import swarm_plot
import matplotlib.pyplot as plt


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
        fig.update_layout(title="Distributions for '%s'" % feature)
        return fig
    else:
        fig = px.pie(
            data,
            values=data.value_counts().values,
            names=data.value_counts().index,
            title="Distributions for '%s'" % feature,
        )
        return fig


def view_summary_plot(contributions):
    st.pyplot(
        generate_swarm_plot(rename_for_pyreal_vis(contributions)),
        clear_figure=True,
    )


def view_feature_plot(contributions_to_show, feature):
    st.plotly_chart(
        generate_feature_plot(feature, contributions_to_show),
        clear_figure=True,
        use_container_width=True,
    )


def view(all_contributions):
    sort_by = st.selectbox(
        "Sort order", ["Total", "Most Increasing", "Most Decreasing"]
    )

    global_contributions = contributions.compute_global_contributions(all_contributions)
    bars = generate_bars_bidirectional(
        global_contributions["negative"], global_contributions["positive"]
    )
    feature_info = all_contributions[next(iter(all_contributions))][
        ["category", "Feature"]
    ].rename(columns={"category": "Category"})
    to_show = pd.concat([feature_info, bars, global_contributions], axis="columns")

    if sort_by == "Total":
        to_show = to_show.reindex(
            (to_show["negative"].abs() + to_show["positive"])
            .sort_values(ascending=False)
            .index
        )
    if sort_by == "Most Increasing":
        to_show = to_show.sort_values(by="positive", axis="index", ascending=False)
    if sort_by == "Most Decreasing":
        to_show = to_show.sort_values(by="negative", axis="index")

    to_show = process_options(to_show).drop(["positive", "negative"], axis=1)
    AgGrid(to_show, fit_columns_on_grid_load=True)
    return to_show
