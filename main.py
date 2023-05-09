import streamlit as st
import pandas as pd
import numpy as np
from pyreal.sample_applications import ames_housing

st.set_page_config(layout="wide")

X, y = ames_housing.load_data(include_targets=True)
app = ames_housing.load_app()
sample = X.iloc[0:10]

emoji_length = 8

explanations = app.produce_feature_contributions(sample)
importance = app.produce_feature_importance()
importance.set_index("Feature Name", inplace=True)
importance["Importance Value"] = importance["Importance"]
num_to_show = importance["Importance Value"] / max(importance["Importance Value"].abs()) * emoji_length
num_to_show = num_to_show.apply(np.ceil).astype("int")
importance["Importance"] = [("🟪" * n + "⬜" * (emoji_length - n) + "⬆") for n in num_to_show]
predictions = app.predict(sample)
average_pred = np.average(list(predictions.values()))

sample_options = {f'House {key} (${predictions[key]:,.2f})' : key for key in sample.index}

chosen_option = st.sidebar.selectbox("Select a house", sample_options)
row = sample_options[chosen_option]

st.title("Sibyl")

pred = predictions[row]
st.sidebar.metric("Predicted price", f'${pred:,.2f}', delta=f'{(pred-average_pred):,.2f}')

if 'show_more' not in st.session_state:
    st.session_state['show_more'] = False

st.checkbox("Show all features", key="show_more")
exp = st.expander("Search and filter")
with exp:
    search = st.text_input("Search features")
    categories = st.multiselect("Filter by category", ["C1", "C2", "C3"])

tab1, tab2 = st.tabs(["Feature Contributions", "Feature Importance"])
with tab1:
    sort_by = st.selectbox("Sort order",
                               ["Absolute", "Ascending", "Descending", "Side-by-side"])

    to_show = explanations[row]
    to_show["Contribution Value"] = to_show["Contribution"]
    to_show.drop("Average/Mode", axis="columns", inplace=True)
    to_show.set_index("Feature Name", inplace=True)
    num_to_show = to_show["Contribution"] / max(to_show["Contribution"].abs()) * emoji_length
    num_to_show = num_to_show.apply(np.ceil).astype("int")
    to_show["Contribution"] = [("🟦" * n + "⬜" * (emoji_length - n) + "⬆") if n > 0 else ("⬇" + "⬜" * (emoji_length + n) + "🟥" * -n) for n in num_to_show]

    if sort_by == "Side-by-side":
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Negative features")
            to_show_neg = to_show[to_show["Contribution Value"] < 0].sort_values(
                by="Contribution", axis="index", ascending=False)
            if not st.session_state['show_more']:
                to_show_neg = to_show_neg[0:10]
            if search is not None:
                to_show_neg = to_show_neg[to_show_neg.index.str.contains(search, case=False)]
            st.table(to_show_neg.drop("Contribution Value", axis="columns"))
        with col2:
            st.subheader("Positive features")
            to_show_pos = to_show[to_show["Contribution Value"] >= 0].sort_values(
                by="Contribution", axis="index", ascending=False)
            if not st.session_state['show_more']:
                to_show_pos = to_show_pos[0:10]
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

with tab2:
    to_show = importance.copy()
    to_show = to_show.sort_values(by="Importance Value", axis="index", ascending=False)
    if not st.session_state['show_more']:
        to_show = to_show[0:10]
    if search is not None:
        to_show = to_show[to_show.index.str.contains(search, case=False)]
    st.table(to_show.drop("Importance Value", axis="columns"))


