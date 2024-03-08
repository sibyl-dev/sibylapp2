# pylint: disable=invalid-name

import streamlit as st

from sibylapp2.compute import context, features, importance
from sibylapp2.compute.api import format_feature_df_for_modify, modify_features
from sibylapp2.view.utils import filtering


def view_instructions():
    with st.sidebar.expander("How to Use"):
        st.write(
            "On this page you can add and edit feature categories, and modify feature descriptions"
        )


def submit_new_category():
    if st.session_state["new_category"] in st.session_state["categories"]:
        st.toast("Category already exists", icon="⚠️")
        st.session_state["new_category"] = None
        return
    if not st.session_state["new_category"]:
        return
    st.session_state["categories"].append(st.session_state["new_category"])
    st.session_state["new_category"] = None
    st.toast("Added category successfully", icon="✅")


def apply_changes():
    if "feature_table_changes" in st.session_state:
        changes = st.session_state["feature_table_changes"]["edited_rows"]
        for row in changes:
            for col in changes[row]:
                st.session_state["edited_table"].iloc[row][col] = changes[row][col]
                st.session_state["changes_made"] = True


def main():
    view_instructions()

    if "changes_made" not in st.session_state:
        st.session_state["changes_made"] = False
    filtering.view_filtering()
    feature_table = features.get_features()
    if "edited_table" not in st.session_state:
        st.session_state["edited_table"] = feature_table.copy()

    if "categories" not in st.session_state:
        st.session_state["categories"] = list(feature_table["Category"].unique())

    st.text_input("Add a new category", key="new_category", on_change=submit_new_category)

    column_config = {
        "Category": st.column_config.SelectboxColumn(
            options=st.session_state["categories"],
            default=st.session_state["categories"][0],
            required=True,
        )
    }
    st.data_editor(
        filtering.process_options(st.session_state["edited_table"]),
        hide_index=True,
        use_container_width=True,
        key="feature_table_changes",
        column_config=column_config,
        on_change=apply_changes,
    )

    def reset_changes():
        st.session_state["edited_table"] = feature_table.copy()
        st.session_state["changes_made"] = False

    def save_changes():
        modify_features(format_feature_df_for_modify(st.session_state["edited_table"].copy()))
        features.get_features.clear()
        importance.compute_importance.clear()
        context.get_category_list.clear()
        st.session_state["changes_made"] = False
        del st.session_state["feature_table_changes"]

    button_col1, button_col2, _ = st.columns((1, 1, 5))
    button_col1.button(
        "Reset changes",
        use_container_width=True,
        disabled=not st.session_state["changes_made"],
        on_click=reset_changes,
    )
    button_col2.button(
        "Save changes to database",
        use_container_width=True,
        disabled=not st.session_state["changes_made"],
        on_click=save_changes,
    )
