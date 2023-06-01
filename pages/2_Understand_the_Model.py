import streamlit as st
from sibylapp import importance, filtering, explore_feature, entities, config, setup
from sibylapp.context import get_term


setup.setup_page()


# Global options ------------------------------
filtering.view()


tab1, tab2 = st.tabs(
    [get_term("Feature Importance"), "Explore a %s" % get_term("Feature")]
)
with tab1:
    features = importance.view()

with tab2:
    explore_feature.view(features)
