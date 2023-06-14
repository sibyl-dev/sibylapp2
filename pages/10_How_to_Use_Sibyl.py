import streamlit as st
from sibylapp.view.utils import setup
from sibylapp.compute.context import get_term

setup.setup_page()

st.markdown(
    "Sibyl offers many ways to better understand your ML models, making them easier to use."
)

st.header("Understanding model predictions")
st.markdown(
    "The **Explore a Prediction** page lets you investigate a specific model prediction. On this page, "
    "you can select a %s on the left sidebar to get an explanation of the model's prediction on that %s."
    % (get_term("Entity"), get_term("Entity"))
)
st.subheader("Explore a Prediction")
st.markdown(
    "This page tells you how much each feature contributed to the model's prediction on that house."
)
