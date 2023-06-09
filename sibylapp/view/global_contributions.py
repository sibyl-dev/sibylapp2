import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from pyreal.visualize import swarm_plot

from sibylapp.compute import contributions
from sibylapp.compute.context import get_term
from sibylapp.view.utils import filtering, helpers


@st.cache_data(show_spinner="Generating plot...")
def generate_swarm_plot(contribution_dict):
    swarm_plot(contribution_dict, type="strip")
    return plt.gcf()


def view_summary_plot(contribution_dict):
    st.pyplot(
        generate_swarm_plot(helpers.rename_for_pyreal_vis(contribution_dict)),
        clear_figure=True,
    )


def view(all_contributions):
    sort_by = st.selectbox("Sort order", ["Total", "Most Increasing", "Most Decreasing"])

    global_contributions = contributions.compute_global_contributions(all_contributions)
    bars = helpers.generate_bars_bidirectional(
        global_contributions["negative"], global_contributions["positive"]
    )
    feature_info = all_contributions[next(iter(all_contributions))][
        ["category", "Feature"]
    ].rename(columns={"category": "Category"})
    to_show = pd.concat([feature_info, bars, global_contributions], axis="columns")

    if sort_by == "Total":
        to_show = to_show.reindex(
            (to_show["negative"].abs() + to_show["positive"]).sort_values(ascending=False).index
        )
    if sort_by == "Most Increasing":
        to_show = to_show.sort_values(by="positive", axis="index", ascending=False)
    if sort_by == "Most Decreasing":
        to_show = to_show.sort_values(by="negative", axis="index")

    to_show = filtering.process_options(to_show).drop(["positive", "negative"], axis=1)
    helpers.show_table(to_show)
    return to_show


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        positive, negative = helpers.get_pos_neg_names()
        st.markdown(
            "**Global {feature_contributions}** show how each {feature} tends to contribute to the"
            " model prediction overall across the training dataset. Each row shows the average"
            " positive and negative contribution for that {feature}.".format(
                feature_contributions=get_term("Feature Contributions"),
                feature=get_term("Feature", l=True),
            )
        )
        st.markdown(
            "For example, a large **{pos}** bar without a **{neg}** bar means this {feature} often"
            " greatly increases the model prediction, and never decreases it. A large **{pos}**"
            " bar and a large **{neg}** bar means this {feature} can both increase and decrease"
            " the model prediction, depending on its value and the context.".format(
                feature=get_term("Feature", l=True), pos=positive, neg=negative
            )
        )
        st.markdown(
            "You can **filter** and **search** the {feature} table or adjust the **sort order**."
            " You can also use the selector to visualize the contributions for rows in the dataset"
            " with only a select subset of predictions.".format(
                feature=get_term("Feature", l=True)
            )
        )
