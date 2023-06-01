import streamlit as st
from sibylapp import importance, filtering, explore_feature, entities, config
from sibylapp.context import get_term

st.set_page_config(layout="wide")
st.title("Sibyl")

# Prepping data -----------------------------
if "eids" not in st.session_state:
    st.session_state["eids"] = entities.get_eids(max_entities=config.MAX_ENTITIES)


# Prepping explanations ---------------------
importance_results = importance.compute_importance()


# Global options ------------------------------
filtering.view()


tab1, tab2 = st.tabs(
    [get_term("Feature Importance"), "Explore a %s" % get_term("Feature")]
)
with tab1:
    features = importance.view(importance_results)

with tab2:
    explore_feature.view(features)
