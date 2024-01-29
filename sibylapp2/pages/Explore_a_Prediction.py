# pylint: disable=invalid-name

import extra_streamlit_components as stx
import streamlit as st

from sibylapp2.compute.context import get_term
from sibylapp2.view import feature_contribution, filtering, sidebar, helpers


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


def main():
    # Sidebar ------------------------------------
    sidebar.set_up_sidebar(
        model_select=True,
        entity_select=True,
        row_select=True,
        prediction=True,
        probability_select=True,
    )
    # sidebar.show_probability_select_box()
    # sidebar.view_model_select()
    # sidebar.view_entity_and_row_select()
    view_instructions()

    # Global options ------------------------------
    filtering.view_filtering()

    feature_contribution.view(
        st.session_state["eid"],
        st.session_state["model_id"],
        key="feature_contributions",
        row_id=st.session_state["row_id"],
    )
