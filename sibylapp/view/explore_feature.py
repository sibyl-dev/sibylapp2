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
