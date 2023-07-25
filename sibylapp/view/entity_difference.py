import streamlit as st

from sibylapp.config import pred_format_func
from sibylapp.compute import contributions, model
from sibylapp.compute.context import get_term
from sibylapp.view.feature_contribution import show_legend
from sibylapp.view.utils import filtering, helpers


def view_compare_entities_select():
    def format_func(s):
        return f"{get_term('Entity')} {s} (" + pred_format_func(predictions[s]) + ")"

    predictions = model.get_predictions(st.session_state["eids"])

    if "eid" in st.session_state:
        st.session_state["select_eid_index"] = st.session_state["eids"].index(
            st.session_state["eid"]
        )
    else:
        st.session_state["select_eid_index"] = 0

    if "eid_comp" in st.session_state:
        st.session_state["select_eid_comp_index"] = st.session_state["eids"].index(
            st.session_state["eid_comp"]
        )
    else:
        st.session_state["select_eid_comp_index"] = 0

    st.session_state["eid"] = st.sidebar.selectbox(
        "Select %s #1" % get_term("Entity"),
        st.session_state["eids"],
        format_func=format_func,
        index=st.session_state["select_eid_index"],
    )
    pred = predictions[st.session_state["eid"]]
    st.sidebar.metric(
        "%s for %s #1" % (get_term("Prediction"), get_term("Entity")), pred_format_func(pred)
    )

    st.session_state["eid_comp"] = st.sidebar.selectbox(
        "Select %s #2" % get_term("Entity"),
        st.session_state["eids"],
        format_func=format_func,
        index=st.session_state["select_eid_comp_index"],
    )
    pred = predictions[st.session_state["eid_comp"]]
    st.sidebar.metric(
        "%s for %s #2" % (get_term("Prediction"), get_term("Entity")), pred_format_func(pred)
    )


def show_sorted_contributions(to_show, sort_by):
    show_legend()
    if sort_by == "Absolute Difference":
        to_show = to_show.reindex(
            to_show["Contribution Change Value"].abs().sort_values(ascending=False).index
        )
    if sort_by == "Ascending":
        to_show = to_show.sort_values(by="Contribution Change Value", axis="index")
    if sort_by == "Descending":
        to_show = to_show.sort_values(
            by="Contribution Change Value", axis="index", ascending=False
        )
    to_show = filtering.process_options(to_show)
    helpers.show_table(to_show.drop("Contribution Change Value", axis="columns"))


def format_two_contributions_to_view(df1, df2, show_number=False, show_contribution=True):
    original_df = df1.rename(
        columns={
            "category": "Category",
            "Feature Value": "Value",
        }
    )
    original_df = original_df[["Category", "Feature", "Value", "Contribution"]]
    original_df["Contribution Value"] = original_df["Contribution"].copy()
    original_df["Contribution"] = helpers.generate_bars(
        original_df["Contribution"], show_number=show_number
    )

    other_df = df2.rename(
        columns={
            "Feature Value": "Value",
        }
    )
    other_df = other_df[["Value", "Contribution"]]
    other_df["Contribution Value"] = other_df["Contribution"].copy()
    other_df["Contribution"] = helpers.generate_bars(
        other_df["Contribution"], show_number=show_number
    )

    compare_df = original_df.join(
        other_df[["Value", "Contribution", "Contribution Value"]],
        lsuffix=" of %s #1" % get_term("Entity"),
        rsuffix=" of %s #2" % get_term("Entity"),
    )
    compare_df["Contribution Change"] = (
        other_df["Contribution Value"] - original_df["Contribution Value"]
    )
    compare_df["Contribution Change Value"] = compare_df["Contribution Change"].copy()
    compare_df["Contribution Change"] = helpers.generate_bars(
        compare_df["Contribution Change"], show_number=show_number
    )

    if not show_contribution:
        compare_df.drop(
            [
                "Contribution of %s #1" % get_term("Entity"),
                "Contribution of %s #2" % get_term("Entity"),
                "Contribution Value of %s #1" % get_term("Entity"),
                "Contribution Value of %s #2" % get_term("Entity"),
            ]
        )
    return compare_df


def filter_different_rows(to_show):
    neighbor_col = to_show["Value of %s #1" % get_term("Entity")]
    selected_col = to_show["Value of %s #2" % get_term("Entity")]
    to_show_filtered = to_show[neighbor_col != selected_col]
    return to_show_filtered


def view(eid, eid_comp, save_space=False):
    show_number = False

    if not save_space:
        cols = st.columns(2)
        with cols[0]:
            sort_by = helpers.show_sort_options(["Absolute Difference", "Ascending", "Descending"])
        with cols[1]:
            show_number = st.checkbox(
                "Show numeric contributions?",
                help="Show the exact amount this feature contributes to the model prediction",
            )
    else:
        cols = st.columns(1)
        with cols[0]:
            sort_by = helpers.show_sort_options(["Absolute Difference", "Ascending", "Descending"])
    contributions_dict = contributions.get_contributions([eid, eid_comp])
    contribution_original = contributions_dict[eid]
    contribution_compare = contributions_dict[eid_comp]
    to_show = format_two_contributions_to_view(
        contribution_original, contribution_compare, show_number=show_number
    )
    show_sorted_contributions(to_show, sort_by)
    options = ["No filtering", "With filtering"]
    show_different = st.radio(
        "Apply filtering by differences?",
        options,
        horizontal=True,
        help="Show only rows where value differs from selected",
    )
    if show_different == "With filtering":
        to_show = filter_different_rows(to_show)

    helpers.show_table(to_show)


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "This page compares the **{feature} values** and **{feature} contributions**"
            " of two distinct {entities}.".format(
                entities=get_term("Entity", l=True, p=True), feature=get_term("Feature", l=True)
            )
        )
        positive, negative = helpers.get_pos_neg_names()
        st.markdown(
            "A large **{positive}** bar means that this {feature}'s value significantly increased"
            " the model's prediction on this {entity}. A large **{negative}** bar means that this"
            " {feature}'s value significantly decreased the model's prediction. A lack of a bar"
            " suggests this {feature} had little effect on the model's prediction in this case."
            .format(
                positive=positive,
                negative=negative,
                feature=get_term("Feature").lower(),
                entity=get_term("Entity").lower(),
            )
        )
        st.markdown(
            "You can select {a_entity} from the dropdown above, and see the {feature}"
            " contributions. You can also **filter** and **search** the {feature} table or adjust"
            " the **sort order**.".format(
                a_entity=get_term("Entity", a=True, l=True),
                feature=get_term("Feature", l=True),
            )
        )
