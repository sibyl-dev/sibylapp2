import streamlit as st
from sibylapp.compute.context import get_term
from sibylapp.compute import contributions, model, entities
from pyreal.visualize import feature_scatter_plot
import matplotlib.pyplot as plt


@st.cache_data(show_spinner="Generating plot...")
def generate_feature_plot(feature):
    if "dataset_eids" not in st.session_state:
        st.session_state["dataset_eids"] = entities.get_eids(1000)
    predictions = model.get_predictions(st.session_state["dataset_eids"])
    contributions_results = contributions.get_contributions(
        st.session_state["dataset_eids"]
    )
    feature_scatter_plot(contributions_results, feature, predictions=predictions)
    st.pyplot(plt.gcf(), use_container_width=False, clear_figure=True)


def view(features):
    feature = st.selectbox("Select a %s" % get_term("feature"), features)
    generate_feature_plot(feature)
