import streamlit as st
from sibylapp2.compute import features
from sibylapp2.view.utils import filtering


def main():
    filtering.view_filtering()
    feature_table = features.get_features()

    if "categories" not in st.session_state:
        st.session_state["categories"] = list(feature_table["Category"].unique())

    def submit_new_category():
        if st.session_state["new_category"] in st.session_state["categories"]:
            st.toast("Category already exists", icon="⚠️")
            st.session_state["new_category"] = None
            return
        if not st.session_state["new_category"]:
            return
        st.session_state["categories"].append(st.session_state["new_category"])
        st.session_state["new_category"] = None

    st.text_input("Add a new category", key="new_category", on_change=submit_new_category)

    column_config = {
        "Category": st.column_config.SelectboxColumn(
            options=st.session_state["categories"],
            default=st.session_state["categories"][0],
            required=True,
        )
    }
    st.data_editor(
        feature_table,
        hide_index=True,
        use_container_width=True,
        key="feature_table",
        column_config=column_config,
    )
    button_col1, button_col2, _ = st.columns((1, 1, 5))
    button_col1.button("Reset changes", use_container_width=True)
    button_col2.button(
        "Save changes to database",
        use_container_width=True,
    )
