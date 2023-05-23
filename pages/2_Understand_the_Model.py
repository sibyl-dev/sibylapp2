import streamlit as st
from sibylapp import importance, filtering
from sibylapp.context import get_term

st.set_page_config(layout="wide")
st.title("Sibyl")


# Prepping explanations ---------------------
importance_results = importance.compute_importance()


# Global options ------------------------------
filtering.view()


tab1, = st.tabs(
    [get_term("Feature Importance"), ]
)
with tab1:
    importance.view(importance_results)
