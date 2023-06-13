from sibylapp.compute import example_based, context
from sibylapp.view.utils.filtering import process_options
from st_aggrid import AgGrid
import streamlit as st
import pandas as pd


def view(eid):
    similar_entities = example_based.get_similar_entities(eid)
    feature_info = similar_entities[["Category", "Feature"]]
    similar_entity_info = similar_entities.drop(columns=["Feature", "Category"])
    similar_entity_info.columns = [
        "Similar %s #%i" % (context.get_term("Entity"), i)
        for i in range(1, similar_entity_info.shape[1] + 1)
    ]
    to_show = pd.concat([feature_info, similar_entity_info], axis=1)
    to_show = process_options(to_show)
    to_show = to_show.rename(columns={"Feature": context.get_term("Feature")})
    AgGrid(to_show, fit_columns_on_grid_load=True)
