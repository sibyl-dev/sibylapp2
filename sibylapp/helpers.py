import streamlit as st
from sibylapp.config import BAR_LENGTH, FLIP_COLORS
import math

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


def process_options(to_show):
    return process_search(process_filter(process_show_more(to_show)))


def process_show_more(to_show):
    if not st.session_state["show_more"]:
        return to_show[0:10]
    return to_show


def process_search(to_show):
    if st.session_state["search_term"] is not None:
        to_show = to_show[
            to_show["Feature"].str.contains(st.session_state["search_term"], case=False)
        ]
    return to_show


def process_filter(to_show):
    if len(st.session_state["filters"]) > 0:
        return to_show[to_show["Category"].isin(st.session_state["filters"])]
    return to_show


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
