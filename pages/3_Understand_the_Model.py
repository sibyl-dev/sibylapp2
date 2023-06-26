import streamlit as st
from sibylapp.view.utils import filtering, setup
from sibylapp.view import explore_feature, feature_importance, global_contributions
from sibylapp.compute.context import get_term
from sibylapp.compute import model, contributions


setup.setup_page()


# Global options ------------------------------
filtering.view_filtering()

# Filtering by prediction
all_contributions = contributions.get_dataset_contributions()

tab1, tab2, tab3 = st.tabs(
    [
        get_term("Feature Importance"),
        "Global %s" % get_term("Feature Contributions"),
        "Explore a %s" % get_term("Feature"),
    ]
)
with tab1:
    features = feature_importance.view()

with tab2:
    global_contributions.view(all_contributions)

with tab3:
    explore_feature.view(features)
