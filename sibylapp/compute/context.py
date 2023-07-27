import inflect
import streamlit as st

from sibylapp.compute import api

lang = inflect.engine()


@st.cache_data(show_spinner="Fetching categories...")
def get_category_list():
    categories = api.fetch_categories()
    return list(categories["name"])


@st.cache_data(show_spinner="Fetching context...")
def get_context():
    return api.fetch_context()


def get_term(term, p=False, l=False, a=False):
    terms = get_context()["terms"]
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


def get_gui_config(key, default=None):
    return get_context()["gui_config"].get(key, default)


def get_flip_colors_from_api():
    return True if get_gui_config("model_pred_bad_outcome") else False


def get_pred_format_func_from_api():
    if get_gui_config("pred_type") == "numeric":
        if get_gui_config("pred_format_string") is not None:
            return get_gui_config("pred_format_string").format(pred)
    if get_gui_config("pred_type") == "boolean":
        return (
            get_gui_config("pos_pred_name", pred)
            if pred
            else get_gui_config("neg_pred_name", pred)
        )
