import streamlit as st
from sibylapp import contributions, model, config, filtering, setup
from sibylapp.context import get_term

setup.setup_page()

# Sidebar ------------------------------------
predictions = model.get_predictions(st.session_state["eids"])
sample_options = {
    f"{get_term('Entity')} {key} ("
    + config.pred_format_func(predictions[key])
    + ")": key
    for key in st.session_state["eids"]
}

chosen_option = st.sidebar.selectbox("Select %s" % get_term("Entity"), sample_options)
eid = sample_options[chosen_option]
pred = predictions[eid]
st.sidebar.metric(get_term("Prediction"), config.pred_format_func(pred))

# Global options ------------------------------
filtering.view()


(tab1,) = st.tabs(
    [
        get_term("Feature Contributions"),
    ]
)
with tab1:
    contributions.view(eid)
