import pandas as pd
import streamlit as st

from sibylapp2.compute import api, entities


@st.cache_data(show_spinner="Getting contributions...")
def get_contributions(eids, model_id=api.fetch_model_id()):
    contributions, values = api.fetch_contributions(eids, model_id=model_id)
    return contributions, values


@st.cache_data(show_spinner="Getting contributions...")
def get_contributions_for_rows(eid, row_ids, model_id=api.fetch_model_id()):
    contributions, values = api.fetch_contributions([eid], row_ids, model_id=model_id)
    return contributions, values


@st.cache_data(show_spinner="Getting contributions...")
def get_dataset_contributions(model_id=api.fetch_model_id()):
    if "dataset_eids" not in st.session_state:
        st.session_state["dataset_eids"] = entities.get_eids(1000)
    return get_contributions(st.session_state["dataset_eids"], model_id=model_id)


@st.cache_data(show_spinner="Getting contribution for your data...")
def get_contribution_for_modified_data(eid, changes, row_id=None, model_id=api.fetch_model_id()):
    return api.fetch_contribution_for_modified_data(eid, changes, row_id=row_id, model_id=model_id)


@st.cache_data(show_spinner="Getting global contributions...")
def compute_global_contributions(eids, model_id):
    contributions_in_range, _ = get_contributions(eids, model_id=model_id)
    contributions_in_range = contributions_in_range.T
    negs = contributions_in_range[contributions_in_range <= 0].mean(axis=1).fillna(0)
    poss = contributions_in_range[contributions_in_range >= 0].mean(axis=1).fillna(0)
    return pd.concat({"negative": negs, "positive": poss}, axis=1)
