import numpy as np
import streamlit as st


@st.cache_data
def setup_contributions(_app, sample, bar_length):
    print("COMPUTING CONTRIBUTIONS")
    contributions = _app.produce_feature_contributions(sample)
    for eid in contributions:
        contributions[eid]["Contribution Value"] = contributions[eid]["Contribution"]
        contributions[eid].drop("Average/Mode", axis="columns", inplace=True)
        contributions[eid].set_index("Feature Name", inplace=True)
        num_to_show = contributions[eid]["Contribution"] / max(
            contributions[eid]["Contribution"].abs()) * bar_length
        num_to_show = num_to_show.apply(np.ceil).astype("int")
        contributions[eid]["Contribution"] = [
            ("🟦" * n + "⬜" * (bar_length - n) + "⬆") if n > 0 else (
                    "⬇" + "⬜" * (bar_length + n) + "🟥" * -n) for n in num_to_show]

    return contributions
