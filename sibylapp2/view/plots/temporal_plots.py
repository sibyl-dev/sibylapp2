import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from sibylapp2.compute.context import get_term
from sibylapp2.config import (
    PREDICTION_TYPE,
    PredType,
    get_color_scheme,
    pred_format_func,
    ROW_LABEL,
)


def plot_temporal_line_charts(
    df, value_df=None, y_label="Contribution", fig=None, secondary_y=False
):
    """
    Transform dataframe from wide form to long form for streamlit visualizations.

    Plot line charts for data.
    """
    pos_color = (
        "rgba(194, 17, 17, 1)" if get_color_scheme() == "Reversed" else "rgba(24, 74, 201, 1)"
    )
    neg_color = (
        "rgba(24, 74, 201, 1)" if get_color_scheme() == "Reversed" else "rgba(194, 17, 17, 1)"
    )

    if "Category" in df.columns:
        df = df.drop(columns="Category")
    df = df.set_index("Feature").transpose().reset_index(names=[ROW_LABEL])
    df = df.melt(
        id_vars=[ROW_LABEL],
        value_vars=set(df.columns) - {ROW_LABEL},
        var_name="feature",
        value_name=y_label,
    )

    if fig is None:
        fig = go.Figure()

    for feature in df["feature"].unique():
        df_feature = df[df["feature"] == feature]
        if value_df is not None:
            hovertemplate = (
                "<b>%{customdata[0]}</b><br>Lead time: %{x}<br>Contribution:"
                " %{y}<br>Value:%{customdata[0]}<extra></extra>"
            )
            customdata = np.stack((df_feature["feature"], value_df.loc[feature]), axis=-1)
        else:
            hovertemplate = (
                "<b>%{customdata[0]}</b><br>Lead time: %{x}<br>Contribution: %{y}<extra></extra>"
            )
            customdata = df_feature[["feature"]]
        color = "black"
        fig.add_trace(
            go.Scatter(
                x=df_feature[ROW_LABEL],
                y=df_feature[y_label],
                mode="lines+markers",
                name=feature,
                customdata=customdata,
                line=dict(color=color),
                hovertemplate=hovertemplate,
                legend="legend2",
            ),
            secondary_y=secondary_y,
        )
    fig.add_hline(y=0, secondary_y=secondary_y, line_color="purple", line_dash="dash")
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=df[ROW_LABEL],
            dtick=1,
        ),
        hoverdistance=50,
    )
    fig.update_yaxes(
        title_text=y_label,
        secondary_y=secondary_y,
        tickfont=dict(size=20),
        titlefont=dict(size=20),
        overlaying="y",
        side="right",
        anchor="x",
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

    if "label" in df.columns:
        section_dfs = {
            f"{pred_format_func(label)}": df[df["label"] == label]
            for label in df["label"].unique()
        }
    else:
        section_dfs = {get_term("Prediction"): df}

    for label in section_dfs:
        section_df = section_dfs[label]
        name = label

        if PREDICTION_TYPE != PredType.BOOLEAN:
            color = "rgba(183, 149, 230, .5)"
        else:
            if label > 0.5:
                color = pos_color
            else:
                color = neg_color

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
        # yaxis2=dict(
        #     title=yaxis2_label,
        #     tickfont=dict(size=20),
        #     titlefont=dict(size=20),
        #     overlaying="y",
        #     side="right",
        #     anchor="x",
        # ),
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
