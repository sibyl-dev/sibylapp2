import streamlit as st
import pandas as pd
from sibylapp.compute import contributions, api
from sklearn.neighbors import KDTree


@st.cache_data(show_spinner="Fetching data...")
def get_data():
    # TODO: switch this out for values only once value fetching is optimized
    data = contributions.get_dataset_contributions()
    values = pd.concat(
        [data[eid]["Feature Value"] for eid in data],
        axis=1
    ).T
    values.index = data.keys()
    return values


@st.cache_data(show_spinner="Fitting nearest neighbor explainer...")
def get_explainer():
    return KDTree(get_data())


def get_similar_entities(eid):
    eid_values = api.fetch_entity(eid).to_frame().T
    neighbor_inds = get_explainer().query(eid_values, k=4, return_distance=False)
    neighbors = get_data().iloc[neighbor_inds[0], :]
    if eid in neighbors.index:
       neighbors = neighbors.drop(index=eid)
    st.dataframe(neighbors.T, use_container_width=True)


def view(eid):
    get_similar_entities(eid)