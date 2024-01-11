import pandas as pd
import plotly.express as px


def plot_temporal_line_charts(df: pd.DataFrame, y_max=1.0, y_min=-1.0, x_max=30, x_min=0):
    """
    Transform dataframe from wide form to long form for streamlit visualizations.

    Plot line charts for data.
    """
    df = df.set_index("Feature").transpose().reset_index(names=["time"])

    df = df.melt(
        id_vars=["time"],
        value_vars=set(df.columns) - set(["time"]),
        var_name="feature",
        value_name="contribution",
    )
    fig = px.line(
        df,
        x="time",
        y="contribution",
        color="feature",
        symbol="feature",
        labels={"contribution": "Feature contribution", "time": "Lead time (days)"},
        title="Feature contribution for predictions at different lead time",
    )
    fig.update_layout(
        showlegend=False,
        xaxis={
            "tickmode": "linear",
            "tick0": 0,
            "dtick": 1,
            "tickfont": {"size": 20},
            "titlefont": {"size": 20},
        },
        yaxis={"tickfont": {"size": 20}, "titlefont": {"size": 20}},
        xaxis_range=[x_min, x_max],
        yaxis_range=[y_min, y_max],
    )
    return fig


def plot_scatter_chart(
    df: pd.DataFrame = None,
    x: list = None,
    y: list = None,
    y_max=1.0,
    y_min=0.0,
    x_max=30,
    x_min=0,
):
    """
    Plot scatter plot for the given dataframe
    """
    # Validate input arguments
    if df is None and (x is None or y is None):
        raise ValueError("Must provide a dataframe or lists for x and y axis to this function")

    if df is None:
        fig = px.scatter(x=x, y=y)
    else:
        fig = px.scatter(
            df,
            x="time",
            y="value",
            color="labels",
            labels={
                "time": "Lead time (days)",
                "value": "Prediction value",
                "labels": "Prediction outcome",
            },
            title="Prediction at different lead time",
        )
    fig.update_layout(
        showlegend=False,
        xaxis={
            "tickmode": "linear",
            "tick0": 0,
            "dtick": 1,
            "tickfont": {"size": 20},
            "titlefont": {"size": 20},
        },
        yaxis={"tickfont": {"size": 20}, "titlefont": {"size": 20}},
        xaxis_range=[x_min, x_max],
        yaxis_range=[y_min, y_max],
    )
    fig.update_traces(marker_size=10)

    return fig
