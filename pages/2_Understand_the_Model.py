import streamlit as st
from sibylapp.view.utils import filtering, setup
from sibylapp.view import explore_feature, feature_importance, feature_distributions
from sibylapp.compute.context import get_term


setup.setup_page()


# Global options ------------------------------
filtering.view()


tab1, tab2, tab3 = st.tabs(
    [
        get_term("Feature Importance"),
        "%s Distributions" % get_term("Feature"),
        "Explore a %s" % get_term("Feature"),
    ]
)
with tab1:
    features = feature_importance.view()

with tab2:
    feature_distributions.view()

with tab3:
    explore_feature.view(features)
