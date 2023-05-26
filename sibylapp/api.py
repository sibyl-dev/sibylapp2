from sibylapp.config import BASE_URL, CERT
import requests
import pandas as pd
import streamlit as st

session = requests.Session()
session.headers.update({"Access-Control-Allow-Origin": "*"})
if CERT is not None:
    session.cert = CERT
cache = {}


def api_get(url):
    fetch_url = BASE_URL + url
    response = session.get(fetch_url)
    if response.status_code != 200:
        st.error(
            "Error with GET(%s). %s: %s"
            % (fetch_url, response.status_code, response.reason)
        )
        st.stop()
    return response.json()


def api_post(url, json):
    fetch_url = BASE_URL + url
    response = session.post(fetch_url, json=json)
    if response.status_code != 200:
        st.error(
            "Error with POST(%s). %s: %s"
            % (fetch_url, response.status_code, response.reason)
        )
        st.stop()
    return response.json()


def fetch_model_id():
    if "model_id" in cache:
        return cache["model_id"]
    model_id = api_get("models/")["models"][0]["id"]
    cache["model_id"] = model_id
    return model_id


def fetch_eids():
    entities = api_get("entities/")["entities"]
    return [entry["eid"] for entry in entities]


def fetch_predictions(eids):
    predictions = {}
    for eid in eids:
        url = "prediction?model_id=" + fetch_model_id() + "&eid=" + str(eid)
        prediction = api_get(url)["output"]
        predictions[eid] = prediction
    return predictions


def fetch_features():
    if "features" in cache:
        return cache["features"]
    features = api_get("features/")["features"]
    features_df = pd.DataFrame(features)
    features_df = features_df.set_index("name")
    cache["features"] = features_df
    return features_df


def fetch_entity(eid):
    url = "entities/" + str(eid)
    entity_features = api_get(url)["features"]
    return pd.Series(entity_features, name="value")


def fetch_contributions(eids):
    features_df = fetch_features()

    results = {}
    for eid in eids:
        json = {"eid": eid, "model_id": fetch_model_id()}
        contributions = api_post("contributions/", json)
        contribution_df = pd.DataFrame(contributions)
        feature_values = fetch_entity(eid)
        result = pd.concat([features_df, feature_values, contribution_df], axis=1)
        results[eid] = result
    return results


def fetch_importance():
    features_df = fetch_features()
    url = "importance?model_id=" + fetch_model_id()
    importance = api_get(url)
    importance_df = pd.DataFrame(importance)
    return pd.concat([features_df, importance_df], axis=1)


def fetch_categories():
    categories = api_get("categories/")["categories"]
    return pd.DataFrame(categories)


def fetch_terms():
    context_id = api_get("contexts/")["contexts"][0]["id"]
    url = "context/" + context_id
    return api_get(url)["context"]["terms"]
