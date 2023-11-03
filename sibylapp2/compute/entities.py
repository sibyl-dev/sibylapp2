import streamlit as st

from sibylapp2.compute import api


@st.cache_data(show_spinner="Fetching data...")
def get_eids(max_entities=None, return_row_ids=False):
    if return_row_ids:
        eids, row_id_dict = api.fetch_eids(return_row_ids=True)
    else:
        eids = api.fetch_eids()
    if max_entities is not None:
        eids = eids[:max_entities]
    if return_row_ids:
        return eids, row_id_dict
    else:
        return eids
