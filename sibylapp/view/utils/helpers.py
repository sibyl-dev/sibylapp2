import math

import pandas as pd
from st_aggrid import AgGrid, ColumnsAutoSizeMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

from sibylapp.compute.context import get_term
from sibylapp.config import BAR_LENGTH, FLIP_COLORS
import streamlit as st

if FLIP_COLORS:
    POS_EM = "🟥"
    NEG_EM = "🟦"
else:
    POS_EM = "🟦"
    NEG_EM = "🟥"
NEUT_EM = "🟪"
BLANK_EM = "⬜"
UP_ARROW = "⬆"
DOWN_ARROW = "⬇"
DIVIDING_BAR = "|"


def show_sort_options(options):
    return st.radio("Sort by", options, horizontal=True)


def get_pos_neg_names():
    if FLIP_COLORS:
        return "red", "blue"
    else:
        return "blue", "red"


def show_table(df, page_size=10):
    table = st.container()
    _, col1, col2 = st.columns((4, 1, 1))
    with col2:
        page_size = st.selectbox("Rows per page", [10, 25, 50])
    with col1:
        page = st.number_input("Page", value=1, step=1, min_value=1, max_value=int(df.shape[0]/page_size)+1)
    renames = {}
    for column in df:
        renames[column] = get_term(column)
    df = df.rename(columns=renames)

    table.data_editor(df[(page-1)*page_size: (page-1)*page_size+page_size], 
                   hide_index=True, use_container_width=True, num_rows="fixed", disabled=True)


def generate_bars(values, neutral=False, show_number=False):
    def format_func(n, v=None):
        if neutral:
            formatted = (NEUT_EM * n + BLANK_EM * (BAR_LENGTH - n) + UP_ARROW)
        else:
            formatted = (POS_EM * n + BLANK_EM * (BAR_LENGTH - n) + UP_ARROW) if n > 0 else (DOWN_ARROW + BLANK_EM * (BAR_LENGTH + n) + NEG_EM * -n)
        if show_number:
            formatted = "%s    %.3f" % (formatted, v)
        return formatted

    def round_away_from_zero(x):
        if x >= 0.0:
            return math.floor(x + 0.5)
        else:
            return math.ceil(x - 0.5)

    num_to_show = values / max(values.abs()) * BAR_LENGTH
    num_to_show = num_to_show.apply(round_away_from_zero).astype("int")

    return [format_func(n, v) for n, v in zip(num_to_show, values)]


def generate_bars_bidirectional(neg_values, pos_values):
    def round_away_from_zero(x):
        if x >= 0.0:
            return math.floor(x + 0.5)
        else:
            return math.ceil(x - 0.5)

    half_bar_length = math.ceil(BAR_LENGTH / 2)

    neg_num_to_show = (
        (neg_values / max(neg_values.abs()) * half_bar_length)
        .apply(round_away_from_zero)
        .astype("int")
    )
    pos_num_to_show = (
        (pos_values / max(pos_values.abs()) * half_bar_length)
        .apply(round_away_from_zero)
        .astype("int")
    )
    strings = [
        (
            DOWN_ARROW
            + BLANK_EM * (half_bar_length + neg)
            + (NEG_EM * -neg)
            + DIVIDING_BAR
            + (POS_EM * pos)
            + (BLANK_EM * (half_bar_length - pos))
            + UP_ARROW
        )
        for (neg, pos) in zip(neg_num_to_show, pos_num_to_show)
    ]
    return pd.Series(strings, index=neg_values.index, name="Average Contribution")


def rename_for_pyreal_vis(df):
    return {eid: df[eid].rename(columns={"Feature": "Feature Name"}) for eid in df}
