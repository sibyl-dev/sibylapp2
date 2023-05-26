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
