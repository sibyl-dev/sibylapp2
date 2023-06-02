import streamlit as st
from sibylapp.compute import entities, model, contributions, context
from sibylapp import config
from sibylapp.view.utils.helpers import generate_bars, process_options, show_sorted_contributions
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
    return "%.2f - %.2f - %.2f - %.2f - %.2f" \
           % (row.min(), row.quantile(.25), row.mean(), row.quantile(.75), row.max())


def get_categorical_metrics(row):
    values, counts = np.unique(row, return_counts=True)
    counts = counts / sum(counts) * 100
    return ["%.2f%%: %s" % (count, value) for (value, count) in zip(values, counts)]


def aggregate(row):
    if pd.api.types.is_numeric_dtype(pd.to_numeric(row, errors="ignore")):
        return get_numeric_metrics(row)
    else:
        return get_categorical_metrics(row)


@st.cache_data(show_spinner="Getting global contributions...")
def generate_distribution_table(contributions_in_range):
    averaged = pd.concat(
        [contributions_in_range[eid]["Contribution"] for eid in contributions_in_range], axis=1
    ).mean(axis=1)
    quantiles = pd.concat(
        [contributions_in_range[eid]["Feature Value"] for eid in contributions_in_range], axis=1
    ).apply(aggregate, axis=1)

    to_show = contributions_in_range[next(iter(contributions_in_range))].copy()
    to_show = to_show.rename(columns={
        "Feature Name": "Feature",
        "category": "Category",
    })[["Category", "Feature"]]

    to_show["Contribution Value"] = averaged
    to_show["Average Contribution"] = generate_bars(to_show["Contribution Value"])
    to_show["Distribution"] = quantiles
    return to_show


@st.cache_data(show_spinner="Getting relevant entries...")
def get_relevant_contributions(pred_range, _predictions, _contribution_results):
    eids = [eid for eid in _predictions if pred_range[0] <= _predictions[eid] <= pred_range[1]]
    return {
        eid: _contribution_results[eid] for eid in eids
    }


@st.cache_data(show_spinner="Generating plot...")
def generate_swarm_plot(contribution_dict):
    swarm_plot(contribution_dict, type="strip")
    return plt.gcf()


def generate_feature_plot(feature, contribution_dict):
    data = pd.DataFrame([contribution_dict[eid][contribution_dict[eid]["Feature Name"] == feature]["Feature Value"] for eid in contribution_dict]).squeeze()
    if pd.api.types.is_numeric_dtype(pd.to_numeric(data, errors="ignore")):
        trace1 = go.Box(x=data, boxpoints='all', name=feature)
        fig = go.Figure(data=[trace1])
        return fig
    else:
        fig = px.pie(data, values=data.value_counts().values, names=data.value_counts().index, title=feature)
        return fig


def view(features):
    if "dataset_eids" not in st.session_state:
        st.session_state["dataset_eids"] = entities.get_eids(config.DATASET_SIZE)
    predictions = model.get_predictions(st.session_state["dataset_eids"])
    contributions_results = contributions.get_contributions(
        st.session_state["dataset_eids"]
    )

    pred_values = predictions.values()
    min_pred = min(pred_values)
    max_pred = max(pred_values)
    a, size = sorted(pred_values), len(pred_values)
    min_diff = min([a[i + 1] - a[i] for i in range(size) if i+1 < size])
    pred_range = st.slider("Predictions to visualize", min_pred, max_pred, (min_pred, max_pred), step=min_diff)

    subtab1, subtab2, subtab3 = st.tabs(["Average Contribution Table", "Summary plot", "Feature Distributions"])
    with subtab1:
        sort_by = st.selectbox(
            "Sort order", ["Absolute", "Ascending", "Descending", "Side-by-side"]
        )

        contributions_in_range = get_relevant_contributions(pred_range, predictions, contributions_results)

        to_show = generate_distribution_table(contributions_in_range)
        show_sorted_contributions(to_show, sort_by, show_table)

    with subtab2:
        st.pyplot(generate_swarm_plot(contributions_in_range), clear_figure=True)

    with subtab3:
        feature = st.selectbox("Select a %s" % context.get_term("feature"), features, key="feature distribution feature select")
        st.plotly_chart(generate_feature_plot(feature, contributions_in_range), clear_figure=True)
