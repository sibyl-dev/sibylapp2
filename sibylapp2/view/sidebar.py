import streamlit as st

from sibylapp2.compute import context, model
from sibylapp2 import config


def show_probability_select_box():
    if config.SUPPORT_PROBABILITY:
        st.sidebar.checkbox(
            "Show probability",
            value=st.session_state["display_proba"],
            help="Display prediction in terms of probability",
            key="display_proba",
        )


def set_up_sidebar(
    model_select=False,
    entity_select=False,
    row_select=False,
    prediction=False,
    probability_select=False,
):
    if model_select:
        view_model_select()
    if entity_select:
        view_entity_select()
    if row_select:
        view_row_select()
    if prediction:
        view_prediction(st.session_state["eid"], st.session_state.get("row_id", None))
    if probability_select:
        show_probability_select_box()


def view_prediction(eid, row_id=None):
    row_id = [row_id] if row_id is not None else None
    pred = model.get_predictions([eid], row_id, model_id=st.session_state["model_id"])
    st.write(pred)
    if st.session_state["display_proba"]:
        pred_proba = model.get_predictions(
            [eid], row_id, model_id=st.session_state["model_id"], return_proba=True
        )
        pred_display = (
            f"{config.pred_format_func(pred)} ({config.pred_format_func(pred_proba, pred_is_probability=True)})"
        )
    else:
        pred_display = config.pred_format_func(pred)

    st.sidebar.metric(context.get_term("Prediction"), pred_display)


def view_model_select(default=0):
    if config.DISABLE_MODEL_SELECTION:
        return
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
        return f"{eid} ({config.pred_format_func(predictions[eid])})"

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


def view_row_select(eid=None, row_ids=None, row_id_text="row_id", prefix=None, default=0):
    if eid is None:
        eid = st.session_state["eid"]
    if row_ids is None:
        row_ids = st.session_state["row_id_dict"][eid]
    if config.DISABLE_ROW_SELECTION or not st.session_state["multirow"]:
        return
    if row_id_text not in st.session_state:
        st.session_state[f"select_{row_id_text}_index"] = default

    if prefix is None:
        select_text = "Select row"
    else:
        select_text = f"Select {prefix} row"

    st.sidebar.selectbox(
        select_text,
        row_ids,
        index=st.session_state[f"select_{row_id_text}_index"],
        key=row_id_text,
    )
