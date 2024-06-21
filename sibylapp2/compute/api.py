import json as json_encoder
from os import path

import pandas as pd
import requests
import streamlit as st
import yaml

# from sibylapp2.config import ENABLE_LOGGING

with open(path.join(path.dirname(path.dirname(path.abspath(__file__))), "config.yml"), "r") as f:
    cfg = yaml.safe_load(f)

session = requests.Session()
session.headers.update({"Access-Control-Allow-Origin": "*"})
if cfg.get("CERT") is not None:
    cert_string = cfg.get("CERT")
    cert = cert_string.split(",")
    session.cert = cert


def api_get(url):
    fetch_url = cfg["BASE_URL"] + url
    try:
        response = session.get(fetch_url)
    except requests.exceptions.RequestException as err:
        st.error(f"Connection error. Please check your connection and refresh the page ({err})")
        st.stop()
    if response.status_code != 200:
        st.error(
            "Error with request (%s) %s: %s" % (fetch_url, response.status_code, response.reason)
        )
        st.stop()
    return response.json()


def api_post(url, json=None, data=None):
    fetch_url = cfg["BASE_URL"] + url
    try:
        if data:
            response = session.post(
                fetch_url, data=data, headers={"Content-Type": "application/json"}
            )
        else:
            response = session.post(fetch_url, json=json)
    except requests.exceptions.RequestException as err:
        st.write(fetch_url, json)
        st.error(f"Connection error. Please check your connection and refresh the page ({err})")
        st.stop()
    if response.status_code != 200:
        st.error(
            "Error with request (%s) %s: %s" % (fetch_url, response.status_code, response.reason)
        )
        st.stop()
    return response.json()


def api_put(url, json=None, data=None):
    fetch_url = cfg["BASE_URL"] + url
    try:
        if data:
            response = session.put(
                fetch_url, data=data, headers={"Content-Type": "application/json"}
            )
        else:
            response = session.put(fetch_url, json=json)
    except requests.exceptions.RequestException as err:
        st.error(f"Connection error. Please check your connection and refresh the page ({err})")
        st.stop()
    if response.status_code != 200:
        st.error(
            "Error with request (%s) %s: %s" % (fetch_url, response.status_code, response.reason)
        )
        st.stop()
    return response.json()


def fetch_models():
    models = api_get("models/")["models"]
    return [model["model_id"] for model in models]


def fetch_model_id():
    model_id = api_get("models/")["models"][0]["model_id"]
    return model_id


def fetch_eids():
    """
    Return corresponding row_ids in the form of a dictionary where the keys are the eids
    and the values are the lists of row_ids for each eid, when specified.
    """
    return api_get("entities/")["entities"]


def fetch_modified_prediction(
    eid, changes, row_id=None, model_id=fetch_model_id(), return_proba=False
):
    json = {
        "eid": eid,
        "row_id": row_id,
        "model_id": model_id,
        "changes": changes,
        "return_proba": return_proba,
    }
    prediction = api_post("modified_prediction/", data=json_encoder.dumps(json))["prediction"]
    return prediction


def fetch_predictions(eids, row_ids=None, model_id=fetch_model_id(), return_proba=False):
    json = {
        "eids": eids,
        "model_id": model_id,
        "row_ids": row_ids,
        "return_proba": return_proba,
    }
    predictions = api_post("multi_prediction/", json)["predictions"]
    return predictions


def fetch_features():
    features = api_get("features/")["features"]
    features_df = pd.DataFrame(features).rename(
        columns={
            "description": "Feature",
            "category": "Category",
            "type": "Type",
            "values": "Values",
        }
    )
    features_df = features_df.set_index("name")
    return features_df


