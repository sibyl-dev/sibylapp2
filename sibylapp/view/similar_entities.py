import pandas as pd
import streamlit as st

from sibylapp.compute import example_based
from sibylapp.compute.context import get_term
from sibylapp.view.utils import helpers
from sibylapp.view.utils.filtering import process_options


def format_similar_entities(x, y):
    similar_entities = pd.concat([y, x], axis=0)

    feature_info = similar_entities[["Category", "Feature"]]
    similar_entity_info = similar_entities.drop(columns=["Feature", "Category"]).iloc[:, :3]
    neighbor_names = [
        "Similar %s #%i" % (get_term("Entity"), i) for i in range(1, similar_entity_info.shape[1])
    ]
    selected_col_name = "Selected"
    similar_entity_info.columns = [selected_col_name] + neighbor_names
    to_show = pd.concat([feature_info, similar_entity_info], axis=1)
    to_show = process_options(to_show)

    return to_show, neighbor_names, selected_col_name


def filter_different_rows(to_show, neighbor_names, selected_col_name):
    neighbor_col = to_show[neighbor_names]
    selected_col = to_show[selected_col_name]
    to_show_filtered = to_show[neighbor_col != selected_col]
    return to_show_filtered


def view(eid):
    x, y = example_based.get_similar_entities(eid)
    y.index = ["y"]  # Used to prevent bug in data_editor where index is assumed to be numeric
    to_show, neighbor_names, selected_col_name = format_similar_entities(x, y)
    options = ["No filtering"] + neighbor_names
    show_different = st.radio(
        "Apply filtering by differences?",
        options,
        horizontal=True,
        help="Show only rows where value differs from selected",
    )
    if show_different == "No filtering":
        pass
    else:
        to_show = filter_different_rows(to_show, show_different, selected_col_name)

    helpers.show_table(to_show, "similar_entities")


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "The **Similar Cases** page shows the two {entities} from the training dataset with"
            " the most similar {feature} values. Rows where a similar {entity} has a"
            " different value are highlighted.".format(
                entities=get_term("Entity", plural=True, lower=True),
                feature=get_term("Feature", lower=True),
                entity=get_term("Entity", lower=True),
            )
        )
