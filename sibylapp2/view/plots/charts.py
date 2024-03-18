import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from sibylapp2.compute.context import get_term
from sibylapp2.config import PREDICTION_TYPE, PredType, get_color_scheme, pred_format_func


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
    pos_color = (
        "rgba(194, 17, 17, 1)" if get_color_scheme() == "Reversed" else "rgba(24, 74, 201, 1)"
    )
    neg_color = (
        "rgba(24, 74, 201, 1)" if get_color_scheme() == "Reversed" else "rgba(194, 17, 17, 1)"
    )

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

    for feature in df["feature"].unique():
        df_feature = df[df["feature"] == feature]
        values = value_df.loc[feature]
        if df_feature["contribution"].mean() > 0:
            color = pos_color
        else:
            color = neg_color
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

    # traces = px.line(
    #     df,
    #     x="time",
    #     y="contribution",
    #     color="feature",
    #     markers=True,
    #     color_discrete_sequence=px.colors.sequential.gray,
    # ).data
    # for trace in traces:
    #     trace.legend = "legend2"
    #     fig.add_trace(trace, secondary_y=secondary_y)
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


def plot_scatter_chart(df, fig=None, yaxis_range=None):
    """
    Plot scatter plot for the given dataframe. The dataframe must have the following columns:
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

    change_indices = df[df["label"] != df["label"].shift(1)].index.tolist()
    change_indices.append(len(df))
    shown_legends = []
    for i in range(len(change_indices) - 1):
        start_idx = change_indices[i]
        end_idx = change_indices[i + 1]
        section_df = df[start_idx:end_idx]
        if i < len(change_indices) - 2:
            next_section_start = df.iloc[[end_idx]]
            section_df = pd.concat([section_df, next_section_start])

        label = section_df["label"].iloc[0]

        if PREDICTION_TYPE != PredType.BOOLEAN:
            color = "rgba(183, 149, 230, .5)"
            name = get_term("Prediction")
            showlegend = i == 0
        else:
            if label > 0.5:
                color = pos_color
            else:
                color = neg_color
            name = f"{pred_format_func(label)}"
            if label in shown_legends:
                showlegend = False
            else:
                showlegend = True
                shown_legends.append(label)
        # color = "blue" if label == "normal" else "red"

        fig.add_trace(
            go.Scatter(
                x=section_df["time"],
                y=section_df["value"],
                name=name,
                fill="tozeroy",
                fillcolor=color,
                mode="none",
                showlegend=showlegend,
                legend="legend1",
            ),
        )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=df["time"],
            dtick=1,
        ),
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
