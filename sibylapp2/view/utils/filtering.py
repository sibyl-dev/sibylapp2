import numpy as np
import streamlit as st

from sibylapp2 import config
from sibylapp2.compute import context, model
from sibylapp2.view.utils import display


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


def view_entity_select(eid_text="eid", prefix=None, default=0):
    def format_func(eid):
        return f"{context.get_term('Entity')} {eid} ({config.pred_format_func(predictions[eid])})"

    predictions = model.get_predictions(
        st.session_state["eids"], model_id=st.session_state["model_id"]
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


def view_row_select(eid, row_ids, row_id_text="row_id", prefix=None, default=0):
    def format_rowid_select(row_id):
        return str(row_id)

    if row_id_text not in st.session_state:
        st.session_state[f"select_{row_id_text}_index"] = default

    if prefix is None:
        select_text = "Select row"
    else:
        select_text = f"Select {prefix} row"

    st.sidebar.selectbox(
        select_text,
        row_ids,
        format_func=format_rowid_select,
        index=st.session_state[f"select_{row_id_text}_index"],
        key=row_id_text,
    )
    predictions = model.get_predictions_for_rows(
        eid, row_ids, model_id=st.session_state["model_id"]
    )
    pred = predictions[st.session_state[row_id_text]]

    if st.session_state["display_proba"]:
        predictions_proba = model.get_predictions_for_rows(
            eid, row_ids, model_id=st.session_state["model_id"], return_proba=True
        )
        pred_proba = predictions_proba[st.session_state[row_id_text]]
        pred_display = (
            config.pred_format_func(pred)
            + " ("
            + config.pred_format_func(pred_proba, display_proba=True)
            + ")"
        )
    else:
        pred_display = config.pred_format_func(pred)
    st.sidebar.metric(context.get_term("Prediction"), pred_display)


def view_model_select(default=0):
    if "model_id" in st.session_state:
        st.session_state["select_model_index"] = st.session_state["model_ids"].index(
            st.session_state["model_id"]
        )
    else:
        st.session_state["select_model_index"] = default
    if len(st.session_state["model_ids"]) > 1:
        st.sidebar.selectbox(
            "Select model",
            st.session_state["model_ids"],
            index=st.session_state["select_model_index"],
            key="model_id",
        )
    else:
        st.session_state["model_id"] = st.session_state["model_ids"][0]


def view_selection():
    """
    This function handles the display of entities selection.
    """
    view_entity_select()
    eid = st.session_state["eid"]
    row_ids = st.session_state["row_id_dict"][eid]
    if len(row_ids) > 1:
        view_row_select(eid, row_ids, row_id_text="row_id")
        st.session_state["use_rows"] = True
    else:
        st.session_state["row_id"] = None
        display.view_prediction(eid)


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
            to_show["Feature"].str.contains(st.session_state["search_term"], case=False, na=False)
        ]
    return to_show


def process_search_on_features(features):
    if st.session_state["search_term"] is not None:
        features = features.index[
            features.index.str.contains(st.session_state["search_term"], case=False, na=False)
        ]
    return features


def process_filter(to_show):
    if len(st.session_state["filters"]) > 0:
        return to_show[to_show["Category"].isin(st.session_state["filters"])]
    return to_show
