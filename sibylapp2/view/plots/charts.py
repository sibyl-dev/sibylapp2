import pandas as pd
import plotly.graph_objects as go

from sibylapp2.config import NEGATIVE_TERM, POSITIVE_TERM


def plot_temporal_line_charts(
    df: pd.DataFrame,
    fig: go.Figure | None = None,
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
    if fig is None:
        fig = go.Figure()

    for feature in df["feature"].unique():
        df_feature = df[df["feature"] == feature]
        fig.add_trace(
            go.Scatter(
                x=df_feature["time"],
                y=df_feature["contribution"],
                mode="lines+markers",
                name=feature,
                yaxis="y2",
            )
        )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=df["time"],
            dtick=1,
        ),
    )
    return fig


def plot_scatter_chart(
    df: pd.DataFrame,
    fig: go.Figure | None = None,
):
    """
    Plot scatter plot for the given dataframe. The dataframe must have the following columns:
        - time
        - value
        - labels
    """
    # Change this when positive and negative colors are defined
    color_map = {POSITIVE_TERM: "blue", NEGATIVE_TERM: "red"}
    if fig is None:
        fig = go.Figure()

    for label in df["labels"].unique():
        df_label = df[df["labels"] == label]
        colors = [color_map[lab] for lab in df_label["labels"]]
        fig.add_trace(
            go.Scatter(
                x=df_label["time"],
                y=df_label["value"],
                mode="markers",
                name=label,
                marker=dict(color=colors, size=20),
                yaxis="y1",
            )
        )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=df["time"],
            dtick=1,
        ),
    )

    return fig


def update_figure(
    fig: go.Figure,
    width=800,
    height=800,
    y_min=-1.0,
    y_max=1.0,
    y_margin=0.1,
    xaxis_label="",
    yaxis_label="",
    yaxis2_label="",
):
    fig.update_layout(
        width=width,
        height=height,
        title="Feature contribution for predictions at different lead time",
        xaxis=dict(
            title=xaxis_label,
            tickfont=dict(size=20),
            titlefont=dict(size=20),
        ),
        yaxis=dict(
            title=yaxis_label,
            tickfont=dict(size=20),
            titlefont=dict(size=20),
            anchor="x",
            range=[y_min - y_margin, y_max + y_margin],
        ),
        yaxis2=dict(
            title=yaxis2_label,
            tickfont=dict(size=20),
            titlefont=dict(size=20),
            overlaying="y",
            side="right",
            anchor="x",
            range=[y_min - y_margin, y_max + y_margin],
        ),
        legend=dict(x=0, y=-0.2, traceorder="normal", orientation="h"),
    )
    return fig
