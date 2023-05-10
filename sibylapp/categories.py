from sibylapp import api
import streamlit as st


@st.cache_data
def get_category_list():
    categories = api.fetch_categories()
    return list(categories["name"])
