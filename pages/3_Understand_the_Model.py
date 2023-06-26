import streamlit as st
from sibylapp.view.utils import filtering, setup
from sibylapp.view import explore_feature, feature_importance, global_contributions
from sibylapp.compute.context import get_term


setup.setup_page()


# Global options ------------------------------
filtering.view_filtering()


tab1, tab2, tab3 = st.tabs(
    [
        get_term("Feature Importance"),
        get_term("Global Contributions"),
        "Explore a %s" % get_term("Feature"),
    ]
)
with tab1:
    features = feature_importance.view()

with tab2:
    global_contributions.view()

with tab3:
    explore_feature.view(features)
