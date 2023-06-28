import streamlit as st
from sibylapp.compute.context import get_term
from sibylapp.compute import contributions, model, entities
from sibylapp.view.utils import helpers
from pyreal.visualize import feature_scatter_plot
import matplotlib.pyplot as plt


@st.cache_data(show_spinner="Generating plot...")
def generate_feature_plot(contributions_to_show, predictions, feature):
    contributions_renamed = helpers.rename_for_pyreal_vis(contributions_to_show)
    feature_scatter_plot(contributions_renamed, feature, predictions=predictions)
    st.pyplot(plt.gcf(), clear_figure=True)


def view(contributions_to_show, predictions, feature):
    generate_feature_plot(contributions_to_show, predictions, feature)


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
