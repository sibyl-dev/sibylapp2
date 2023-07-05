import streamlit as st

from sibylapp.compute import api


@st.cache_data
def get_similar_entities(eid):
    result = api.fetch_similar_examples([eid])
    x = result[eid]["X"]
    x = x.rename(columns={"category": "Category"})
    y = result[eid]["y"]
    y["Feature"] = "Real Target Value"

    return x, y
