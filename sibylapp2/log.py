from time import time

import streamlit as st

from sibylapp2.compute.api import log as api_log
from sibylapp2.config import ENABLE_LOGGING


def log(
    timestamp=None,
    user_id=None,
    eid=None,
    action=None,
    element=None,
    details=None,
    interface=None,
):
    """
    Log an action in the system
    Args:
        timestamp (int):
            Time of the action. If not provided, current time is used.
        user_id (str):
            ID of the user that took the action
        eid (str):
            Entity ID the action was taken on
        action (str):
            Action taken
        element (str):
            Element the action was taken on
        details (dict):
            Details of the action
        interface (str):
            Interface the action was taken on
    """
    if not ENABLE_LOGGING:
        return
    if timestamp is None:
        timestamp = int(time())
    if interface is None and "page_selected" in st.session_state:
        interface = st.session_state["page_selected"]
    if eid is None and "eid" in st.session_state:
        eid = st.session_state["eid"]
    api_log(
        timestamp=timestamp,
        user_id=user_id,
        eid=eid,
        action=action,
        element=element,
        details=details,
        interface=interface,
    )
