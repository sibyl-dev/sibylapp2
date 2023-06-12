import streamlit as st
from sibylapp.compute import context, model
from sibylapp import config


def view_entity_select():
    def format_func(s):
        return (
            f"{context.get_term('Entity')} {s} ("
            + config.pred_format_func(predictions[s])
            + ")"
        )

    predictions = model.get_predictions(st.session_state["eids"])

    if "eid" in st.session_state:
        st.session_state["select_eid_index"] = st.session_state["eids"].index(
            st.session_state["eid"]
        )
    else:
        st.session_state["select_eid_index"] = 0

    st.session_state["eid"] = st.sidebar.selectbox(
        "Select %s" % context.get_term("Entity"),
        st.session_state["eids"],
        format_func=format_func,
        index=st.session_state["select_eid_index"],
    )
    pred = predictions[st.session_state["eid"]]
    st.sidebar.metric(context.get_term("Prediction"), config.pred_format_func(pred))


def view_filtering():
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
