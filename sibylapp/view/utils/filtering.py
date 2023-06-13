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


def view_filtering(include_show_more=True):
    if "show_more" not in st.session_state:
        st.session_state["show_more"] = False
    if "search_term" not in st.session_state:
        st.session_state["search_term"] = ""
    if "filters" not in st.session_state:
        st.session_state["filters"] = []

    if include_show_more:
        st.checkbox("Show all", key="show_more", value=st.session_state["show_more"])
    else:
        st.session_state["show_more"] = True

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


def process_options(to_show):
    return process_search(process_filter(process_show_more(to_show)))


def process_show_more(to_show):
    if not st.session_state["show_more"]:
        return to_show[0:10]
    return to_show


def process_search(to_show):
    if st.session_state["search_term"] is not None:
        to_show = to_show[
            to_show["Feature"].str.contains(st.session_state["search_term"], case=False)
        ]
    return to_show


def process_filter(to_show):
    if len(st.session_state["filters"]) > 0:
        return to_show[to_show["Category"].isin(st.session_state["filters"])]
    return to_show
