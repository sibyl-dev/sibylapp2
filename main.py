import streamlit as st
import pandas as pd
import numpy as np
from pyreal.sample_applications import ames_housing

st.set_page_config(layout="wide")

X, y = ames_housing.load_data(include_targets=True)
app = ames_housing.load_app()
sample = X.iloc[0:10]

if 'show_more' not in st.session_state:
    st.session_state['show_more'] = False

exp = st.expander("Search and filter")
with exp:
    search = st.text_input("Search features")


row = st.sidebar.selectbox("Select a house", sample.index)
sort_by = st.sidebar.radio("Sort order", ["Absolute", "Ascending", "Descending", "Side-by-side"])

explanation = app.produce_feature_contributions(sample)

to_show = explanation[row]
to_show["Contribution Value"] = to_show["Contribution"]
to_show.drop("Average/Mode", axis="columns", inplace=True)
to_show.set_index("Feature Name", inplace=True)
length = 10
num_to_show = to_show["Contribution"] / max(to_show["Contribution"].abs()) * length
num_to_show = num_to_show.astype("int")
to_show["Contribution"] = [("🟦" * n + "⬜"*(length-n) + "⬆") if n > 0 else ("⬇" + "⬜"*(length+n) + "🟥"*-n) for n in num_to_show]

st.checkbox("Show all features", key="show_more")

if sort_by == "Side-by-side":
    col1, col2 = st.columns(2)
    with col1:
        to_show_neg = to_show[to_show["Contribution Value"] < 0].sort_values(
            by="Contribution", axis="index")
        if search is not None:
            to_show_neg = to_show_neg[to_show_neg.index.str.contains(search, case=False)]
        st.table(to_show_neg.drop("Contribution Value", axis="columns"))
    with col2:
        to_show_pos = to_show[to_show["Contribution Value"] >= 0].sort_values(
            by="Contribution", axis="index", ascending=False)
        if search is not None:
            to_show_pos = to_show_pos[to_show_pos.index.str.contains(search, case=False)]
        st.table(to_show_pos.drop("Contribution Value", axis="columns"))
else:
    if sort_by == "Absolute":
        to_show = to_show.reindex(to_show['Contribution Value'].abs().sort_values(ascending=False).index)
    if sort_by == "Ascending":
        to_show = to_show.sort_values(by="Contribution Value", axis="index")
    if sort_by == "Descending":
        to_show = to_show.sort_values(by="Contribution Value", axis="index", ascending=False)
    if not st.session_state['show_more']:
        to_show = to_show[0:10]
    if search is not None:
        to_show = to_show[to_show.index.str.contains(search, case=False)]
    st.table(to_show.drop("Contribution Value", axis="columns"))
