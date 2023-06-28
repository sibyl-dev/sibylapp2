import streamlit as st
from sibylapp.view.utils import filtering, setup
from sibylapp.view import explore_feature, feature_importance, global_contributions
from sibylapp.compute.context import get_term
from sibylapp.compute import model, contributions
import extra_streamlit_components as stx


setup.setup_page()

# Global options ------------------------------
filtering.view_filtering()

# Compute -------------------------------------
predictions = model.get_dataset_predictions()
all_contributions = contributions.get_dataset_contributions()

# Setup tabs ----------------------------------
pred_filter_container = st.container()

tab = stx.tab_bar(
    data=[
        stx.TabBarItemData(id=1, title=get_term("Feature Importance"), description=""),
        stx.TabBarItemData(
            id=2, title="Global %s" % get_term("Feature Contributions"), description=""
        ),
        stx.TabBarItemData(id=3, title="Summary Plot", description=""),
        stx.TabBarItemData(
            id=4, title="Explore a %s" % get_term("Feature"), description=""
        ),
    ],
    default=1,
)

# Sidebar --------------------------------------
if tab == "1":
    feature_importance.view_instructions()

if tab == "2":
    global_contributions.view_instructions()

if tab == "4":
    explore_feature.view_instructions()

st.session_state["disabled"] = tab == "1"

# Prediction filtering -------------------------
with pred_filter_container:
    if "disabled" not in st.session_state:
        st.session_state["disabled"] = True
    eids = filtering.view_prediction_selection(
        predictions, disabled=st.session_state["disabled"]
    )
    filtered_contributions = filtering.filter_eids(eids, all_contributions)
    filtered_predictions = filtering.filter_eids(eids, predictions)

placeholder = st.container()
features = all_contributions[next(iter(all_contributions))]["Feature"]

if tab == "1":
    with placeholder:
        feature_importance.view()

if tab == "2":
    with placeholder:
        if len(eids) == 0:
            st.warning("Select predictions above to see explanation!")
        else:
            global_contributions.view(filtered_contributions)

if tab == "3":
    if len(eids) == 0:
        st.warning("Select predictions above to see explanation!")
    else:
        global_contributions.view_summary_plot(filtered_contributions)

if tab == "4":
    with placeholder:
        if len(eids) == 0:
            st.warning("Select predictions above to see explanation!")
        else:
            feature = st.selectbox(
                "Select a %s" % get_term("feature"),
                filtering.process_search_on_features(features),
            )
            col1, col2 = st.columns(2)
            with col1:
                explore_feature.view(
                    filtered_contributions, filtered_predictions, feature
                )
            with col2:
                global_contributions.view_feature_plot(filtered_contributions, feature)
