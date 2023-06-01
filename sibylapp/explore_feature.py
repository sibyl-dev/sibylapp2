import streamlit as st
from sibylapp.context import get_term
from sibylapp import contributions, entities, api, model, config
from pyreal.visualize import feature_scatter_plot
import matplotlib.pyplot as plt


@st.cache_data
def generate_feature_plot(feature):
    eids = entities.get_eids(1000)
    predictions = model.predictions(eids)
    feature_scatter_plot(contributions.get_contributions(eids), feature, predictions=predictions)
    st.pyplot(plt.gcf(), use_container_width=False)
    plt.clf()


def view(features):
    feature = st.selectbox("Select a %s" % get_term("feature"), features)
    generate_feature_plot(feature)