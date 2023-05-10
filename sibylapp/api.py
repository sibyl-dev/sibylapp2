from sibylapp.config import BASE_URL
import requests
import pandas as pd

session = requests.Session()


def fetch_model_id():
    model_id = session.get(BASE_URL + "models").json()["models"][0]["id"]
    return model_id


def fetch_eids():
    entities = session.get(BASE_URL + "entities").json()["entities"]
    return [entry["eid"] for entry in entities]


def fetch_predictions(eids):
    predictions = {}
    for eid in eids:
        request_str = BASE_URL + "prediction?model_id=" + fetch_model_id() + "&eid=" + str(eid)
        prediction = session.get(request_str).json()["output"]
        predictions[eid] = prediction
    return predictions


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


def fetch_importance():
    features = session.get(BASE_URL + "features").json()["features"]
    features_df = pd.DataFrame(features)
    features_df = features_df.set_index("name")

    importance = session.get(
        BASE_URL + "importance?model_id=" + fetch_model_id()
    ).json()
    importance_df = pd.DataFrame(importance)
    return pd.concat([features_df, importance_df], axis=1)


def fetch_categories():
    categories = session.get(BASE_URL + "categories").json()["categories"]
    return pd.DataFrame(categories)


def fetch_terms():
    context_id = session.get(BASE_URL + "contexts").json()["contexts"][0]["id"]
    return session.get(BASE_URL + "context/" + context_id).json()["context"]["terms"]
