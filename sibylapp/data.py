import pandas as pd
import pickle
from pyreal import RealApp
from pyreal.sample_applications import ames_housing


def get_application(application):
    if application == "turbines":

        def format_func(pred):
            return "failure" if pred else "normal"

        data = pd.read_csv("data.csv")
        y = data["label"]
        X = data.drop("label", axis="columns")

        features = pd.read_csv("features.csv")
        features = features[["name", "description"]]
        features = features.set_index("name")
        feature_descriptions = features.iloc[:, 0].to_dict()

        model = pickle.load(open("model.pkl", "rb"))

        print(model.predict(X.drop("eid", axis="columns")))

        realApp = RealApp(
            model,
            X_train_orig=X,
            y_train=y,
            id_column="eid",
            feature_descriptions=feature_descriptions,
        )

        return X, realApp, format_func

    elif application == "housing":

        def format_func(pred):
            return "${:,.2f}".format(pred)

        X = ames_housing.load_data()
        realApp = ames_housing.load_app()

        return X, realApp, format_func

    return None, None
