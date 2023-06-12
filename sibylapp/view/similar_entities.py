import streamlit as st
import pandas as pd
from sibylapp.compute import contributions, api
from sklearn.neighbors import KDTree


@st.cache_data
def get_similar_entities(eid):
    result = api.fetch_similar_examples([eid])
    st.write(result)


def view(eid):
    get_similar_entities(eid)