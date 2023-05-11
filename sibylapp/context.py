from sibylapp import api
import streamlit as st


@st.cache_data
def get_category_list():
    categories = api.fetch_categories()
    return list(categories["name"])


@st.cache_data
def get_terms():
    return api.fetch_terms()


def get_term(term):
    if term in get_terms():
        return get_terms()[term]
    return term
