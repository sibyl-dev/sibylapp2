import streamlit as st
from sibylapp import importance, contributions, model, context, config, entities
from sibylapp.context import get_term


st.set_page_config(layout="wide")
st.title("Sibyl")

# Fill session storage
if "show_more" not in st.session_state:
    st.session_state["show_more"] = False
if "search_term" not in st.session_state:
    st.session_state["search_term"] = None
if "filters" not in st.session_state:
    st.session_state["filters"] = []

# Prepping data -----------------------------
eids = entities.get_eids(max_entities=config.MAX_ENTITIES)

# Prepping explanations ---------------------
contribution_results = contributions.compute_contributions(eids)
importance_results = importance.compute_importance()

# Prepping predictions -----------------------
predictions = model.predictions(eids)

# Sidebar ------------------------------------
sample_options = {
    f"{get_term('Entity')} {key} ("
    + config.pred_format_func(predictions[key])
    + ")": key
    for key in eids
}

chosen_option = st.sidebar.selectbox("Select %s" % get_term("Entity"), sample_options)
row = sample_options[chosen_option]
pred = predictions[row]
st.sidebar.metric(get_term("Prediction"), config.pred_format_func(pred))

# Global options ------------------------------
st.checkbox("Show all", key="show_more")

exp = st.expander("Search and filter")
with exp:
    st.session_state["search_term"] = st.text_input(
        "Search by %s" % get_term("Feature").lower()
    )
    st.session_state["filters"] = st.multiselect(
        "Filter by category", context.get_category_list()
    )


tab1, tab2 = st.tabs(
    [get_term("Feature Contributions"), get_term("Feature Importance")]
)
with tab1:
    contributions.view(contribution_results[row])

with tab2:
    importance.view(importance_results)
