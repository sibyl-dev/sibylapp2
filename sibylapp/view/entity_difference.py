import streamlit as st

from sibylapp.compute import contributions, model
from sibylapp.compute.context import get_term
from sibylapp.config import pred_format_func
from sibylapp.view.feature_contribution import show_legend
from sibylapp.view.utils import filtering, helpers


def view_other_entity_select():
    def format_func(s):
        return f"{get_term('Entity')} {s} (" + pred_format_func(predictions[s]) + ")"

    predictions = model.get_predictions(st.session_state["eids"])

    if "eid_comp" in st.session_state:
        st.session_state["select_eid_comp_index"] = st.session_state["eids"].index(
            st.session_state["eid_comp"]
        )
    else:
        st.session_state["select_eid_comp_index"] = 1

    st.session_state["eid_comp"] = st.sidebar.selectbox(
        "Select %s #2" % get_term("Entity"),
        st.session_state["eids"],
        format_func=format_func,
        index=st.session_state["select_eid_comp_index"],
    )

    pred_new = predictions[st.session_state["eid_comp"]]
    st.sidebar.metric(
        "%s for %s #2" % (get_term("Prediction"), get_term("Entity")), pred_format_func(pred_new)
    )


def view_prediction_difference():
    predictions = model.get_predictions(st.session_state["eids"])
    difference = predictions[st.session_state["eid_comp"]] - predictions[st.session_state["eid"]]
    st.metric(
        "{prediction} Difference between {entity} #2 and {entity} #1:".format(
            prediction=get_term("Prediction"), entity=get_term("Entity")
        ),
        pred_format_func(difference),
    )


def show_sorted_contributions(to_show, sort_by):
    show_legend()
    if sort_by == "Absolute Difference":
        to_show = to_show.reindex(
            to_show["Contribution Change Value"].abs().sort_values(ascending=False).index
        )
    if sort_by == "Positive Difference":
        to_show = to_show.sort_values(
            by="Contribution Change Value", axis="index", ascending=False
        )
    if sort_by == "Negative Difference":
        to_show = to_show.sort_values(by="Contribution Change Value", axis="index")

    to_show = filtering.process_options(to_show)
    helpers.show_table(to_show.drop("Contribution Change Value", axis="columns"))


def format_two_contributions_to_view(df1, df2, show_number=False, show_contribution=False):
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
        lsuffix=" for %s #1" % get_term("Entity"),
        rsuffix=" for %s #2" % get_term("Entity"),
    )
    compare_df = compare_df.rename(
        columns={
            "Value for %s #1"
            % get_term("Entity"): "%s Value for %s #1" % (get_term("Feature"), get_term("Entity")),
            "Value for %s #2"
            % get_term("Entity"): "%s Value for %s #2" % (get_term("Feature"), get_term("Entity")),
        }
    )
    compare_df["Contribution Change"] = (
        other_df["Contribution Value"] - original_df["Contribution Value"]
    )
    compare_df["Contribution Change Value"] = compare_df["Contribution Change"].copy()
    compare_df["Contribution Change"] = helpers.generate_bars(
        compare_df["Contribution Change"], show_number=show_number
    )

    if not show_contribution:
        compare_df = compare_df.drop(
            [
                "Contribution for %s #1" % get_term("Entity"),
                "Contribution for %s #2" % get_term("Entity"),
                "Contribution Value for %s #1" % get_term("Entity"),
                "Contribution Value for %s #2" % get_term("Entity"),
            ],
            axis="columns",
        )
    return compare_df


def filter_different_rows(to_show):
    neighbor_col = to_show["%s Value for %s #1" % (get_term("Feature"), get_term("Entity"))]
    selected_col = to_show["%s Value for %s #2" % (get_term("Feature"), get_term("Entity"))]
    to_show_filtered = to_show[neighbor_col == selected_col]
    return to_show_filtered


def view(eid, eid_comp, save_space=False):
    show_number = False

    if not save_space:
        cols = st.columns(2)
        with cols[0]:
            sort_by = helpers.show_sort_options(
                ["Absolute Difference", "Positive Difference", "Negative Difference"]
            )
        with cols[1]:
            show_number = st.checkbox(
                "Show numeric contributions?",
                help="Show the exact amount this feature contributes to the model prediction",
            )
            show_contriubtion = st.checkbox(
                "Show original contributions?",
                help="Show the original %s contributions for both %s"
                % (get_term("Feature"), get_term("Entity", p=True)),
            )
    else:
        cols = st.columns(1)
        with cols[0]:
            sort_by = helpers.show_sort_options(
                ["Absolute Difference", "Positive Difference", "Negative Difference"]
            )

    contributions_dict = contributions.get_contributions([eid, eid_comp])
    contribution_original = contributions_dict[eid]
    contribution_compare = contributions_dict[eid_comp]
    to_show = format_two_contributions_to_view(
        contribution_original,
        contribution_compare,
        show_number=show_number,
        show_contribution=show_contriubtion,
    )

    options = ["No filtering", "With filtering"]
    show_different = st.radio(
        "Apply filtering by identical %s values?" % get_term("Feature", l=True),
        options,
        horizontal=True,
        help="Show only rows where %s values of two %s are identical"
        % (get_term("Feature", l=True), get_term("Entity", l=True, p=True)),
    )
    if show_different == "With filtering":
        to_show = filter_different_rows(to_show)

    show_sorted_contributions(to_show, sort_by)


def view_instructions():
    expander = st.sidebar.expander("How to Use")
    with expander:
        st.markdown(
            "This page compares the **{feature} values** and **{feature} contributions**"
            " of two distinct {entities}."
            "You can select two {entities} you want to compare from the dropdown above.".format(
                entities=get_term("Entity", p=True, l=True),
                feature=get_term("Feature", l=True),
            )
        )
        positive, negative = helpers.get_pos_neg_names()
        st.markdown(
            "The **Contribution Change** column refers to the difference between the {feature}"
            " contribution of the two {entities}.A large **{positive}** bar means that this"
            " {feature}'s value has a much more positive contribution to the model's prediction on"
            " {entity} #2 than on {entity} #1. A large **{negative}** bar means that this"
            " {feature}'s value has a much more negative contribution to the model's prediction on"
            " {entity} #2 than on {entity} #1. A lack of a bar suggests this {feature} had little"
            " effect on the model's prediction in this case.".format(
                positive=positive,
                negative=negative,
                feature=get_term("Feature", l=True),
                entity=get_term("Entity", l=True),
                entities=get_term("Entity", l=True, p=True),
            )
        )
        st.markdown(
            "You can **filter** and **search** the {feature} table or adjust"
            " the **sort order**. You can also look at {features} with identical"
            " {feature} values.".format(
                feature=get_term("Feature", l=True),
                features=get_term("Feature", p=True, l=True),
            )
        )
