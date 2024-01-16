import pandas as pd
import plotly.express as px


def plot_temporal_line_charts(
    df: pd.DataFrame,
    width=800,
    height=800,
    y_max=1.0,
    y_min=-1.0,
    x_max=30,
    x_min=0,
    chart_labels={},
):
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
        labels=chart_labels,
        title="Feature contribution for predictions at different lead time",
    )
    fig.update_layout(
        width=width,
        height=height,
        xaxis_range=[x_min, x_max],
        yaxis_range=[y_min, y_max],
        xaxis={
            "tickmode": "array",
            "tickvals": df["time"],
            "dtick": 1,
            "tickfont": {"size": 20},
            "titlefont": {"size": 20},
        },
        yaxis={"tickfont": {"size": 20}, "titlefont": {"size": 20}},
    )
    return fig


def plot_scatter_chart(
    df: pd.DataFrame,
    width=800,
    height=800,
    y_max=1.0,
    y_min=0.0,
    x_max=30,
    x_min=0,
    y_margin=0.2,
    chart_labels={},
):
    """
    Plot scatter plot for the given dataframe. The dataframe must have the following columns:
        - time
        - value
        - labels
    """
    fig = px.scatter(
        df,
        x="time",
        y="value",
        color="labels",
        labels=chart_labels,
        title="Prediction at different lead time",
    )
    fig.update_layout(
        width=width,
        height=height,
        xaxis_range=[x_min, x_max],
        yaxis_range=[y_min - y_margin, y_max + y_margin],
        xaxis={
            "tickmode": "array",
            "tickvals": df["time"],
            "dtick": 1,
            "tickfont": {"size": 20},
            "titlefont": {"size": 20},
        },
        yaxis={"tick0": y_min, "tickfont": {"size": 20}, "titlefont": {"size": 20}},
    )
    fig.update_traces(marker_size=10)

    return fig
