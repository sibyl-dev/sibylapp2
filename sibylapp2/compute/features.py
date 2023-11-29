from __future__ import annotations

import pandas as pd
import streamlit as st

from sibylapp2.compute import api


@st.cache_data(show_spinner="Fetching data...")
def get_features(include_type=False) -> pd.DataFrame:
    columns = ["Category", "Feature"]
    if include_type:
        columns.append("Type")
    features = api.fetch_features()[columns]
    return features


@st.cache_data(show_spinner="Fetching data...")
def get_entity(eid: str, row_id: str | None = None) -> pd.Series:
    feature_values = api.fetch_entity(eid, row_id)
    return feature_values


@st.cache_data(show_spinner="Fetching data...")
def get_options_for_categories(entities: list[str]) -> dict[str, list[str | int | float]]:
    """
    This function should be replaced when API call for options of non-numeric
    variables is implemented. This function currently iterates through all
    entities in `dataset_eids` to generate options.
    """
    options = {}
    # each column is an entity
    dataset = pd.concat([get_entity(eid) for eid in entities], axis=1)
    for feature in dataset.index:
        if get_features(include_type=True).loc[feature, "Type"] != "numeric":
            options[feature] = pd.unique(dataset.loc[feature, :]).tolist()
    return options
