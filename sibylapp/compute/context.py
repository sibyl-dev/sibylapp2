import inflect
import streamlit as st

from sibylapp.compute import api

lang = inflect.engine()

# we do this once here instead of caching to avoid a bug caused by calling st.cache_data
#   in config, before pages have been set up
context = api.fetch_context()


@st.cache_data(show_spinner="Fetching categories...")
def get_category_list():
    categories = api.fetch_categories()
    return list(categories["name"])


def get_term(term, p=False, l=False, a=False):
    terms = context["terms"]
    if term in terms:
        new_term = terms[term]
    else:
        new_term = term
    if p:
        new_term = lang.plural(new_term)
    if l:
        new_term = new_term.lower()
    if a:
        new_term = lang.a(new_term)
    return new_term


def get_gui_config(key):
    if "gui_config" not in context:
        return None
    return context["gui_config"].get(key)
