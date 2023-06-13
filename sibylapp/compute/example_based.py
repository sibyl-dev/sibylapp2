import streamlit as st
import pandas as pd
from sibylapp.compute import api, context


@st.cache_data
def get_similar_entities(eid):
    result = api.fetch_similar_examples([eid])
    X = result[eid]["X"]
    y = result[eid]["y"]
    y_row = y.T
    y_row["Feature Name"] = "Real Target Value"

    return pd.concat([y_row, X], axis=0)
