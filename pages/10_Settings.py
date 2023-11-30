import streamlit as st
import ruamel.yaml as yaml
import os
from sibylapp2 import config


NEG_EM = "🟥"
POS_EM = "🟦"
NEUT_EM = "🟪"
NEUT_EM_2 = "🟨"
BLANK_EM = "⬜"
UP_ARROW = "⬆"
DOWN_ARROW = "⬇"
DIVIDING_BAR = "|"

CONFIG_FILEPATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "sibylapp2", "config.yml"
)


def load_existing_config(loader):
    existing_config = {}
    if os.path.exists(CONFIG_FILEPATH):
        with open(CONFIG_FILEPATH) as yaml_file:
            existing_config = loader.load(yaml_file)
    return existing_config


def save_config(loader, config_data, existing_config):
    old_config = existing_config.copy()
    loader.default_flow_style = False

    existing_config.update(config_data)

    with open(CONFIG_FILEPATH, "w") as yaml_file:
        loader.dump(existing_config, yaml_file)
    if old_config != existing_config:
        st.toast("Configuration saved successfully!", icon="✅")


def color_scheme_descriptions():
    return [
        (
            f"{DOWN_ARROW}{NEG_EM}{NEG_EM}{DIVIDING_BAR}{POS_EM}{POS_EM}{UP_ARROW}"
            "  \nHigher model outputs are good"
        ),
        (
            f"{DOWN_ARROW}{POS_EM}{POS_EM}{DIVIDING_BAR}{NEG_EM}{NEG_EM}{UP_ARROW}"
            "  \nHigher model outputs are bad"
        ),
        (
            f"{DOWN_ARROW}{NEUT_EM_2}{NEUT_EM_2}{DIVIDING_BAR}{NEUT_EM}{NEUT_EM}{UP_ARROW}"
            "  \nModel outputs are neutral"
        ),
    ]


def view():
    st.title("Settings")
    loader = yaml.YAML()

    # Load existing configuration if available
    existing_config = load_existing_config(loader)

    config_data = dict()

    # Question 1: Color Scheme
    color_scheme_options = ["Standard", "Reversed", "Neutral"]
    config_data["COLOR_SCHEME"] = st.radio(
        "Color scheme:",
        color_scheme_options,
        captions=color_scheme_descriptions(),
        horizontal=True,
        index=color_scheme_options.index(config.get_color_scheme()),
    )

    config_data["BAR_LENGTH"] = st.slider(
        "Length of bars:", min_value=4, max_value=10, value=config.get_bar_length()
    )

    def remove_eids_and_row_id_dict():
        if "eids" in existing_config:
            del existing_config["eids"]
        if "row_id_dict" in existing_config:
            del existing_config["row_id_dict"]

    config_data["MAX_ENTITIES"] = st.number_input(
        "Number of entities to include:",
        min_value=1,
        max_value=50,
        value=config.get_max_entities(),
        on_change=remove_eids_and_row_id_dict,
    )

    config_data["DATASET_SIZE"] = st.number_input(
        "Number of dataset entries to load:",
        min_value=10,
        value=config.get_dataset_size(),
        help="High values will slow down the application",
        on_change=lambda: st.session_state.pop("dataset_eids"),
    )

    save_config(loader, config_data, existing_config)
    config.load_config.clear()  # clear cache to force config reload


view()