def format_feature_df_for_modify(features_df):
    """
    Formats a dataframe to for use in modify_features

    Args:
        features_df (DataFrame): Dataframe of features to be modified.
            Includes the following columns (case-insensitive):
            - [index]: Feature name
            - Feature: Feature description
            - Category: Feature category
            - Type: Feature type
    """
    features_df["name"] = features_df.index
    features_df.columns = features_df.columns.str.lower()
    features_df["description"] = features_df["feature"]
    features_df = features_df[
        [col for col in ["name", "category", "description", "type"] if col in features_df.columns]
    ]
    return features_df.to_dict(orient="records")


def modify_features(new_features):
    """
    Put new_features in the database.

    Args:
        new_features (dict): Dictionary of feature name to feature information, including:
            - name (required): Feature name
            - description: Feature description
            - category: Feature category
            - type: Feature type
            - values: Feature values (if categorical)

    Returns:
        None
    """
    api_put("features/", json={"features": new_features})


def fetch_entity(eid, row_id=None):
    url = f"entities/{eid}"
    if row_id is not None:
        url += f"/?row_id={row_id}"
    entity_features = api_get(url)["features"]
    if row_id is not None:
        return pd.Series(entity_features)
    else:
        return pd.Series(next(iter(entity_features.values())), name="value")


def fetch_contributions(eids, row_ids=None, model_id=fetch_model_id()):
    json = {"eids": eids, "model_id": model_id, "row_ids": row_ids}
    result = api_post("multi_contributions/", json)
    contributions = pd.DataFrame.from_dict(result["contributions"], orient="index")
    values = pd.DataFrame.from_dict(result["values"], orient="index")
    return contributions, values


def fetch_contribution_for_modified_data(eid, changes, row_id=None, model_id=fetch_model_id()):
    json = {"eid": eid, "row_id": row_id, "model_id": model_id, "changes": changes}
    result = api_post("modified_contribution/", data=json_encoder.dumps(json))
    contributions = pd.DataFrame.from_dict(result["contributions"], orient="index")
    values = pd.DataFrame.from_dict(result["values"], orient="index")
    return contributions, values


def fetch_importance(model_id=fetch_model_id()):
    features_df = fetch_features()
    url = "importance?model_id=" + model_id
    importance = api_get(url)
    importance_df = pd.DataFrame(importance)
    return pd.concat([features_df, importance_df], axis=1)


def fetch_similar_examples(eids, model_id=fetch_model_id()):
    features_df = fetch_features()
    json = {"eids": eids, "model_id": model_id}
    result = api_post("similar_entities/", json)["similar_entities"]
    similar_entities = {}
    for eid in result:
        y = pd.Series(result[eid]["y"]).to_frame().T
        X = pd.concat(
            [
                features_df,
                pd.DataFrame.from_dict(result[eid]["X"], orient="index").T,
            ],
            axis=1,
        )
        X.columns = X.columns.astype(str)
        y.columns = y.columns.astype(str)
        if str(eid) not in X:
            X = pd.concat([X, fetch_entity(eid)], axis=1)
        y[str(eid)] = "N/A"
        similar_entities[eid] = {
            "X": X,
            "y": y,
        }
    return similar_entities


def fetch_categories():
    categories = api_get("categories/")["categories"]
    return pd.DataFrame(categories)


def fetch_context():
    context_id = api_get("contexts/")["contexts"][0]["context_id"]
    url = "context/" + context_id
    return api_get(url)["context"]


def log(
    timestamp,
    user_id=None,
    eid=None,
    action=None,
    element=None,
    details=None,
    interface=None,
):
    """
    Log an action in the system
    Args:
        timestamp (int):
            Time of the action.
        user_id (str):
            ID of the user that took the action
        eid (str):
            Entity ID the action was taken on
        action (str):
            Action taken
        element (str):
            Element the action was taken on
        details (dict):
            Details of the action
        interface (str):
            Interface the action was taken on
    """
    json = {
        "timestamp": timestamp,
        "user_id": user_id,
        "eid": eid,
        "event": {
            "action": action,
            "element": element,
            "details": details,
            "interface": interface,
        },
    }
    api_post("log/", json)
