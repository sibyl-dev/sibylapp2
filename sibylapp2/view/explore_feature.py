import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_plotly_events import plotly_events

from sibylapp2 import config
from sibylapp2.compute import contributions
from sibylapp2.compute.context import get_term
from sibylapp2.view import feature_contribution


@st.cache_data(show_spinner="Generating distribution plot...")
def generate_feature_distribution_plot(eids, feature, model_id):
    _, value_dict = contributions.get_contributions(eids, model_id=model_id)
    data = pd.Series(value_dict[feature])

    if pd.api.types.is_numeric_dtype(pd.to_numeric(data, errors="ignore")):
        trace1 = go.Box(x=data, boxpoints="all", name="", marker_color="rgb(84, 31, 63)")
        fig = go.Figure(data=[trace1])
        fig.update_layout(title="Distributions for '%s'" % feature)
        return fig
    else:
        fig = px.pie(
            data,
            values=data.value_counts().values,
            names=data.value_counts().index,
            title="Distributions for '%s'" % feature,
        )
        return fig


@st.cache_data(show_spinner="Generating feature plot...")
def generate_feature_plot_data(eids, predictions, feature, model_id):
    contributions_df, values = contributions.get_contributions(eids, model_id=model_id)
    contributions_for_feature = contributions_df[feature]
    values_for_feature = values[feature]

    formatted_pred = {i: config.pred_format_func(predictions[i]) for i in predictions}
    # Adding the space after prediction as a hack to allow two columns with the same displayed name
    df = pd.concat(
        [
            pd.Series(predictions, name="Prediction "),
            pd.Series(formatted_pred, name="Prediction"),
        ],
        axis=1,
    )
    df["Value"] = values_for_feature
    df["Contribution"] = contributions_for_feature
    df["ID"] = df.index
    return df


def generate_feature_plot(eids, predictions, feature, model_id, discrete=False):
    # The data computation part of this function is separated out to address a bug with
    #   plotly_events when generating the fig with a cached function
    df = generate_feature_plot_data(eids, predictions, feature, model_id=model_id)
    hover_data = {
        "Contribution": ":.3f",
        "Value": True,
        "Prediction ": False,
        "Prediction": True,
        "ID": True,
    }
    color = "Prediction" if discrete else "Prediction "
    fig = px.scatter(
        df,
        x="Value",
        y="Contribution",
        color=color,
        color_continuous_scale="Brwnyl",
        category_orders={color: sorted(set(df[color]))},
        color_discrete_sequence=px.colors.qualitative.Bold,
        hover_data=hover_data,
    )
    fig.update_traces(opacity=0.7, marker=dict(size=10, line=dict(width=0.5, color="black")))
    return fig


def view(eids, predictions, feature, model_id, discrete=False):
    col1, col2 = st.columns(2)
    with col1:
        fig1 = generate_feature_plot(eids, predictions, feature, model_id, discrete)
        selected_index = plotly_events(fig1)
        fig2 = generate_feature_distribution_plot(eids, feature, model_id=model_id)
        st.plotly_chart(fig2)
    with col2:
        if len(selected_index) > 0:
            eid = eids[selected_index[0]["pointIndex"]]
            st.subheader(
                "Contributions for {entity} {eid}".format(entity=get_term("Entity"), eid=eid)
            )
            feature_contribution.view(eid, model_id, save_space=True, key="explore_feature")
        else:
            st.warning("Select a point in the plot to see all contributions!")


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "The **Explore a {feature_up}** tab lets you see how the model uses a"
            " specific {feature} in more detail. The plot on the left shows how much each value"
            " for the chosen {feature} contributes to the model's prediction across the training"
            " set, as well as the corresponding model predictions.".format(
                feature_up=get_term("Feature"), feature=get_term("Feature", lower=True)
            )
        )
        st.markdown(
            "The plot on the right shows how the values for the chosen {feature} varied across the"
            " training dataset. For numeric features, you will see a box-and-whiskers plot"
            " with some notable distribution values (hover for specifics). For categorical"
            " features, you will see a pie chart.".format(feature=get_term("Feature", lower=True))
        )
        st.markdown(
            "You can use the selector to visualize only rows in the training set with a"
            " subset of prediction values"
        )
