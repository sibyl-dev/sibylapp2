import streamlit as st
import numpy as np
import data
import contributions


def process_show_more(to_show_, show_more_):
    if not show_more_:
        return to_show_[0:10]
    return to_show_


def process_search(to_show_, search_):
    if search is not None:
        to_show_ = to_show_[to_show_.index.str.contains(search_, case=False)]
    return to_show_


st.set_page_config(layout="wide")
st.title("Sibyl")

# Configurations ----------------------------
BAR_LENGTH = 8

# Prepping data -----------------------------
X, app, format_func = data.get_application("housing")
sample = X.iloc[0:10]

# Prepping contributions ---------------------
contributions = contributions.setup_contributions(app, sample, BAR_LENGTH)

# Prepping importance ------------------------


# Prepping predictions -----------------------
predictions = app.predict(sample)

# Sidebar ------------------------------------
sample_options = {f'Entity {key} (' + format_func(predictions[key]) + ')': key for key in sample.index}
chosen_option = st.sidebar.selectbox("Select an entity", sample_options)
row = sample_options[chosen_option]
pred = predictions[row]
st.sidebar.metric("Prediction", format_func(pred))

# Global options ------------------------------
if 'show_more' not in st.session_state:
    st.session_state['show_more'] = False
st.checkbox("Show all features", key="show_more")

exp = st.expander("Search and filter")
with exp:
    search = st.text_input("Search features")
    categories = st.multiselect("Filter by category", ["C1", "C2", "C3"])


tab1, tab2 = st.tabs(["Feature Contributions", "Feature Importance"])
with tab1:
    sort_by = st.selectbox("Sort order", ["Absolute", "Ascending", "Descending", "Side-by-side"])

    to_show = contributions[row]

    if sort_by == "Side-by-side":
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Negative features")
            to_show_neg = to_show[to_show["Contribution Value"] < 0].sort_values(
                by="Contribution", axis="index", ascending=False)
            to_show_neg = process_search(process_show_more(
                to_show_neg, st.session_state['show_more']), search)
            st.table(to_show_neg.drop("Contribution Value", axis="columns"))
        with col2:
            st.subheader("Positive features")
            to_show_pos = to_show[to_show["Contribution Value"] >= 0].sort_values(
                by="Contribution", axis="index", ascending=False)
            to_show_pos = process_search(process_show_more(
                to_show_pos, st.session_state['show_more']), search)
            st.table(to_show_pos.drop("Contribution Value", axis="columns"))
    else:
        if sort_by == "Absolute":
            to_show = to_show.reindex(to_show['Contribution Value'].abs().sort_values(ascending=False).index)
        if sort_by == "Ascending":
            to_show = to_show.sort_values(by="Contribution Value", axis="index")
        if sort_by == "Descending":
            to_show = to_show.sort_values(by="Contribution Value", axis="index", ascending=False)
        to_show = process_search(process_show_more(
            to_show, st.session_state['show_more']), search)
        st.table(to_show.drop("Contribution Value", axis="columns"))

with tab2:
    to_show = importance.copy()
    to_show = to_show.sort_values(by="Importance Value", axis="index", ascending=False)
    to_show = process_search(process_show_more(
        to_show, st.session_state['show_more']), search)
    st.table(to_show.drop("Importance Value", axis="columns"))


