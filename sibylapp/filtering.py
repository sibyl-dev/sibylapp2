import streamlit as st
from sibylapp.context import get_term
from sibylapp import context


def view():
    if "show_more" not in st.session_state:
        st.session_state["show_more"] = False
    if "search_term" not in st.session_state:
        st.session_state["search_term"] = ""
    if "filters" not in st.session_state:
        st.session_state["filters"] = []
    if "expanded_search_bar" not in st.session_state:
        st.session_state["expanded_search_bar"] = False

    st.checkbox("Show all", key="show_more", value=st.session_state["show_more"])

    exp = st.expander("Search and filter", expanded=st.session_state["expanded_search_bar"])
    print(exp.expanded)
    with exp:
        st.session_state["search_term"] = st.text_input(
            "Search by %s" % get_term("Feature").lower(), value=st.session_state["search_term"]
        )
        st.session_state["filters"] = st.multiselect(
            "Filter by category", context.get_category_list(), default=st.session_state["filters"]
        )