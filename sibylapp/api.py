from sibylapp.config import BASE_URL
import requests
import pandas as pd


def fetch_model_id():
    return requests.get(BASE_URL + "models").json()["models"][0]["id"]


def fetch_contributions(eids):
    features = requests.get(BASE_URL + "features").json()
    features_df = pd.DataFrame(features["features"])
    features_df = features_df.set_index("name")

    results = {}
    for eid in eids:
        json = {"eid": eid, "model_id": fetch_model_id()}

        contributions = requests.post(BASE_URL + "contributions", json=json).json()
        contribution_df = pd.DataFrame(contributions)
        result = pd.concat([features_df, contribution_df], axis=1)
        result = result.set_index("description")
        results[eid] = result
    return results