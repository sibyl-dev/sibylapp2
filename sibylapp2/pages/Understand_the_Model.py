# pylint: disable=invalid-name

import extra_streamlit_components as stx
import streamlit as st

from sibylapp2 import config
from sibylapp2.compute import contributions, features, model
from sibylapp2.compute.context import get_term
from sibylapp2.view import explore_feature, feature_importance, global_contributions
from sibylapp2.view.utils import filtering, setup


def main():
    # Global options ------------------------------
    filtering.view_model_select()
    filtering.view_filtering()

    # Compute -------------------------------------
    predictions = model.get_dataset_predictions(st.session_state["model_id"])
    discrete = config.PREDICTION_TYPE in (config.PredType.BOOLEAN, config.PredType.CATEGORICAL)

    all_contributions, all_values = contributions.get_dataset_contributions(
        st.session_state["model_id"]
    )

    # Setup tabs ----------------------------------
    pred_filter_container = st.container()

    tab = stx.tab_bar(
        data=[
            stx.TabBarItemData(
                id=1, title=get_term(f"{get_term('Feature')} Importance"), description=""
            ),
            stx.TabBarItemData(
                id=2,
                title="Global %s" % get_term(f"{get_term('Feature')} Contributions"),
                description="",
            ),
            stx.TabBarItemData(id=4, title="Explore a %s" % get_term("Feature"), description=""),
        ],
        default=1,
    )

    # Sidebar --------------------------------------
    if tab == "1":
        feature_importance.view_instructions()

    if tab == "2":
        global_contributions.view_instructions()

    if tab == "4":
        explore_feature.view_instructions()

    st.session_state["disabled"] = tab == "1"

    # Prediction filtering -------------------------
    with pred_filter_container:
        if "disabled" not in st.session_state:
            st.session_state["disabled"] = True
        eids = filtering.view_prediction_selection(
            predictions, disabled=st.session_state["disabled"]
        )

    placeholder = st.container()
    features_values = features.get_features()

    if tab == "1":
        with placeholder:
            feature_importance.view()

    if tab == "2":
        with placeholder:
            if len(eids) == 0:
                st.warning("Select predictions above to see explanation!")
            else:
                global_contributions.view(eids, st.session_state["model_id"])

    if tab == "4":
        with placeholder:
            if len(eids) == 0:
                st.warning("Select predictions above to see explanation!")
            else:
                feature = st.selectbox(
                    "Select a %s" % get_term("feature"),
                    filtering.process_search_on_features(features_values),
                )
                explore_feature.view(
                    eids, predictions, feature, st.session_state["model_id"], discrete
                )
