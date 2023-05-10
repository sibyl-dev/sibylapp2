import numpy as np
import streamlit as st


@st.cache_data
def setup_importance(_app, bar_length):
    importance = _app.produce_feature_importance()
    importance.set_index("Feature Name", inplace=True)
    importance["Importance Value"] = importance["Importance"]
    num_to_show = importance["Importance Value"] / max(
        importance["Importance Value"].abs()) * bar_length
    num_to_show = num_to_show.apply(np.ceil).astype("int")
    importance["Importance"] = [("🟪" * n + "⬜" * (bar_length - n) + "⬆") for n in num_to_show]

    return importance