import streamlit as st

from sibylapp2.compute import context, model
from sibylapp2.config import SUPPORT_PROBABILITY, pred_format_func


def show_probability_select_box():
    if SUPPORT_PROBABILITY:
        st.sidebar.checkbox(
            "Show probability",
            value=st.session_state["display_proba"],
            help="Display prediction in terms of probability",
            key="display_proba",
        )


def view_prediction(eid):
    pred = model.get_predictions(st.session_state["eids"], model_id=st.session_state["model_id"])[
        eid
    ]
    if st.session_state["display_proba"]:
        pred_proba = model.get_predictions(
            st.session_state["eids"], model_id=st.session_state["model_id"], return_proba=True
        )[eid]
        pred_display = (
            f"{pred_format_func(pred)} ({pred_format_func(pred_proba, display_proba=True)})"
        )
    else:
        pred_display = pred_format_func(pred)

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


def view_entity_select(eid_text="eid", prefix=None, default=0):
    def format_func(eid):
        return f"{context.get_term('Entity')} {eid} ({pred_format_func(predictions[eid])})"

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
            pred_format_func(pred) + " (" + pred_format_func(pred_proba, display_proba=True) + ")"
        )
    else:
        pred_display = pred_format_func(pred)
    st.sidebar.metric(context.get_term("Prediction"), pred_display)


def view_entity_and_row_select():
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
        view_prediction(eid)
