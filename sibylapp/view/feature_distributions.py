import streamlit as st
from sibylapp.compute import entities, model, contributions, context
from sibylapp import config
from sibylapp.view.utils.helpers import generate_bars, process_options, show_sorted_contributions
from st_aggrid import AgGrid
import pandas as pd
from pyreal.visualize import swarm_plot
import matplotlib.pyplot as plt
import numpy as np


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


def view():
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

    subtab1, subtab2 = st.tabs(["Average Contribution Table", "Summary plot"])
    with subtab1:
        sort_by = st.selectbox(
            "Sort order", ["Absolute", "Ascending", "Descending", "Side-by-side"]
        )

        contributions_in_range = get_relevant_contributions(pred_range, predictions, contributions_results)

        to_show = generate_distribution_table(contributions_in_range)
        show_sorted_contributions(to_show, sort_by, show_table)

    with subtab2:
        st.pyplot(generate_swarm_plot(contributions_in_range), clear_figure=True)


"""
import streamlit as st
from sibylapp import entities, api, contributions, helpers
from sibylapp.config import pred_format_func
import numpy as np
import pandas as pd
from pyreal.visualize import swarm_plot
import matplotlib.pyplot as plt
from plotly.express import strip


def format_contributions(df):
    df = df.drop(["Contribution"], axis="columns")
    return df.rename(
        columns={
            "Value": "Feature Value",
            "Contribution Value": "Contribution",
            "Feature": "Feature Name",
        }
    )


def view(contribution_results, predictions, categorical=True, nbins=2):
    prediction_lst = list(predictions.values())
    max_val = max(prediction_lst)
    min_val = min(prediction_lst)

    all_eids = {}
    if not categorical:
        total_range = (max_val - min_val) / nbins
        thresholds = [min_val + n * total_range for n in range(nbins)]
        thresholds.append(max_val + 1)
        clss = [
            pred_format_func(thresholds[i]) + "-" + pred_format_func(thresholds[i + 1])
            for i in range(nbins)
        ]
        for i in range(nbins):
            eids = [
                x
                for x in predictions
                if thresholds[i] <= predictions[x] < thresholds[i + 1]
            ]
            all_eids[clss[i]] = eids

    if categorical:
        for cls in np.unqiue(prediction_lst):
            eids = [x for x in predictions if predictions[x] == cls]
            all_eids[cls] = eids

    cls = st.selectbox("Prediction", list(all_eids.keys()))

    st.text("Average contributions for prediction: " + cls)

    cls_contributions = {
        eid: format_contributions(contribution_results[eid]) for eid in all_eids[cls]
    }
    averaged = pd.concat(
        [cls_contributions[eid]["Contribution"] for eid in cls_contributions], axis=1
    ).mean(axis=1)
    to_show = contribution_results[next(iter(contribution_results))]
    to_show["Contribution Value"] = averaged
    to_show["Contribution"] = helpers.generate_bars(to_show["Contribution Value"])
    contributions.view(to_show.drop("Value", axis="columns"))

    #st.write(pd.concat(cls_contributions, axis=0))
    #fig = strip(pd.concat(cls_contributions, axis=0), x="Contribution", y="Feature Name", color="Feature Value")
    #st.plotly_chart(fig)

    swarm_plot(cls_contributions)
    st.pyplot(plt.gcf())
    plt.clf()

"""