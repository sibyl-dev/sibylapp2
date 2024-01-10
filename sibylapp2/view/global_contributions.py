import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from pyreal.visualize import strip_plot

from sibylapp2.compute import contributions, features
from sibylapp2.compute.context import get_term
from sibylapp2.view.utils import filtering, helpers
from sibylapp2.view.utils.helpers import show_legend


@st.cache_data(show_spinner="Generating summary plot...")
def generate_swarm_plot(eids, model_id):
    contribution_dict = helpers.rename_for_pyreal_vis(
        contributions.get_contributions(eids, model_id)
    )
    strip_plot(contribution_dict, type="strip")
    return plt.gcf()


def view_summary_plot(eids, model_id):
    st.pyplot(
        generate_swarm_plot(eids, model_id),
        clear_figure=True,
    )


def view(eids, model_id):
    sort_by = helpers.show_sort_options(["Total", get_term("Positive"), get_term("Negative")])
    show_legend()

    global_contributions = contributions.compute_global_contributions(eids, model_id)
    bars = helpers.generate_bars_bidirectional(
        global_contributions["negative"], global_contributions["positive"]
    )

    feature_info = features.get_features().rename(columns={"category": "Category"})
    to_show = pd.concat([feature_info, bars, global_contributions], axis="columns")

    if sort_by == "Total":
        to_show = to_show.reindex(
            (to_show["negative"].abs() + to_show["positive"]).sort_values(ascending=False).index
        )
    if sort_by == get_term("Positive"):
        to_show = to_show.sort_values(by="positive", axis="index", ascending=False)
        to_show = to_show[to_show["positive"] > 0]
    if sort_by == get_term("Negative"):
        to_show = to_show.sort_values(by="negative", axis="index")
        to_show = to_show[to_show["negative"] < 0]

    to_show = filtering.process_options(to_show).drop(["positive", "negative"], axis=1)
    helpers.show_table(to_show, key="global")
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
                feature=get_term("feature"),
            )
        )
        st.markdown(
            "For example, a large **{pos}** bar without a **{neg}** bar means this"
            " {feature} often greatly increases the model prediction, and never decreases it. A"
            " large **{pos}** bar and a large **{neg}** bar means this {feature} can both"
            " increase and decrease the model prediction, depending on its value and the context."
            .format(feature=get_term("feature"), pos=positive, neg=negative)
        )
        st.markdown(
            "You can **filter** and **search** the {feature} table or adjust the **sort order**."
            " You can also use the selector to visualize the contributions for rows in the dataset"
            " with only a select subset of predictions.".format(feature=get_term("feature"))
        )
