import streamlit as st
from sibylapp.compute import api, entities


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


@st.cache_data(show_spinner="Getting contributions...")
def get_contributions(eids):
    if "contributions" not in st.session_state:
        compute_contributions(eids)
    missing_eids = list(set(eids) - st.session_state["contributions"].keys())
    if len(missing_eids) > 0:
        compute_contributions(missing_eids)
    return {eid: st.session_state["contributions"][eid] for eid in eids}


@st.cache_data(show_spinner="Getting contributions...")
def get_dataset_contributions():
    if "dataset_eids" not in st.session_state:
        st.session_state["dataset_eids"] = entities.get_eids(1000)
    return get_contributions(st.session_state["dataset_eids"])
