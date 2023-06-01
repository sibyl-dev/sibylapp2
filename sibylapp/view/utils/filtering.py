import streamlit as st
from sibylapp.compute import context


def view():
    if "show_more" not in st.session_state:
        st.session_state["show_more"] = False
    if "search_term" not in st.session_state:
        st.session_state["search_term"] = ""
    if "filters" not in st.session_state:
        st.session_state["filters"] = []

    st.checkbox("Show all", key="show_more", value=st.session_state["show_more"])

    if (
        "search_term" in st.session_state and len(st.session_state["search_term"]) > 0
    ) or ("filters" in st.session_state and len(st.session_state["filters"]) > 0):
        expanded = True
    else:
        expanded = False
    exp = st.expander("Search and filter", expanded=expanded)

    with exp:
        st.session_state["search_term"] = st.text_input(
            "Search by %s" % context.get_term("Feature").lower(),
            value=st.session_state["search_term"],
        )
        st.session_state["filters"] = st.multiselect(
            "Filter by category",
            context.get_category_list(),
            default=st.session_state["filters"],
        )
