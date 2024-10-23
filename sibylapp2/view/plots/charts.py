import matplotlib.cm as cm
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from sibylapp2.compute.context import get_term
from sibylapp2.config import PREDICTION_TYPE, PredType, get_color_scheme, pred_format_func


def lighten(base, step):
    """
    Lighten a color by a number of steps.
    """
    if base.startswith("rgba"):
        color = base.split("(")[1].split(")")[0].split(",")
        color = [int(c) for c in color]
        color = [int(min(255, c + step)) for c in color]
        color = "rgba(%d, %d, %d, %d)" % (color[0], color[1], color[2], 1)
    else:
        color = base.lstrip("#")
        color = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
        color = tuple(int(min(255, c + step)) for c in color)
        color = "#%02x%02x%02x" % color
    return color


def interpolate(color1, color2, steps=10):
    """
    Interpolate between color1 and color2, both in rgba format, with the given number of steps
    """
    color1 = color1.split("(")[1].split(")")[0].split(",")
    color1 = [int(c) for c in color1]
    color2 = color2.split("(")[1].split(")")[0].split(",")
    color2 = [int(c) for c in color2]
    colors = []
    for i in range(steps):
        color = [int(color1[j] + (color2[j] - color1[j]) * i / steps) for j in range(3)]
        color = "rgba(%d, %d, %d, %d)" % (color[0], color[1], color[2], 1)
        colors.append(color)
    return colors


def plot_temporal_line_charts(
    df,
    value_df,
    fig=None,
    secondary_y=False,
):
    """
    Transform dataframe from wide form to long form for streamlit visualizations.

    Plot line charts for data.
    """
    if "Category" in df.columns:
        df = df.drop(columns="Category")
    df = df.set_index("Feature").transpose().reset_index(names=["time"])

    df = df.melt(
        id_vars=["time"],
        value_vars=set(df.columns) - set(["time"]),
        var_name="feature",
        value_name="contribution",
    )

    if fig is None:
        fig = go.Figure()

    features = df["feature"].unique()

    colors = [cm.viridis(i / len(features)) for i in range(len(features))]
    colors = [f"rgba({int(c[0]*255)}, {int(c[1]*255)}, {int(c[2]*255)}, 1)" for c in colors]

    for step, feature in enumerate(features):
        df_feature = df[df["feature"] == feature]
        values = value_df.loc[feature]
        color = colors[step]
        customdata = np.stack((df_feature["feature"], values), axis=-1)
        fig.add_trace(
            go.Scatter(
                x=df_feature["time"],
                y=df_feature["contribution"],
                mode="lines+markers",
                name=feature,
                customdata=customdata,
                line=dict(color=color),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>Lead time: %{x}<br>Contribution:"
                    " %{y}<br>Value:%{customdata[1]}<extra></extra>"
                ),
                legend="legend2",
            ),
            secondary_y=secondary_y,
        )
    fig.add_hline(y=0, secondary_y=secondary_y, line_color="purple", line_dash="dash")
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=df["time"],
            dtick=1,
        ),
        hoverdistance=50,
    )
    return fig


def plot_prediction_regions(df, fig=None, yaxis_range=None):
    """
    Plot predictions regions for the given dataframe. The dataframe must have these columns:
        - time
        - value
        - labels
    """
    pos_color = (
        "rgba(227, 143, 143, .5)"
        if get_color_scheme() == "Reversed"
        else "rgba(163, 217, 227, .5)"
    )
    neg_color = (
        "rgba(163, 217, 227, .5)"
        if get_color_scheme() == "Reversed"
        else "rgba(227, 143, 143, .5)"
    )
    if fig is None:
        fig = go.Figure()

    for label in df["label"].unique():
        section_df = df[df["label"] == label]

        if PREDICTION_TYPE != PredType.BOOLEAN:
            color = "rgba(183, 149, 230, .5)"
            name = get_term("Prediction")
        else:
            if label > 0.5:
                color = pos_color
            else:
                color = neg_color
            name = f"{pred_format_func(label)}"

        fig.add_trace(
            go.Bar(
                x=section_df["time"],
                y=section_df["value"],
                name=name,
                showlegend=True,
                legend="legend1",
                marker_color=color,
            )
        )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=df["time"],
            dtick=1,
        ),
        bargap=0.03,
    )
    if yaxis_range is not None:
        fig.update_yaxes(range=yaxis_range, secondary_y=False)

    return fig


def update_figure(
    fig: go.Figure,
    width=800,
    height=800,
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
        ),
        yaxis2=dict(
            title=yaxis2_label,
            tickfont=dict(size=20),
            titlefont=dict(size=20),
            overlaying="y",
            side="right",
            anchor="x",
        ),
        legend1=dict(
            x=0, y=-0.2, traceorder="normal", orientation="h", title=get_term("Prediction")
        ),
        legend2=dict(
            x=0,
            y=-0.3,
            traceorder="normal",
            orientation="h",
            title=get_term("Feature", plural=True),
        ),
    )
    return fig
