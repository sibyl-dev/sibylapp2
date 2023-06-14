import streamlit as st
from sibylapp.view.utils import filtering, setup
from sibylapp.view import explore_feature, feature_importance
from sibylapp.compute.context import get_term


setup.setup_page()


# Global options ------------------------------
filtering.view()
feature_importance.view_instructions()


tab1, tab2 = st.tabs(
    [
        get_term("Feature Importance"),
        "Explore a %s" % get_term("Feature"),
    ]
)
with tab1:
    features = feature_importance.view()

with tab2:
    explore_feature.view(features)
