# pylint: disable=invalid-name

import streamlit as st

from sibylapp2 import config
from sibylapp2.compute import entities, model
from sibylapp2.compute.features import get_feature_description
from sibylapp2.view import explore_feature, feature_contribution
from sibylapp2.view.utils import display, filtering


def get_selected_features(feature_names):
    features = []
    if "changes_to_table_feature_contributions" in st.session_state:
        changes = st.session_state["changes_to_table_feature_contributions"]["edited_rows"]
        for row in changes:
            if "Show feature plot?" in changes[row] and changes[row]["Show feature plot?"]:
                features.append(feature_names.iloc[row])
    return features


def main():
    # Sidebar ------------------------------------
    display.show_probability_select_box()
    filtering.view_model_select()
    filtering.view_selection()
    feature_contribution.view_instructions()

    # Global options ------------------------------
    filtering.view_filtering()

    selected_features = feature_contribution.view(
        st.session_state["eid"],
        st.session_state["model_id"],
        key="feature_contributions",
        row_id=st.session_state["row_id"],
    )
    if selected_features:
        if "dataset_eids" not in st.session_state:
            st.session_state["dataset_eids"] = entities.get_eids(
                max_entities=config.get_dataset_size()
            )
        predictions = model.get_dataset_predictions(st.session_state["model_id"])
        for selected_feature in selected_features:
            discrete = config.PREDICTION_TYPE in (
                config.PredType.BOOLEAN,
                config.PredType.CATEGORICAL,
            )
            st.subheader(get_feature_description(selected_feature))
            explore_feature.view(
                st.session_state["dataset_eids"],
                predictions,
                selected_feature,
                st.session_state["model_id"],
                one_line=True,
                discrete=discrete,
            )
