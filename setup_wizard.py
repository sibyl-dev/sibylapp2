import streamlit as st
import ruamel.yaml as yaml
import os


def represent_none(self, _):
    return self.represent_scalar("tag:yaml.org,2002:null", "")


def main():
    loader = yaml.YAML()
    # loader.add_representer(type(None), represent_none)

    st.title("Configuration Wizard")

    # Load existing configuration if available
    existing_config = load_existing_config(loader)

    config_data = {}

    # Question 1: Color Scheme
    config_data["COLOR"] = st.radio("Which color scheme would you like?", ["A", "B", "C"])

    # Question 2: Use Multiple Rows
    config_data["USE_MULTIPLE_ROWS"] = st.radio(
        "Does your data have multiple rows?", ["Yes", "No"]
    )

    config_data["BAR_LENGTH"] = st.number_input(
        "What is the length of the bar?", min_value=0, max_value=10, value=8
    )

    save_config(loader, config_data, existing_config)


def load_existing_config(loader):
    existing_config = {}
    if os.path.exists("config.yml"):
        with open("config.yml", "r") as yaml_file:
            existing_config = loader.load(yaml_file)
    return existing_config


def save_config(loader, config_data, existing_config):
    existing_config.update(config_data)
    loader.default_flow_style = False
    for key, value in config_data.items():
        if value is None:
            existing_config[key] = ""
        else:
            existing_config[key] = value
    with open("config2.yml", "w") as yaml_file:
        loader.dump(existing_config, yaml_file)
    st.success("Configuration saved successfully!")


if __name__ == "__main__":
    main()
