import numpy as np
import streamlit as st

from sibylapp2 import config
from sibylapp2.compute import context, model
from sibylapp2.view import sidebar


@st.cache_data
def get_relevant_eids(preds, _all_preds):
    return [eid for eid in _all_preds if _all_preds[eid] in preds]


@st.cache_data
def get_relevant_eids_range(pred_range, _all_preds):
    return [eid for eid in _all_preds if pred_range[0] <= _all_preds[eid] <= pred_range[1]]


def filter_eids(eids, eid_dict):
    return {eid: eid_dict[eid] for eid in eids}


def view_prediction_selection(predictions, disabled=False):
    pred_values = list(predictions.values())
    if config.PREDICTION_TYPE in (config.PredType.BOOLEAN, config.PredType.CATEGORICAL):
        chosen_preds = st.multiselect(
            "Predictions to visualize",
            list(np.unique(pred_values)),
            default=np.unique(pred_values),
            format_func=config.pred_format_func,
            disabled=disabled,
        )
        eids = get_relevant_eids(chosen_preds, predictions)
    else:
        min_pred = min(pred_values)
        max_pred = max(pred_values)
        pred_range = st.slider(
            "Predictions to visualize",
            min_pred,
            max_pred,
            (min_pred, max_pred),
            disabled=disabled,
        )
        eids = get_relevant_eids_range(pred_range, predictions)
    return eids


def view_filtering(include_show_more=False):
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

    exp = st.expander("Search and filter", expanded=True)

    with exp:
        st.text_input(
            "Search by %s" % context.get_term("Feature").lower(),
            key="search_term",
            value=st.session_state["search_term"],
        )
        st.multiselect(
            "Filter by category",
            context.get_category_list(),
            key="filters",
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
            to_show["Feature"].str.contains(st.session_state["search_term"], case=False, na=False)
        ]
    return to_show


def process_search_on_features(features):
    if st.session_state["search_term"] is not None:
        features = features[
            features["Feature"].str.contains(st.session_state["search_term"], case=False, na=False)
        ]
    if len(st.session_state["filters"]) > 0:
        features = features[features["Category"].isin(st.session_state["filters"])]
    return features.index


def process_filter(to_show):
    if len(st.session_state["filters"]) > 0:
        return to_show[to_show["Category"].isin(st.session_state["filters"])]
    return to_show
