from __future__ import annotations

import pandas as pd
import streamlit as st
from sibylapp2.compute.context import get_term

from sibylapp2.compute import api


@st.cache_data(show_spinner="Fetching data...")
def get_features() -> pd.DataFrame:
    features = api.fetch_features()[["Feature", "Category"]]
    return features


@st.cache_data(show_spinner="Fetching data...")
def get_entity(eid: str, row_id: str | None = None) -> pd.Series:
    feature_values = api.fetch_entity(eid, row_id)
    return feature_values


@st.cache_data(show_spinner="Fetching data...")
def get_options_for_categories(
    entities: list[str], features_df: pd.DataFrame
) -> dict[str, list[str | int | float]]:
    """
    This function should be replaced when API call for options of non numeric
    variables is implemented. This function currently iterates through all
    entities in `dataset_eids` to generate options.
    """
    options = {}
    # each column is an entity
    dataset = pd.concat([get_entity(eid) for eid in entities], axis=1)
    for feature in dataset.index:
        if features_df.loc[feature, "type"] != "numeric":
            options[feature] = pd.unique(dataset.loc[feature, :]).tolist()
    return options
