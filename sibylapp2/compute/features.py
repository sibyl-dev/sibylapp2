from __future__ import annotations

import pandas as pd
import streamlit as st

from sibylapp2.compute import api


@st.cache_data(show_spinner="Fetching data...")
def get_features(include_type=False, include_values=False):
    columns = ["Category", "Feature"]
    if include_type:
        columns.append("Type")
    if include_values:
        columns.append("Values")
    features = api.fetch_features()[columns]
    return features


@st.cache_data(show_spinner="Fetching data...")
def get_feature_description(feature: str):
    feature_description = get_features().loc[feature, "Feature"]
    return feature_description


@st.cache_data(show_spinner="Fetching data...")
def get_entity(eid: str, row_id: str | None = None):
    feature_values = api.fetch_entity(eid, row_id)
    return feature_values


@st.cache_data(show_spinner="Fetching categorical values...")
def get_categorical_values():
    features_df = get_features(include_type=True, include_values=True)
    features_df = features_df[features_df["Type"] == "categorical"]
    feature_value_dict = dict(zip(features_df.index, features_df["Values"]))
    return feature_value_dict


def get_categories():
    return api.fetch_categories()["name"].tolist()
