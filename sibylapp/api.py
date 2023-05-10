from sibylapp.config import BASE_URL
import requests
import pandas as pd

session = requests.Session()


def fetch_model_id():
    model_id = session.get(BASE_URL + "models").json()["models"][0]["id"]
    return model_id


def fetch_contributions(eids):
    features = session.get(BASE_URL + "features").json()["features"]
    features_df = pd.DataFrame(features)
    features_df = features_df.set_index("name")

    results = {}
    for eid in eids:
        json = {"eid": eid, "model_id": fetch_model_id()}

        contributions = session.post(BASE_URL + "contributions", json=json).json()
        contribution_df = pd.DataFrame(contributions)
        result = pd.concat([features_df, contribution_df], axis=1)
        results[eid] = result
    return results


def fetch_categories():
    categories = session.get(BASE_URL + "categories").json()["categories"]
    return pd.DataFrame(categories)