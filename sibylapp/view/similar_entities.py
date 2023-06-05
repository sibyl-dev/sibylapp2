import streamlit as st
import pandas as pd
from sibylapp.compute import contributions


def get_similar_entities(eid):
    # TODO: switch this out for values only once value fetching is optimized
    data = contributions.get_contributions(st.session_state["dataset_eids"])
    eid_values = data[eid][["Feature Name", "Feature Value"]]

    values = pd.concat(
        [data[eid]["Feature Value"] for eid in data],
        axis=1
    ).T
    values.index = data.keys()
    st.table(values)


def view(eid):
    get_similar_entities(eid)