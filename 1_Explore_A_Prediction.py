import streamlit as st
from sibylapp import contributions, model, config, entities, filtering
from sibylapp.context import get_term

st.set_page_config(layout="wide")
st.title("Sibyl")

# Prepping data -----------------------------
if "eids" not in st.session_state:
    st.session_state["eids"] = entities.get_eids(max_entities=config.MAX_ENTITIES)

# Prepping explanations ---------------------
contribution_results = contributions.compute_contributions(st.session_state["eids"])

# Prepping predictions -----------------------
if "predictions" not in st.session_state:
    st.session_state["predictions"] = model.predictions(st.session_state["eids"])

# Sidebar ------------------------------------
sample_options = {
    f"{get_term('Entity')} {key} ("
    + config.pred_format_func(st.session_state["predictions"][key])
    + ")": key
    for key in st.session_state["eids"]
}

chosen_option = st.sidebar.selectbox("Select %s" % get_term("Entity"), sample_options)
row = sample_options[chosen_option]
pred = st.session_state["predictions"][row]
st.sidebar.metric(get_term("Prediction"), config.pred_format_func(pred))

# Global options ------------------------------
filtering.view()


(tab1,) = st.tabs(
    [
        get_term("Feature Contributions"),
    ]
)
with tab1:
    contributions.view(contribution_results[row])
