import streamlit as st
import ruamel.yaml as yaml
import os


NEG_EM = "🟥"
POS_EM = "🟦"
NEUT_EM = "🟪"
NEUT_EM_2 = "🟫"
BLANK_EM = "⬜"
UP_ARROW = "⬆"
DOWN_ARROW = "⬇"
DIVIDING_BAR = "|"


def represent_none(self, _):
    return self.represent_scalar("tag:yaml.org,2002:null", "")


def main():
    loader = yaml.YAML()

    st.title("Configuration Wizard")

    # Load existing configuration if available
    existing_config = load_existing_config(loader)

    with st.form("config_form"):
        config_data = dict()

        # Question 1: Color Scheme
        config_data["COLOR"] = st.radio(
            "What color scheme should we use?",
            ["Standard", "Reversed", "Neutral"],
            captions=[
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
            ],
            horizontal=True,
        )

        # Question 2: Use Multiple Rows
        config_data["USE_MULTIPLE_ROWS"] = st.radio(
            "Does your data have multiple rows?", ["Yes", "No"], horizontal=True
        )

        if config_data["USE_MULTIPLE_ROWS"] == "Yes":
            config_data["ROW_LABEL"] = st.text_input(
                "How should we label rows?", value="Timestamp"
            )

        with st.expander("General configurations"):
            config_data["BAR_LENGTH"] = st.slider(
                "How long should bars be?",
                min_value=2,
                max_value=10,
                value=8,
                step=2,
            )

        with st.expander("Configure terms"):
            terms = [
                ("Entity", "Label of whatever is being predicted on"),
                ("Feature", ""),
                ("Positive", "Features that increase the model output"),
                ("Negative", "Features that decrease the model output"),
            ]
            for term, helper in terms:
                st.text_input(term, max_chars=15, placeholder=helper)

        submitted = st.form_submit_button("Save config")

    if submitted:
        save_config(loader, config_data, existing_config)


def load_existing_config(loader):
    existing_config = {}
    if os.path.exists("config.yml"):
        with open("config.yml", "r") as yaml_file:
            existing_config = loader.load(yaml_file)
    return existing_config


def save_config(loader, config_data, existing_config):
    loader.default_flow_style = False

    if "COLOR" in config_data:
        color_option = config_data.pop("COLOR")
        if color_option == "Reversed":
            existing_config["FLIP_COLORS"] = True
        elif color_option in ["Standard", "Neutral"]:
            existing_config["FLIP_COLORS"] = False

    existing_config.update(config_data)

    with open("config2.yml", "w") as yaml_file:
        loader.dump(existing_config, yaml_file)
    st.success("Configuration saved successfully!")


if __name__ == "__main__":
    main()
