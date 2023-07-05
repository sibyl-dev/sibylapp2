import inflect
import streamlit as st

from sibylapp.compute import api

lang = inflect.engine()


@st.cache_data(show_spinner="Fetching categories...")
def get_category_list():
    categories = api.fetch_categories()
    return list(categories["name"])


@st.cache_data(show_spinner="Fetching terms...")
def get_terms():
    return api.fetch_terms()


def get_term(term, p=False, l=False, a=False):
    if term in get_terms():
        new_term = get_terms()[term]
    else:
        new_term = term
    if p:
        new_term = lang.plural(new_term)
    if l:
        new_term = new_term.lower()
    if a:
        new_term = lang.a(new_term)
    return new_term
