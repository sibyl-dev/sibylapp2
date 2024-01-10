from __future__ import annotations

import math

import pandas as pd
import streamlit as st

from sibylapp2.compute import features, importance
from sibylapp2.compute.api import format_feature_df_for_modify, modify_features
from sibylapp2.compute.context import get_term
from sibylapp2.config import (
    NEGATIVE_TERM,
    POSITIVE_TERM,
    PREDICTION_TYPE,
    PredType,
    get_bar_length,
    get_color_scheme,
)

NEUT_EM = "🟪"
BLANK_EM = "⬜"
UP_ARROW = "⬆"
DOWN_ARROW = "⬇"
DIVIDING_BAR = "|"


def pos_em(color_scheme=None):
    color_scheme = get_color_scheme() if color_scheme is None else color_scheme
    if color_scheme == "Reversed":
        return "🟥"
    elif color_scheme == "Standard":
        return "🟦"
    else:
        return "🟪"


def neg_em(color_scheme=None):
    color_scheme = get_color_scheme() if color_scheme is None else color_scheme
    if color_scheme == "Reversed":
        return "🟦"
    elif color_scheme == "Standard":
        return "🟥"
    else:
        return "🟨"


def show_sort_options(options):
    return st.radio("Sort/Filter by", options, horizontal=True)


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
            "hidden", value=default_input, label_visibility="collapsed", key=label, **input_params
        )
    else:
        if options is None:
            return col2.text_input(
                "hidden",
                value=default_input,
                label_visibility="collapsed",
                key=label,
                **input_params,
            )
        else:
            index = options.index(default_input) if default_input in options else None
            return col2.selectbox(
                "hidden",
                options=options,
                index=index,
                label_visibility="collapsed",
                key=label,
                **input_params,
            )


def get_pos_neg_names():
    if get_color_scheme() == "Reversed":
        return "red", "blue"
    elif get_color_scheme() == "Standard":
        return "blue", "red"
    else:
        return "purple", "yellow"


def show_table(df, key, style_function=None, enable_editing=True):
    """
    Show a table with pagination and editing capabilities.

    Args:
        df (DataFrame): Dataframe to show
        key (string): Key to use for the table
        style_function (function): Function to apply to the dataframe before showing
        enable_editing (bool): Whether to enable any editing of the table.
            Supports editing features and categories.

    Returns:
        None
    """
    st.session_state["original_table_%s" % key] = df.copy()
    if ("edited_table_%s" % key) not in st.session_state:
        st.session_state["edited_table_%s" % key] = df.copy()
    df = st.session_state["edited_table_%s" % key]

    column_config = {}
    for column in df:
        if column == "Category":
            column_config[column] = st.column_config.SelectboxColumn(
                options=features.get_categories(),
                disabled=not enable_editing,
                label=get_term(column),
            )
        elif column == "Feature":
            column_config[column] = st.column_config.TextColumn(
                disabled=not enable_editing, label=get_term(column)
            )
        else:
            column_config[column] = st.column_config.Column(disabled=True, label=get_term(column))

    table = st.container()
    _, col1, col2 = st.columns((4, 1, 1))
    with col2:
        page_size_key = "per_page_key"
        if key is not None:
            page_size_key = "%s%s" % (key, "_per_page")
        page_size = st.selectbox("Rows per page", [10, 25, 50], key=page_size_key)
        reset_changes_container = st.empty()
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
        save_changes_container = st.empty()

    df = df[(page - 1) * page_size : page * page_size]

    # pandas styler must be display in whole
    if style_function is not None:
        df = style_function(df)

    def update_table_with_changes():
        if "changes_to_table_%s" % key in st.session_state:
            changes = st.session_state["changes_to_table_%s" % key]["edited_rows"]
            for row in changes:
                for col in changes[row]:
                    row_offset = row + ((page - 1) * page_size)
                    st.session_state["edited_table_%s" % key].iloc[row_offset][col] = changes[row][
                        col
                    ]
                    st.session_state["changes_made"] = True

    st.write(column_config)
    table.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        column_config=column_config,
        key="changes_to_table_%s" % key,
        on_change=update_table_with_changes,
    )

    def reset_changes():
        st.session_state["edited_table_%s" % key] = st.session_state["original_table_%s" % key]
        st.session_state["changes_made"] = False

    def save_changes():
        st.session_state["original_table_%s" % key] = st.session_state["edited_table_%s" % key]
        modify_features(
            format_feature_df_for_modify(st.session_state["edited_table_%s" % key].copy())
        )
        st.session_state["changes_made"] = False
        del st.session_state["changes_to_table_%s" % key]
        features.get_features.clear()
        importance.compute_importance.clear()  # Should refactor to avoid having to do this

    if enable_editing:
        if "changes_made" not in st.session_state:
            st.session_state["changes_made"] = False
        reset_changes_container.button(
            "Reset changes", disabled=not st.session_state["changes_made"], on_click=reset_changes
        )
        save_changes_container.button(
            "Save changes to database",
            disabled=not st.session_state["changes_made"],
            on_click=save_changes,
        )


def generate_bars(values, neutral=False, show_number=False):
    """
    Generate colorbars for numeric values.
    epsilon is used to avoid zero division error when all values are zero.
    """

    def format_func(num, value=None):
        if neutral:
            formatted = NEUT_EM * num + BLANK_EM * (get_bar_length() - num) + UP_ARROW
        else:
            formatted = (
                (pos_em() * num + BLANK_EM * (get_bar_length() - num) + UP_ARROW)
                if num > 0
                else (DOWN_ARROW + BLANK_EM * (get_bar_length() + num) + neg_em() * -num)
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
        num_to_show = values * get_bar_length()  # this work since values is zero
    else:
        num_to_show = values / max(values.abs()) * get_bar_length()
    num_to_show = num_to_show.apply(round_away_from_zero).astype("int")

    return [format_func(num, value) for num, value in zip(num_to_show, values)]


def generate_bars_bidirectional(neg_values, pos_values):
    def round_away_from_zero(x):
        if x >= 0.0:
            return math.floor(x + 0.5)
        else:
            return math.ceil(x - 0.5)

    half_bar_length = math.ceil(get_bar_length() / 2)

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
            + (neg_em() * -neg)
            + DIVIDING_BAR
            + (pos_em() * pos)
            + (BLANK_EM * (half_bar_length - pos))
            + UP_ARROW
        )
        for (neg, pos) in zip(neg_num_to_show, pos_num_to_show)
    ]
    return pd.Series(strings, index=neg_values.index, name="Average Contribution")


def rename_for_pyreal_vis(df):
    return {eid: df[eid].rename(columns={"Feature": "Feature Name"}) for eid in df}


def show_legend(similar_entities=False):
    model_pred = get_term("prediction")
    separator = "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;"
    if similar_entities:
        pos_change = " Increase in %s's contribution to" % get_term("feature")
        neg_change = " Decrease in %s's contribution to" % get_term("feature")
    else:
        if PREDICTION_TYPE == PredType.BOOLEAN:
            pos_change = f" towards **{POSITIVE_TERM}** as"
            neg_change = f" towards **{NEGATIVE_TERM}** as"
        else:
            pos_change = " Increase in"
            neg_change = " Decrease in"
    st.write(
        (neg_em() + neg_change + " " + model_pred)
        + separator
        + (pos_em() + pos_change + " " + model_pred)
    )
