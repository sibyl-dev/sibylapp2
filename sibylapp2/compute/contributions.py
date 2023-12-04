import pandas as pd
import streamlit as st

from sibylapp2.compute import api, entities
from sibylapp2.config import get_dataset_size


@st.cache_data(show_spinner="Getting contributions...")
def get_contributions(eids, model_id=api.fetch_model_id()):
    contributions, values = api.fetch_contributions(eids, model_id=model_id)
    return contributions, values


@st.cache_data(show_spinner="Getting contributions...")
def get_contributions_for_rows(eid, row_ids, model_id=api.fetch_model_id()):
    contributions, values = api.fetch_contributions([eid], row_ids, model_id=model_id)
    return contributions, values


@st.cache_data(show_spinner="Getting contributions...")
def get_dataset_contributions(model_id=api.fetch_model_id(), all_rows=True):
    if "dataset_eids" not in st.session_state or (
        all_rows and "dataset_row_id_dict" not in st.session_state
    ):
        st.session_state["dataset_eids"], st.session_state["dataset_row_id_dict"] = (
            entities.get_eids(max_entities=1000, return_row_ids=all_rows)
        )
    # confirm at least one entity has more than one row
    if any(len(lst) > 1 for lst in st.session_state["dataset_row_id_dict"].values()):
        all_contributions = []
        all_values = []
        for eid in st.session_state["dataset_eids"]:
            contributions, values = get_contributions_for_rows(
                eid, st.session_state["dataset_row_id_dict"][eid], model_id=model_id
            )
            all_contributions.append(contributions)
            all_values.append(values)
        return pd.concat(all_contributions, axis="rows"), pd.concat(all_values, axis="rows")
    else:
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
