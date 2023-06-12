import streamlit as st
import pandas as pd
from sibylapp.compute import contributions, api, context
from sklearn.neighbors import KDTree
from st_aggrid import AgGrid


def get_similar_entities(eid):
    result = api.fetch_similar_examples([eid])
    X = result[eid]["X"]
    y = result[eid]["y"]
    y_row = y.T
    y_row["Feature Name"] = context.get_term("Prediction")

    to_show = pd.concat([y_row, X], axis=0)
    st.write(to_show)


def view(eid):
    get_similar_entities(eid)
