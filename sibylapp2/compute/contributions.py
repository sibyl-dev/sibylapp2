import pandas as pd
import streamlit as st

from sibylapp2.compute import api, entities


@st.cache_data(show_spinner="Getting contributions...")
def get_contributions(eids, model_id=api.fetch_model_id()):
    contributions, values = api.fetch_contributions(eids, model_id=model_id)
    return contributions, values


@st.cache_data(show_spinner="Computing contributions...")
def compute_contributions_for_rows(
    eid, row_ids, model_id=api.fetch_model_id(), key="contributions_rows"
):
    contributions = api.fetch_contributions([eid], row_ids, model_id=model_id)
    if key not in st.session_state:
        st.session_state[key] = contributions
    else:
        st.session_state[key] = dict(st.session_state[key], **contributions)
    return contributions


@st.cache_data(show_spinner="Getting contributions...")
def get_contributions_for_rows(eid, row_ids, model_id=api.fetch_model_id()):
    key = f"contributions_rows_{model_id}"
    if key not in st.session_state:
        contributions = compute_contributions_for_rows(eid, row_ids, model_id=model_id, key=key)
    else:
        contributions = st.session_state[key]
    missing_row_ids = list(set(row_ids) - contributions.keys())
    if len(missing_row_ids) > 0:
        contributions = {
            **contributions,
            **compute_contributions_for_rows(eid, missing_row_ids, model_id=model_id, key=key),
        }
    return contributions


@st.cache_data(show_spinner="Getting contributions...")
def get_dataset_contributions(model_id=api.fetch_model_id()):
    if "dataset_eids" not in st.session_state:
        st.session_state["dataset_eids"] = entities.get_eids(1000)
    return get_contributions(st.session_state["dataset_eids"], model_id=model_id)


@st.cache_data(show_spinner="Getting contribution for your data...")
def get_contribution_for_modified_data(eid, changes, row_id=None, model_id=api.fetch_model_id()):
    st.session_state["modified_contribution"] = api.fetch_contribution_for_modified_data(
        eid, changes, row_id=row_id, model_id=model_id
    )
    return st.session_state["modified_contribution"]


@st.cache_data(show_spinner="Getting global contributions...")
def compute_global_contributions(eids, model_id):
    contributions_in_range = get_contributions(eids, model_id=model_id)
    rows = pd.concat(
        [contributions_in_range[eid]["Contribution"] for eid in contributions_in_range],
        axis=1,
    )
    negs = rows[rows <= 0].mean(axis=1).fillna(0)
    poss = rows[rows >= 0].mean(axis=1).fillna(0)
    return pd.concat({"negative": negs, "positive": poss}, axis=1)
