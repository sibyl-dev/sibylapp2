import streamlit as st
from sibylapp import importance, filtering, explore_feature
from sibylapp.context import get_term

st.set_page_config(layout="wide")
st.title("Sibyl")


# Prepping explanations ---------------------
importance_results = importance.compute_importance()


# Global options ------------------------------
filtering.view()


tab1, tab2 = st.tabs(
    [get_term("Feature Importance"), "Explore a %s" % get_term("Feature")]
)
with tab1:
    features = importance.view(importance_results)

with tab2:
    explore_feature.view(features)
