import math

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

from sibylapp.compute.context import get_term
from sibylapp.config import BAR_LENGTH, FLIP_COLORS
from sibylapp.view.utils.filtering import process_options

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


def show_table(df, gb=None, allow_unsafe=False):
    renames = {}
    for column in df:
        renames[column] = get_term(column)
    df = df.rename(columns=renames)
    if gb is None:
        gb = GridOptionsBuilder.from_dataframe(df)
    if df.shape[0] > 10:
        gb.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=10)
    AgGrid(
        df,
        fit_columns_on_grid_load=True,
        gridOptions=gb.build(),
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        allow_unsafe_jscode=allow_unsafe,
    )


def generate_bars(values, neutral=False):
    def round_away_from_zero(x):
        if x >= 0.0:
            return math.floor(x + 0.5)
        else:
            return math.ceil(x - 0.5)

    num_to_show = values / max(values.abs()) * BAR_LENGTH
    num_to_show = num_to_show.apply(round_away_from_zero).astype("int")
    if neutral:
        return [(NEUT_EM * n + BLANK_EM * (BAR_LENGTH - n) + UP_ARROW) for n in num_to_show]
    else:
        return [
            (
                (POS_EM * n + BLANK_EM * (BAR_LENGTH - n) + UP_ARROW)
                if n > 0
                else (DOWN_ARROW + BLANK_EM * (BAR_LENGTH + n) + NEG_EM * -n)
            )
            for n in num_to_show
        ]


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
