from os import path

import pandas as pd
import requests
import streamlit as st
import yaml

with open(path.join(path.dirname(path.dirname(path.abspath(__file__))), "config.yml"), "r") as f:
    cfg = yaml.safe_load(f)

session = requests.Session()
session.headers.update({"Access-Control-Allow-Origin": "*"})
if cfg.get("CERT") is not None:
    session.cert = cfg.get("CERT")


def api_get(url):
    fetch_url = cfg["BASE_URL"] + url
    response = session.get(fetch_url)
    if response.status_code != 200:
        st.error("Error with GET(%s). %s: %s" % (fetch_url, response.status_code, response.reason))
        st.stop()
    return response.json()


def api_post(url, json):
    fetch_url = cfg["BASE_URL"] + url
    response = session.post(fetch_url, json=json)
    if response.status_code != 200:
        st.error(
            "Error with POST(%s). %s: %s" % (fetch_url, response.status_code, response.reason)
        )
        st.stop()
    return response.json()


def fetch_models():
    models = api_get("models/")["models"]
    return [model["model_id"] for model in models]


def fetch_model_id():
    model_id = api_get("models/")["models"][0]["model_id"]
    return model_id


def fetch_eids(
    max_entities=None,
    return_row_ids=False,
):
    """
    Return corresponding row_ids in the form of a dictionary where the keys are the eids
    and the values are the lists of row_ids for each eid, when specified.
    """
    entities = api_get("entities/")["entities"]
    if max_entities is not None:
        entities = entities[:max_entities]
    if return_row_ids:
        return [entry["eid"] for entry in entities], {
            entry["eid"]: entry["row_ids"] for entry in entities
        }
    else:
        return [entry["eid"] for entry in entities]


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
    prediction = api_post("modified_prediction/", json)["prediction"]
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
        columns={"description": "Feature", "category": "Category", "type": "Type"}
    )
    features_df = features_df.set_index("name")
    return features_df


def fetch_entity(eid, row_id=None) -> pd.Series:
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
    result = api_post("modified_contribution/", json)
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
    context_id = api_get("contexts/")["contexts"][0]["id"]
    url = "context/" + context_id
    return api_get(url)["context"]
