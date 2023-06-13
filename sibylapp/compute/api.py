from sibylapp.config import BASE_URL, CERT
import requests
import pandas as pd
import streamlit as st

session = requests.Session()
session.headers.update({"Access-Control-Allow-Origin": "*"})
if CERT is not None:
    session.cert = CERT


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
    model_id = api_get("models/")["models"][0]["id"]
    return model_id


def fetch_eids():
    entities = api_get("entities/")["entities"]
    return [entry["eid"] for entry in entities]


def fetch_predictions(eids):
    json = {"eids": eids, "model_id": fetch_model_id()}
    predictions = api_post("multi_prediction/", json)["predictions"]
    return predictions


def fetch_features():
    features = api_get("features/")["features"]
    features_df = pd.DataFrame(features).rename(columns={"description": "Feature Name"})
    features_df = features_df.set_index("name")
    return features_df


def fetch_entity(eid):
    url = "entities/" + str(eid)
    entity_features = api_get(url)["features"]
    return pd.Series(entity_features, name="value")


def fetch_contributions(eids):
    features_df = fetch_features()
    json = {"eids": eids, "model_id": fetch_model_id()}
    result = api_post("multi_contributions/", json)["contributions"]
    contributions = {}
    for eid in result:
        contributions[eid] = pd.concat(
            [features_df, pd.read_json(result[eid], orient="index")], axis=1
        )
    return contributions


def fetch_importance():
    features_df = fetch_features()
    url = "importance?model_id=" + fetch_model_id()
    importance = api_get(url)
    importance_df = pd.DataFrame(importance)
    return pd.concat([features_df, importance_df], axis=1)


def fetch_similar_examples(eids):
    features_df = fetch_features()
    json = {"eids": eids, "model_id": fetch_model_id()}
    result = api_post("similar_entities/", json)["similar_entities"]
    similar_entities = {}
    for eid in result:
        y = pd.read_json(result[eid]["y"], orient="index")
        X = pd.concat(
                [
                    features_df[["Feature Name", "category"]],
                    pd.read_json(result[eid]["X"], orient="index").T,
                ],
                axis=1,
            )
        X.columns = X.columns.astype(str)
        y.index = y.index.map(str)
        if str(eid) not in X:
            X = pd.concat([X, fetch_entity(eid)], axis=1)
            y[eid] = "N/A"
        similar_entities[eid] = {
            "X": X,
            "y": y,
        }
    return similar_entities


def fetch_categories():
    categories = api_get("categories/")["categories"]
    return pd.DataFrame(categories)


def fetch_terms():
    context_id = api_get("contexts/")["contexts"][0]["id"]
    url = "context/" + context_id
    return api_get(url)["context"]["terms"]
