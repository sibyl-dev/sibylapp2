import streamlit as st


def process_options(to_show):
    return process_search(
        process_filter(process_show_more(to_show)))


def process_show_more(to_show):
    if not st.session_state["show_more"]:
        return to_show[0:10]
    return to_show


def process_search(to_show):
    if st.session_state["search_term"] is not None:
        to_show = to_show[to_show["Feature"].str.contains(st.session_state["search_term"], case=False)]
    return to_show


def process_filter(to_show):
    if len(st.session_state["filters"]) > 0:
        return to_show[to_show["Category"].isin(st.session_state["filters"])]
    return to_show
