import numpy as np
import streamlit as st

from sibylapp import config
from sibylapp.compute import context, model


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


def view_entity_select(eid_text="eid", prefix=None, default=0, add_prediction=True):
    def format_func(eid):
        if add_prediction:
            return (
                f"{context.get_term('Entity')} {eid} ("
                + str(config.pred_format_func(predictions[eid]))
                + ")"
            )
        else:
            return f"{context.get_term('Entity')} {eid}"

    if add_prediction:
        predictions = model.get_predictions(
            st.session_state["eids"], return_proba=st.session_state["display_proba"]
        )

    if eid_text in st.session_state:
        st.session_state[f"select_{eid_text}_index"] = st.session_state["eids"].index(
            st.session_state[eid_text]
        )
    else:
        st.session_state[f"select_{eid_text}_index"] = default

    if prefix is None:
        select_text = "Select %s" % (context.get_term("Entity"))
    else:
        select_text = "Select %s %s" % (prefix, context.get_term("Entity"))
    st.sidebar.selectbox(
        select_text,
        st.session_state["eids"],
        format_func=format_func,
        index=st.session_state[f"select_{eid_text}_index"],
        key=eid_text,
    )
    if add_prediction:
        pred = predictions[st.session_state[eid_text]]
        st.sidebar.metric(context.get_term("Prediction"), config.pred_format_func(pred))

    st.session_state["display_proba"] = st.checkbox(
        "Show probability",
        value=st.session_state["display_proba"],
        help="Display prediction in terms of probability",
        disabled=not config.SUPPORT_PROBABILITY,
    )


def view_time_select(eid, row_ids, row_id_text="row_id", prefix=None, default=0):
    def format_rowid_select(row_id):
        return f"Timestamp: {row_id}"

    if row_id_text not in st.session_state:
        st.session_state[f"select_{row_id_text}_index"] = default

    if prefix is None:
        select_text = "Select prediction time"
    else:
        select_text = f"Select {prefix} prediction time"

    row_id = st.sidebar.selectbox(
        select_text,
        row_ids,
        format_func=format_rowid_select,
        index=st.session_state[f"select_{row_id_text}_index"],
        key=row_id_text,
    )
    predictions = model.get_predictions_for_rows(
        eid, row_ids, return_proba=st.session_state["display_proba"]
    )
    pred = predictions[row_id]
    st.sidebar.metric(context.get_term("Prediction"), config.pred_format_func(pred))


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

    expanded = bool(
        ("search_term" in st.session_state and len(st.session_state["search_term"]) > 0)
        or ("filters" in st.session_state and len(st.session_state["filters"]) > 0)
    )
    exp = st.expander("Search and filter", expanded=expanded)

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
            to_show["Feature"].str.contains(st.session_state["search_term"], case=False)
        ]
    return to_show


def process_search_on_features(features):
    if st.session_state["search_term"] is not None:
        features = [
            feature
            for feature in features
            if st.session_state["search_term"].lower() in feature.lower()
        ]
    return features


def process_filter(to_show):
    if len(st.session_state["filters"]) > 0:
        return to_show[to_show["Category"].isin(st.session_state["filters"])]
    return to_show
