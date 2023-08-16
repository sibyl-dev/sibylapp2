from __future__ import annotations

import math

import pandas as pd
import streamlit as st

from sibylapp.compute.context import get_term
from sibylapp.config import (
    BAR_LENGTH,
    FLIP_COLORS,
    NEGATIVE_TERM,
    POSITIVE_TERM,
    PREDICTION_TYPE,
    PredType,
)

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


def show_text_input_side_by_side(
    label: str,
    options: list | None = None,
    default_input: str | None = None,
    numeric: bool = False,
    **input_params,
) -> int | float | str:
    col1, col2 = st.columns([2, 2])
    col1.markdown(label)

    if numeric:
        return col2.number_input(
            "hidden", value=default_input, label_visibility="collapsed", **input_params
        )
    else:
        if options is None:
            return col2.text_input(
                "hidden", value=default_input, label_visibility="collapsed", **input_params
            )
        else:
            return col2.selectbox(
                "hidden",
                options=options,
                index=options.index(default_input),
                label_visibility="collapsed",
                **input_params,
            )


def get_pos_neg_names():
    if FLIP_COLORS:
        return "red", "blue"
    else:
        return "blue", "red"


def show_table(df, page_size=10, key=None, style_function=None):
    table = st.container()
    _, col1, col2 = st.columns((4, 1, 1))
    with col2:
        page_size_key = "per_page_key"
        if key is not None:
            page_size_key = "%s%s" % (key, "_per_page")
        page_size = st.selectbox("Rows per page", [10, 25, 50], key=page_size_key)
    with col1:
        page_key = "page_key"
        if key is not None:
            page_key = "%s%s" % (key, "_page")
        page = st.number_input(
            "Page",
            value=1,
            step=1,
            min_value=1,
            max_value=int(df.shape[0] / page_size) + 1,
            key=page_key,
        )
    renames = {}
    for column in df:
        renames[column] = get_term(column)
    df = df.rename(columns=renames)
    df = df[(page - 1) * page_size : page * page_size]

    # pandas styler must be display in whole
    if style_function is not None:
        df = style_function(df)
    table.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=True,
    )


def generate_bars(values, neutral=False, show_number=False):
    """
    Generate colorbars for numeric values.
    epsilon is used to avoid zero division error when all values are zero.
    """

    def format_func(num, value=None):
        if neutral:
            formatted = NEUT_EM * num + BLANK_EM * (BAR_LENGTH - num) + UP_ARROW
        else:
            formatted = (
                (POS_EM * num + BLANK_EM * (BAR_LENGTH - num) + UP_ARROW)
                if num > 0
                else (DOWN_ARROW + BLANK_EM * (BAR_LENGTH + num) + NEG_EM * -num)
            )
        if show_number:
            formatted = "%s    %.3f" % (formatted, value)
        return formatted

    def round_away_from_zero(x):
        if x >= 0.0:
            return math.floor(x + 0.5)
        else:
            return math.ceil(x - 0.5)

    if max(values.abs()) == 0:
        num_to_show = values * BAR_LENGTH  # this work since values is zero
    else:
        num_to_show = values / max(values.abs()) * BAR_LENGTH
    num_to_show = num_to_show.apply(round_away_from_zero).astype("int")

    return [format_func(num, value) for num, value in zip(num_to_show, values)]


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


def show_legend(similar_entities=False):
    model_pred = get_term("Prediction", lower=True)
    separator = "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;"
    if similar_entities:
        pos_change = " Increase in %s's contribution to" % get_term("Feature", lower=True)
        neg_change = " Decrease in %s's contribution to" % get_term("Feature", lower=True)
    else:
        if PREDICTION_TYPE == PredType.BOOLEAN:
            pos_change = f" towards **{POSITIVE_TERM}** as"
            neg_change = f" towards **{NEGATIVE_TERM}** as"
        else:
            pos_change = " Increase in"
            neg_change = " Decrease in"
    st.write(
        (NEG_EM + neg_change + " " + model_pred)
        + separator
        + (POS_EM + pos_change + " " + model_pred)
    )
