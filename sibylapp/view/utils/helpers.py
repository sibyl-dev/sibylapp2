import streamlit as st
from sibylapp.config import BAR_LENGTH, FLIP_COLORS
from sibylapp.compute.context import get_term
import math

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


def generate_bars(values, neutral=False):
    def round_away_from_zero(x):
        if x >= 0.0:
            return math.floor(x + 0.5)
        else:
            return math.ceil(x - 0.5)

    num_to_show = values / max(values.abs()) * BAR_LENGTH
    num_to_show = num_to_show.apply(round_away_from_zero).astype("int")
    if neutral:
        return [
            (NEUT_EM * n + BLANK_EM * (BAR_LENGTH - n) + UP_ARROW) for n in num_to_show
        ]
    else:
        return [
            (POS_EM * n + BLANK_EM * (BAR_LENGTH - n) + UP_ARROW)
            if n > 0
            else (DOWN_ARROW + BLANK_EM * (BAR_LENGTH + n) + NEG_EM * -n)
            for n in num_to_show
        ]


def show_sorted_contributions(to_show, sort_by, show_func):
    if sort_by == "Side-by-side":
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(get_term("Negative"))
            to_show_neg = to_show[to_show["Contribution Value"] < 0].sort_values(
                by="Contribution", axis="index", ascending=False
            )
            to_show_neg = process_options(to_show_neg)
            show_func(to_show_neg)
        with col2:
            st.subheader(get_term("Positive"))
            to_show_pos = to_show[to_show["Contribution Value"] >= 0].sort_values(
                by="Contribution", axis="index", ascending=False
            )
            to_show_pos = process_options(to_show_pos)
            show_func(to_show_pos)
    else:
        if sort_by == "Absolute":
            to_show = to_show.reindex(
                to_show["Contribution Value"].abs().sort_values(ascending=False).index
            )
        if sort_by == "Ascending":
            to_show = to_show.sort_values(by="Contribution Value", axis="index")
        if sort_by == "Descending":
            to_show = to_show.sort_values(
                by="Contribution Value", axis="index", ascending=False
            )
        to_show = process_options(to_show)
        show_func(to_show)
