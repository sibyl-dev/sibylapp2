import streamlit as st
from sibylapp.compute.context import get_term
from sibylapp.compute import contributions
from sibylapp.view.utils import helpers
from sibylapp.view import feature_contribution
from sibylapp import config
from pyreal.visualize import feature_scatter_plot
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
from streamlit_plotly_events import plotly_events


@st.cache_data(show_spinner="Generating plot...")
def generate_feature_plot(contributions_to_show, predictions, feature):
    data = {
        i: contributions_to_show[i][contributions_to_show[i]["Feature"] == feature][
            ["Contribution", "Feature Value"]
        ].squeeze()
        for i in contributions_to_show
    }
    formatted_pred = {i: config.pred_format_func(predictions[i]) for i in predictions}
    # Adding the space after prediction as a hack to allow two columns with the same displayed name
    df = pd.concat(
        [
            pd.DataFrame(data).T,
            pd.Series(predictions, name="Prediction "),
            pd.Series(formatted_pred, name="Prediction"),
        ],
        axis=1,
    )
    df["ID"] = df.index
    df = df.rename(columns={"Feature Value": "Value"})
    hover_data = {
        "Contribution": ":.3f",
        "Value": True,
        "Prediction ": False,
        "Prediction": True,
        "ID": True,
    }
    fig = px.scatter(
        df,
        x="Value",
        y="Contribution",
        color="Prediction ",
        color_continuous_scale="Brwnyl",
        hover_data=hover_data,
    )
    return fig


def view(contributions_to_show, predictions, feature):
    fig = generate_feature_plot(contributions_to_show, predictions, feature)
    selected_index = plotly_events(fig)
    if len(selected_index) > 0:
        eid = list(contributions_to_show.keys())[selected_index[0]["pointIndex"]]
        #st.write(contributions.get_contributions(eid))
        feature_contribution.view(eid)


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "The **Explore a {feature_up}** tab lets you see how the model uses a specific {feature} in more detail. "
            "The plot on the left shows how much each value for the chosen {feature} contributes to the model's "
            "prediction across the training set, as well as the corresponding model predictions.".format(
                feature_up=get_term("Feature"), feature=get_term("Feature", l=True)
            )
        )
        st.markdown(
            "The plot on the right shows how the values for the chosen {feature} varied across the training dataset. "
            "For numeric features, you will see a box-and-whiskers plot with some notable distribution values "
            "(hover for specifics). For categorical features, you will see a pie chart.".format(
                feature=get_term("Feature", l=True)
            )
        )
        st.markdown(
            "You can use the selector to visualize only rows in the training set with a subset of prediction values"
        )
