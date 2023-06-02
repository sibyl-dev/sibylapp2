import streamlit as st
from sibylapp.compute import api


@st.cache_data(show_spinner="Computing contribution scores...")
def compute_contributions(eids):
    contributions = api.fetch_contributions(eids)
    if "contributions" not in st.session_state:
        st.session_state["contributions"] = contributions
    else:
        st.session_state["contributions"] = dict(
            st.session_state["contributions"], **contributions
        )
    return contributions


def get_contributions(eids):
    if "contributions" not in st.session_state:
        compute_contributions(eids)
    missing_eids = list(set(eids) - st.session_state["contributions"].keys())
    if len(missing_eids) > 0:
        compute_contributions(missing_eids)
    return {eid: st.session_state["contributions"][eid] for eid in eids}
