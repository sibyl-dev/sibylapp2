import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from sibylapp2.config import NEGATIVE_TERM, POSITIVE_TERM
from sibylapp2.view.utils.helpers import get_pos_neg_names
from sibylapp2.config import pred_format_func, PREDICTION_TYPE, get_color_scheme, PredType
from sibylapp2.compute.context import get_term


def plot_temporal_line_charts(
    df,
    fig=None,
    secondary_y=False,
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
    traces = px.line(
        df,
        x="time",
        y="contribution",
        color="feature",
        markers=True,
        color_discrete_sequence=px.colors.sequential.gray,
    ).data
    for trace in traces:
        fig.add_trace(trace, secondary_y=secondary_y)
    fig.add_hline(y=0, secondary_y=secondary_y, line_color="purple", line_dash="dash")
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=df["time"],
            dtick=1,
        ),
        hoverdistance=20,
    )
    return fig


def plot_scatter_chart(df, fig=None):
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
            name = f"{get_term('Prediction')}: {pred_format_func(label)}"
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
            ),
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
            # range=[y_min - y_margin, y_max + y_margin],
        ),
        yaxis2=dict(
            title=yaxis2_label,
            tickfont=dict(size=20),
            titlefont=dict(size=20),
            overlaying="y",
            side="right",
            anchor="x",
            # range=[y_min - y_margin, y_max + y_margin],
        ),
        legend=dict(x=0, y=-0.2, traceorder="normal", orientation="h"),
    )
    return fig
