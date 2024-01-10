import streamlit as st

from sibylapp2.compute import api


@st.cache_data
def get_similar_entities(eid, model_id=api.fetch_model_id()):
    result = api.fetch_similar_examples([eid], model_id)
    x = result[eid]["X"]
    x = x.rename(columns={"category": "Category"})
    y = result[eid]["y"]
    y["Feature"] = "Real Target Value"

    return x, y
