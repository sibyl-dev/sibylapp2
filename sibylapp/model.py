import streamlit as st


@st.cache_data
def predictions(_app, sample):
    return _app.predict(sample)
