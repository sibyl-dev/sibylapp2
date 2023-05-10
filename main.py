import streamlit as st
from sibylapp import importance, data, contributions, model


st.set_page_config(layout="wide")
st.title("Sibyl")

# Prepping data -----------------------------
X, app, format_func = data.get_application("housing")
sample = X.iloc[0:10]

# Prepping explanations ---------------------
contribution_results = contributions.compute_contributions(app, sample)
importance_results = importance.compute_importance(app)

# Prepping predictions -----------------------
predictions = model.predictions(app, sample)

# Sidebar ------------------------------------
sample_options = {
    f"Entity {key} (" + format_func(predictions[key]) + ")": key for key in sample.index
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
    categories = st.multiselect("Filter by category", ["C1", "C2", "C3"])


tab1, tab2 = st.tabs(["Feature Contributions", "Feature Importance"])
with tab1:
    contributions.view(contribution_results[row], search)

with tab2:
    importance.view(importance_results, search)
