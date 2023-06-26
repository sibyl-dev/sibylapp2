import pandas as pd
import streamlit as st
from sibylapp.compute import contributions
from sibylapp.view.utils.helpers import generate_bars_bidirectional, process_options
from st_aggrid import AgGrid


def view(all_contributions):
    sort_by = st.selectbox(
        "Sort order", ["Total", "Most Increasing", "Most Decreasing"]
    )

    global_contributions = contributions.compute_global_contributions(
        all_contributions
    )
    bars = generate_bars_bidirectional(
        global_contributions["negative"], global_contributions["positive"]
    )
    feature_info = all_contributions[next(iter(all_contributions))][
        ["category", "Feature"]
    ].rename(columns={"category": "Category"})
    to_show = pd.concat([feature_info, bars, global_contributions], axis="columns")

    if sort_by == "Total":
        to_show = to_show.reindex(
            (to_show["negative"].abs() + to_show["positive"])
            .sort_values(ascending=False)
            .index
        )
    if sort_by == "Most Increasing":
        to_show = to_show.sort_values(by="positive", axis="index", ascending=False)
    if sort_by == "Most Decreasing":
        to_show = to_show.sort_values(by="negative", axis="index")

    to_show = process_options(to_show).drop(["positive", "negative"], axis=1)
    AgGrid(to_show, fit_columns_on_grid_load=True)
    return to_show
