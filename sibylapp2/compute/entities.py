import streamlit as st

from sibylapp2.compute import api


@st.cache_data(show_spinner="Fetching data...")
def get_eids(
    max_entities=None,
    return_row_ids=False,
    defaults=None,
):
    """
    Returns:
        eids: list[str]
        row_id_dict (only if return_row_ids=True): dict[str, list[int]]
    """
    entities = api.fetch_eids()
    if defaults is not None:
        entities = [entry for entry in entities if entry["eid"] in defaults]
    elif max_entities is not None:
        entities = entities[:max_entities]

    if return_row_ids:
        return [entry["eid"] for entry in entities], {
            entry["eid"]: entry["row_ids"] for entry in entities
        }
    else:
        return [entry["eid"] for entry in entities]
