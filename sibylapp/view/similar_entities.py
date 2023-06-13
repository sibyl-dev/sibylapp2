from sibylapp.compute import example_based, context
from sibylapp.view.utils.filtering import process_options
from st_aggrid import AgGrid
import streamlit as st
import pandas as pd


def format_similar_entities(x, y, eid):
    similar_entities = pd.concat([y, x], axis=0)

    feature_info = similar_entities[["Category", "Feature"]]
    similar_entity_info = similar_entities.drop(columns=["Feature", "Category"])
    neighbor_names = [
        "Similar %s #%i" % (context.get_term("Entity"), i)
        for i in range(1, similar_entity_info.shape[1])
    ]
    selected_col_name = "%s %s" % (context.get_term("Entity"), eid)
    similar_entity_info.columns = [selected_col_name] + neighbor_names
    to_show = pd.concat([feature_info, similar_entity_info], axis=1)
    to_show = process_options(to_show)
    to_show = to_show.rename(columns={"Feature": context.get_term("Feature")})

    return to_show, neighbor_names, selected_col_name


def filter_different_rows(to_show, neighbor_names, selected_col_name):
    neighbor_col = to_show[neighbor_names]
    selected_col = to_show[selected_col_name]
    to_show_filtered = to_show[neighbor_col != selected_col]
    return to_show_filtered


def view(eid):
    x, y = example_based.get_similar_entities(eid)
    to_show, neighbor_names, selected_col_name = format_similar_entities(x, y, eid)
    options = ["No filtering"] + neighbor_names
    show_different = st.radio("Apply filtering by differences?", options, horizontal=True)
    if show_different == "No filtering":
        pass
    else:
        to_show = filter_different_rows(to_show, show_different, selected_col_name)
    AgGrid(to_show, fit_columns_on_grid_load=True)
