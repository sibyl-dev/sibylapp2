import inflect
import streamlit as st

from sibylapp.compute import api

lang = inflect.engine()


@st.cache_data(show_spinner="Fetching categories...")
def get_category_list():
    categories = api.fetch_categories()
    return list(categories["name"])


def fetch_context():
    # can't cache this or the st.cache_data command will be called before st.set_page_config
    return api.fetch_context()


def get_term(term, plural=False, lower=False, with_a=False):
    terms = fetch_context()["terms"]
    if term in terms:
        new_term = terms[term]
    else:
        new_term = term
    if plural:
        new_term = lang.plural(new_term)
    if lower:
        new_term = new_term.lower()
    if with_a:
        new_term = lang.a(new_term)
    return new_term


def get_gui_config(key):
    if "gui_config" not in fetch_context():
        return None
    return fetch_context()["gui_config"].get(key)
