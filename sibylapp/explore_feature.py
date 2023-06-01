import streamlit as st
from sibylapp.context import get_term
from sibylapp import contributions, entities, api, model
from pyreal.visualize import feature_scatter_plot
import matplotlib.pyplot as plt


def generate_feature_plot(feature):
    feature_scatter_plot(contributions.get_all_contributions(), feature, predictions=model.predictions(entities.get_eids()))
    st.pyplot(plt.gcf())
    plt.clf()


def view(features):
    feature = st.selectbox("Select a %s" % get_term("feature"), features)
    generate_feature_plot(feature)