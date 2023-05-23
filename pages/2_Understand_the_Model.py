import streamlit as st
from sibylapp import importance, feature_distributions, filtering
from sibylapp.context import get_term

st.set_page_config(layout="wide")
st.title("Sibyl")


# Prepping explanations ---------------------
importance_results = importance.compute_importance()


# Global options ------------------------------
filtering.view()


tab1, tab2 = st.tabs(
    [get_term("Feature Importance"), "%s %s" % (get_term("Feature"), "Distributions")]
)
with tab1:
    importance.view(importance_results)
with tab2:
    feature_distributions.view()
