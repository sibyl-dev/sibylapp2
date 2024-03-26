# pylint: disable=invalid-name

import streamlit as st

from sibylapp2.view import similar_entities, filtering, sidebar
from sibylapp2.compute.context import get_term


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "The **Similar Cases** page shows the two {entities} from the training dataset with"
            " the most similar {feature} values. Rows where a similar {entity} has a"
            " different value are highlighted.".format(
                entities=get_term("entity", plural=True),
                feature=get_term("feature"),
                entity=get_term("entity"),
            )
        )


def main():
    # Sidebar ------------------------------------
    sidebar.set_up_sidebar(model_select=True, entity_select=True, row_select=True, prediction=True)

    similar_entities.view(st.session_state["eid"], model_id=st.session_state["model_id"])
