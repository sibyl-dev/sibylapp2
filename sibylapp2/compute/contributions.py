import pandas as pd
import streamlit as st

from sibylapp2.compute import api, entities


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
        contributions = compute_contributions(eids)
    else:
        contributions = st.session_state["contributions"]
    missing_eids = list(set(eids) - contributions.keys())
    if len(missing_eids) > 0:
        contributions = {**contributions, **compute_contributions(missing_eids)}
    return {eid: contributions[eid] for eid in eids}


@st.cache_data(show_spinner="Computing contributions...")
def compute_contributions_for_rows(eid, row_ids):
    contributions = api.fetch_contributions([eid], row_ids)
    if "contributions_rows" not in st.session_state:
        st.session_state["contributions_rows"] = contributions
    else:
        st.session_state["contributions_rows"] = dict(
            st.session_state["contributions_rows"], **contributions
        )
    return contributions


@st.cache_data(show_spinner="Getting contributions...")
def get_contributions_for_rows(eid, row_ids):
    if "contributions_rows" not in st.session_state:
        contributions = compute_contributions_for_rows(eid, row_ids)
    else:
        contributions = st.session_state["contributions_rows"]
    missing_row_ids = list(set(row_ids) - contributions.keys())
    if len(missing_row_ids) > 0:
        contributions = {**contributions, **compute_contributions_for_rows(eid, missing_row_ids)}
    return contributions


@st.cache_data(show_spinner="Getting contributions...")
def get_dataset_contributions():
    if "dataset_eids" not in st.session_state:
        st.session_state["dataset_eids"] = entities.get_eids(1000)
    return get_contributions(st.session_state["dataset_eids"])


@st.cache_data(show_spinner="Getting contribution for your data...")
def get_contribution_for_modified_data(eid, changes, row_id=None):
    st.session_state["modified_contribution"] = api.fetch_contribution_for_modified_data(
        eid, changes, row_id=row_id
    )
    return st.session_state["modified_contribution"]


@st.cache_data(show_spinner="Getting global contributions...")
def compute_global_contributions(eids):
    contributions_in_range = get_contributions(eids)
    rows = pd.concat(
        [contributions_in_range[eid]["Contribution"] for eid in contributions_in_range],
        axis=1,
    )
    negs = rows[rows <= 0].mean(axis=1).fillna(0)
    poss = rows[rows >= 0].mean(axis=1).fillna(0)
    return pd.concat({"negative": negs, "positive": poss}, axis=1)
