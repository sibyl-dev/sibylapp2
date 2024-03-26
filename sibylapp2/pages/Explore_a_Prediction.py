# pylint: disable=invalid-name

import streamlit as st

from sibylapp2.compute.context import get_term
from sibylapp2.view import feature_contribution, filtering, sidebar, helpers
from sibylapp2 import config
from sibylapp2.compute import entities, model
from sibylapp2.compute.features import get_feature_description
from sibylapp2.view import explore_feature, feature_contribution
from sibylapp2.view.utils import display


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "**{feature_contributions}** refer to the positive or negative affect a specific"
            " feature value had on the model's prediction.".format(
                feature_contributions=get_term("Feature Contributions")
            )
        )
        positive, negative = helpers.get_pos_neg_names()
        st.markdown(
            "A large **{positive}** bar means that this {feature}'s value significantly increased"
            " the model's prediction on this {entity}. A large **{negative}** bar means that this"
            " {feature}'s value significantly decreased the model's prediction. A lack of a"
            " bar suggests this {feature} had little effect on the model's prediction in this"
            " case.".format(
                positive=positive,
                negative=negative,
                feature=get_term("feature"),
                entity=get_term("entity"),
            )
        )
        st.markdown(
            "You can select {a_entity} from the dropdown above, and see the {feature}"
            " contributions. You can also **filter** and **search** the {feature} table or adjust"
            " the **sort order**.".format(
                a_entity=get_term("entity", with_a=True),
                feature=get_term("feature"),
            )
        )


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
    sidebar.set_up_sidebar(
        model_select=True,
        entity_select=True,
        row_select=True,
        prediction=True,
        probability_select=True,
    )
    view_instructions()

    # # Global options ------------------------------
    filtering.view_filtering()

    selected_features = feature_contribution.view(
        st.session_state["eid"],
        st.session_state["model_id"],
        key="feature_contributions",
        row_id=st.session_state.get("row_id", None),
        include_feature_plot=True,
    )
    if selected_features:
        if "dataset_eids" not in st.session_state:
            st.session_state["dataset_eids"] = entities.get_eids(
                max_entities=config.get_dataset_size()
            )
        predictions = model.get_dataset_predictions(st.session_state["model_id"])
        discrete = config.PREDICTION_TYPE in (
            config.PredType.BOOLEAN,
            config.PredType.CATEGORICAL,
        )
        for selected_feature in selected_features:
            st.subheader(get_feature_description(selected_feature))
            explore_feature.view(
                st.session_state["dataset_eids"],
                predictions,
                selected_feature,
                st.session_state["model_id"],
                one_line=True,
                discrete=discrete,
            )
