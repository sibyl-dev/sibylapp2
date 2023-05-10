import streamlit as st
from sibylapp import importance, data, contributions, model, api, categories
import numpy as np


st.set_page_config(layout="wide")
st.title("Sibyl")

# Prepping data -----------------------------
X, app = data.get_application("turbines")
format_func = data.get_format_func("turbines")
sample = X.iloc[0:10]
eids = range(0, 2)

# Prepping explanations ---------------------
contribution_results = contributions.compute_contributions(eids)
importance_results = importance.compute_importance(app)

# Prepping predictions -----------------------
predictions = model.predictions(app, sample)

# Sidebar ------------------------------------
sample_options = {
    f"Entity {key} (" + format_func(predictions[key]) + ")": key for key in eids
}
chosen_option = st.sidebar.selectbox("Select an entity", sample_options)
row = sample_options[chosen_option]
pred = predictions[row]
st.sidebar.metric("Prediction", format_func(pred))

# Global options ------------------------------
if "show_more" not in st.session_state:
    st.session_state["show_more"] = False
st.checkbox("Show all features", key="show_more")

exp = st.expander("Search and filter")
with exp:
    search = st.text_input("Search features")
    categories = st.multiselect("Filter by category", categories.get_category_list())


tab1, tab2 = st.tabs(["Feature Contributions", "Feature Importance"])
with tab1:
    contributions.view(contribution_results[row], search, categories)

with tab2:
    importance.view(importance_results, search)
