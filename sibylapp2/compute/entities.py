import streamlit as st

from sibylapp2.compute import api


@st.cache_data(show_spinner="Fetching data...")
def get_eids(
    max_entities=None,
    return_row_ids=False,
):
    """
    Returns:
        eids: list[str]
        row_id_dict (only if return_row_ids=True): dict[str, list[int]]
    """
    if return_row_ids:
        return api.fetch_eids(return_row_ids=True, max_entities=max_entities)
    else:
        return api.fetch_eids(max_entities=max_entities)
