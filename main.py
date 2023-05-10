import streamlit as st
from sibylapp import importance, contributions, model, api, categories, config


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
def format_func(s):
    return str(s)

eids = api.fetch_eids()
if config.MAX_ENTITIES is not None:
    eids = eids[:config.MAX_ENTITIES]

# Prepping explanations ---------------------
contribution_results = contributions.compute_contributions(eids)
importance_results = importance.compute_importance()

# Prepping predictions -----------------------
predictions = model.predictions(eids)

# Sidebar ------------------------------------
sample_options = {
    f"Entity {key} (" + format_func(predictions[key]) + ")": key for key in eids
}
chosen_option = st.sidebar.selectbox("Select an entity", sample_options)
row = sample_options[chosen_option]
pred = predictions[row]
st.sidebar.metric("Prediction", format_func(pred))

# Global options ------------------------------
st.checkbox("Show all features", key="show_more")

exp = st.expander("Search and filter")
with exp:
    st.session_state["search_term"] = st.text_input("Search features")
    st.session_state["filters"] = st.multiselect("Filter by category", categories.get_category_list())


tab1, tab2 = st.tabs(["Feature Contributions", "Feature Importance"])
with tab1:
    contributions.view(contribution_results[row])

with tab2:
    importance.view(importance_results)
