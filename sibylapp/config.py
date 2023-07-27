from enum import Enum
from sibylapp.compute import context
import os.path as path
import yaml


with open(path.join(path.dirname(path.abspath(__file__)), "config.yml")) as f:
    cfg = yaml.safe_load(f)

# GENERAL CONFIGURATIONS ============================================================================
BAR_LENGTH = cfg.get("BAR_LENGTH", 8)
MAX_ENTITIES = cfg.get("MAX_ENTITIES", 11)
DATASET_SIZE = cfg.get("DATASET_SIZE", 1000)
LOAD_UPFRONT = cfg.get("LOAD_UPFRONT", True)


# APPLICATION-SPECIFIC CONFIGURATIONS =============================================================
def flip_colors():
    return (
        cfg.get("FLIP_COLORS")
        if cfg.get("FLIP_COLORS") is not None
        else context.get_flip_colors_from_api()
    )


FLIP_COLORS = flip_colors()


class PredType(Enum):
    BOOLEAN = 1
    CATEGORICAL = 2
    NUMERIC = 3


# add names for "positive" and "negative" values after we have a more concrete idea
PREDICTION_TYPE = PredType.NUMERIC
POSITIVE_TERM = None
NEGATIVE_TERM = None


def pred_format_func(pred):
    if get_gui_config("pred_type") == "numeric":
        if get_gui_config("pred_format_string") is not None:
            return get_gui_config("pred_format_string").format(pred)
    if get_gui_config("pred_type") == "boolean":
        return (
            get_gui_config("pos_pred_name", pred)
            if pred
            else get_gui_config("neg_pred_name", pred)
        )


# def pred_format_func(pred):
# Function to format prediction from model
# See pre-written options below for defaults or return None to use API defaults
#    return None


# PRE-WRITTEN FORMAT FUNCTION OPTIONS =============================================================
def format_none(pred):
    return pred


def format_dollar(pred):
    return "${:,.2f}".format(pred)


def format_class_name(pred, class_names):
    return class_names[int(pred)]


def format_boolean_name(pred):
    return POSITIVE_TERM if pred else NEGATIVE_TERM


def format_number(pred, decimals=2):
    return "{:,.{prec}f}".format(pred, prec=decimals)
