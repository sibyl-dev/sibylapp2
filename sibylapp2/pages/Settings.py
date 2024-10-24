# pylint: disable=invalid-name

import os

import streamlit as st
from ruamel import yaml

from sibylapp2 import config
from sibylapp2.compute.contributions import get_dataset_contributions
from sibylapp2.compute.model import get_dataset_predictions
from sibylapp2.log import log
from sibylapp2.view.utils.helpers import neg_em, pos_em

UP_ARROW = "⬆"
DOWN_ARROW = "⬇"
DIVIDING_BAR = "|"

CONFIG_FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.yml")


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
        # print differences between old_config and existing_config
        changed = {
            k: existing_config[k] for k in existing_config if existing_config[k] != old_config[k]
        }
        log(action="changed_setting", details=changed)
        st.toast("Configuration saved successfully!", icon="✅")
        st.toast("Refresh the page to see the changes.", icon="🔄")


def generate_color_scheme_caption(color_scheme, description):
    return (
        f"{DOWN_ARROW}{neg_em(color_scheme)*2}{DIVIDING_BAR}{pos_em(color_scheme)*2}{UP_ARROW}  \n"
        + description
    )


def main():
    def _clear_eid_data():
        if "eids" in st.session_state:
            del st.session_state["eids"]
        if "row_id_dict" in st.session_state:
            del st.session_state["row_id_dict"]

    def _clear_dataset_data():
        if "dataset_eids" in st.session_state:
            del st.session_state["dataset_eids"]
        get_dataset_contributions.clear()  # clear cache to force reload with new settings
        get_dataset_predictions.clear()

    st.title("Settings")
    loader = yaml.YAML()

    # Load existing configuration if available
    existing_config = load_existing_config(loader)

    config_data = dict()

    # Question 1: Color Scheme
    color_scheme_options = ["Standard", "Reversed", "Neutral"]
    color_scheme_descriptions = [
        "Higher model outputs are good",
        "Higher model outputs are bad",
        "Model outputs are neutral",
    ]
    config_data["COLOR_SCHEME"] = st.radio(
        "Color scheme:",
        color_scheme_options,
        captions=[
            generate_color_scheme_caption(scheme, description)
            for scheme, description in zip(color_scheme_options, color_scheme_descriptions)
        ],
        horizontal=True,
        index=(
            0
            if config.get_color_scheme() not in color_scheme_options
            else color_scheme_options.index(config.get_color_scheme())
        ),
    )

    setting_col, _ = st.columns(2)
    with setting_col:
        config_data["BAR_LENGTH"] = st.slider(
            "Length of bars:",
            min_value=4,
            max_value=10,
            value=config.get_bar_length(),
        )
        config_data["MAX_ENTITIES"] = st.number_input(
            "Number of entities to include:",
            min_value=1,
            max_value=50,
            value=config.get_max_entities(),
            on_change=_clear_eid_data,
        )
        config_data["DATASET_SIZE"] = st.number_input(
            "Number of dataset entries to load:",
            min_value=10,
            value=config.get_dataset_size(),
            help="High values will slow down the application",
            on_change=_clear_dataset_data(),
        )
        if config.ALLOW_PAGE_SELECTION:
            with st.form("page_selection"):
                st.write("Select pages to enable:")
                all_pages = [
                    "Prediction Summary",
                    "Explore a Prediction",
                    "Similar Entities",
                    "Compare Entities",
                    "Experiment with Changes",
                    "Change over Time",
                    "Understand the Model",
                    "Edit Features",
                    "Settings",
                ]
                show_pages_bools = []
                for page in all_pages:
                    show_pages_bools.append(
                        st.toggle(page, value=page in config.get_pages_to_show())
                    )
                submitted = st.form_submit_button("Save page selections")
                if submitted:
                    config_data["PAGES_TO_SHOW"] = [
                        page for page, show in zip(all_pages, show_pages_bools) if show
                    ]
                    save_config(loader, config_data, existing_config)
                    config.load_config.clear()  # clear cache to force config reload
                    st.rerun()

    save_config(loader, config_data, existing_config)
    config.load_config.clear()  # clear cache to force config reload
