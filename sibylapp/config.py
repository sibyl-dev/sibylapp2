from enum import Enum
from os import path

import yaml

from sibylapp.compute.context import get_gui_config

with open(path.join(path.dirname(path.abspath(__file__)), "config.yml"), "r") as f:
    cfg = yaml.safe_load(f)

# GENERAL CONFIGURATIONS ==========================================================================
BAR_LENGTH = cfg.get("BAR_LENGTH", 8)
MAX_ENTITIES = cfg.get("MAX_ENTITIES", 11)
DATASET_SIZE = cfg.get("DATASET_SIZE", 1000)
LOAD_UPFRONT = cfg.get("LOAD_UPFRONT", True)


# APPLICATION-SPECIFIC CONFIGURATIONS =============================================================
def get_config(name, api_name, default):
    if cfg.get(name) is not None:
        return cfg.get(name)
    if get_gui_config(api_name) is not None:
        return get_gui_config(api_name)
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


FLIP_COLORS = get_config("FLIP_COLORS", "model_pred_bad_outcome", False)
PREDICTION_TYPE = to_pred_type(get_config("PREDICTION_TYPE", "pred_type", "numeric"))
POSITIVE_TERM = get_config("POSITIVE_TERM", "pos_pred_name", "True")
NEGATIVE_TERM = get_config("NEGATIVE_TERM", "neg_pred_name", "False")
PRED_FORMAT_STRING = get_config("PRED_FORMAT_STRING", "pred_format_string", "{}")
SUPPORT_PROBABILITY = get_config("SUPPORT_PROBABILITY", "support_probability", False)


def pred_format_func(pred, display_proba=False):
    if display_proba:
        return f"{pred*100:.1f}%"
    if cfg.get("OVERRIDE_PRED_FORMAT"):
        return manual_pred_format_func(pred)
    if PREDICTION_TYPE == PredType.NUMERIC:
        return PRED_FORMAT_STRING.format(pred)
    if PREDICTION_TYPE == PredType.BOOLEAN:
        return POSITIVE_TERM if pred else NEGATIVE_TERM
    return str(pred)


def manual_pred_format_func(pred):
    # Not used unless config.OVERRIDE_PRED_FORMAT == True
    return str(pred)
