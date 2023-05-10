import pandas as pd
import pickle
from pyreal import RealApp
from pyreal.sample_applications import ames_housing
import streamlit as st


@st.cache_data
def get_application(application):
    if application == "turbines":
        data = pd.read_csv("data.csv")
        y = data["label"]
        X = data.drop("label", axis="columns")

        features = pd.read_csv("features.csv")
        features = features[["name", "description"]]
        features = features.set_index("name")
        feature_descriptions = features.iloc[:, 0].to_dict()

        model = pickle.load(open("model.pkl", "rb"))

        realApp = RealApp(
            model,
            X_train_orig=X,
            y_train=y,
            id_column="eid",
            feature_descriptions=feature_descriptions,
        )

        return X, realApp

    elif application == "housing":
        X = ames_housing.load_data()
        realApp = ames_housing.load_app()

        return X, realApp

    return None, None


def get_format_func(application):
    # This function is separate from get_application because functions can't be cached
    if application == "turbines":

        def format_func(pred):
            return "failure" if pred else "normal"

        return format_func
    if application == "housing":

        def format_func(pred):
            return "${:,.2f}".format(pred)

        return format_func
