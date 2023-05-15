from sibylapp.config import BASE_URL
import requests
import pandas as pd
import streamlit as st

session = requests.Session()
cache = {}


def fetch_model_id():
    if "model_id" in cache:
        return cache["model_id"]
    model_id = session.get(BASE_URL + "models").json()["models"][0]["id"]
    cache["model_id"] = model_id
    return model_id


def fetch_eids():
    response = session.get(BASE_URL + "entities")
    if response.status_code != 200:
        st.error("Error fetching eids. %s: %s" % (response.status_code, response.reason))
        st.stop()
    entities = response.json()["entities"]
    return [entry["eid"] for entry in entities]


def fetch_predictions(eids):
    predictions = {}
    for eid in eids:
        request_str = (
            BASE_URL + "prediction?model_id=" + fetch_model_id() + "&eid=" + str(eid)
        )
        prediction = session.get(request_str).json()["output"]
        predictions[eid] = prediction
    return predictions


def fetch_features():
    if "features" in cache:
        return cache["features"]
    features = session.get(BASE_URL + "features").json()["features"]
    features_df = pd.DataFrame(features)
    features_df = features_df.set_index("name")
    cache["features"] = features_df
    return features_df


def fetch_entity(eid):
    entity_features = session.get(BASE_URL + "entities/" + str(eid)).json()["features"]
    return pd.Series(entity_features, name="value")


def fetch_contributions(eids):
    features_df = fetch_features()

    results = {}
    for eid in eids:
        json = {"eid": eid, "model_id": fetch_model_id()}

        contributions = session.post(BASE_URL + "contributions", json=json).json()
        contribution_df = pd.DataFrame(contributions)
        feature_values = fetch_entity(eid)
        result = pd.concat([features_df, feature_values, contribution_df], axis=1)
        results[eid] = result
    return results


def fetch_importance():
    features_df = fetch_features()

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
