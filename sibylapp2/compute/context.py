import inflect
import streamlit as st

from sibylapp2.compute import api

lang = inflect.engine()


@st.cache_data(show_spinner="Fetching categories...")
def get_category_list():
    categories = api.fetch_categories()
    return list(categories["name"])


def fetch_context():
    # can't cache this or the st.cache_data command will be called before st.set_page_config
    return api.fetch_context()["config"]


@st.cache_data(show_spinner=False)
def fetch_terms():
    context = fetch_context()
    if "terms" not in context:
        return {}
    return {key.lower(): value.lower() for key, value in context["terms"].items()}


@st.cache_data(show_spinner=False)
def get_config(config_name):
    return fetch_context().get(config_name)


def get_term(term, plural=False, with_a=False):
    """
    Return the configured language for term, using the same case (lower, UPPER, or Title) as
    the input term.
    Args:
        term (string): Term to translate
        plural (boolean): If True, pluralize the input
        with_a (boolean): If True, add a or an before the output, as appropriate

    Returns:
        The translated term, with the same case as the input term
    """
    terms = fetch_terms()
    if term.lower() not in terms:
        new_term = term
    elif term.islower():
        new_term = terms[term]
    elif term.isupper():
        new_term = terms[term.lower()].upper()
    elif term.istitle():
        new_term = terms[term.lower()].title()
    else:
        new_term = terms[term.lower()]

    if plural:
        new_term = lang.plural(new_term)
    if with_a:
        new_term = lang.a(new_term)
    return new_term
