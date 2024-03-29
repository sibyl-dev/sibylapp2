from enum import Enum
from os import path

import streamlit as st
import yaml

from sibylapp2.compute.context import get_config


@st.cache_data(show_spinner=False)
def load_config():
    with open(path.join(path.dirname(path.abspath(__file__)), "config.yml"), "r") as file:
        cfg = yaml.safe_load(file)
    return cfg


# GENERAL CONFIGURATIONS ==========================================================================
def get_bar_length():
    return load_config().get("BAR_LENGTH", 8)


def get_max_entities():
    return load_config().get("MAX_ENTITIES", 11)


def get_dataset_size():
    return load_config().get("DATASET_SIZE", 1000)


def get_load_upfront():
    return load_config().get("LOAD_UPFRONT", True)


def get_color_scheme():
    flip_colors = load_config().get("FLIP_COLORS", False)
    return load_config().get("COLOR_SCHEME", "Reversed" if flip_colors else "Standard")


def get_pages_to_show():
    return select_config("PAGES_TO_SHOW", "pages_to_show", "all")


# APPLICATION-SPECIFIC CONFIGURATIONS =============================================================
def select_config(name, api_name, default):
    if load_config().get(name) is not None:
        return load_config().get(name)
    if get_config(api_name) is not None:
        return get_config(api_name)
    return default


class PredType(Enum):
    BOOLEAN = 1
    CATEGORICAL = 2
    NUMERIC = 3


def to_pred_type(str_pred_type):
    if str_pred_type == "numeric":
        return PredType.NUMERIC
    if str_pred_type == "categorical":
        return PredType.CATEGORICAL
    if str_pred_type == "boolean":
        return PredType.BOOLEAN
    raise ValueError("Received invalid pred type %s" % str_pred_type)


FLIP_COLORS = select_config("FLIP_COLORS", "output_sentiment_is_negative", False)
PREDICTION_TYPE = to_pred_type(select_config("PREDICTION_TYPE", "output_type", "numeric"))
POSITIVE_TERM = select_config("POSITIVE_TERM", "output_pos_label", "True")
NEGATIVE_TERM = select_config("NEGATIVE_TERM", "output_neg_label", "False")
PRED_FORMAT_STRING = select_config("PRED_FORMAT_STRING", "output_format_string", "{}")
SUPPORT_PROBABILITY = select_config("SUPPORT_PROBABILITY", "show_probs", False)
ALLOW_PAGE_SELECTION = select_config("ALLOW_PAGE_SELECTION", "allow_page_selection", False)

MAX_FEATURES = select_config("MAX_FEATURES", "num_plot_features", 10)
TIME_UNIT = select_config("TIME_UNIT", "time_unit", "days")
USE_ROWS = select_config("USE_ROWS", "use_rows", False)
ROW_LABEL = select_config("ROW_LABEL", "row_label", "Row")


def pred_format_func(pred, display_proba=False):
    if display_proba:
        return f"{pred*100:.1f}%"
    if load_config().get("OVERRIDE_PRED_FORMAT"):
        return manual_pred_format_func(pred)
    if PREDICTION_TYPE == PredType.NUMERIC:
        return PRED_FORMAT_STRING.format(pred)
    if PREDICTION_TYPE == PredType.BOOLEAN:
        return POSITIVE_TERM if pred else NEGATIVE_TERM
    return str(pred)


def manual_pred_format_func(pred):
    # Not used unless config.OVERRIDE_PRED_FORMAT == True
    return str(pred)
