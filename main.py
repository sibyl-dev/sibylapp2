import streamlit as st
from sibylapp2.pages import (
    Similar_Cases,
    Explore_a_Prediction,
    Compare_Cases,
    Understand_the_Model,
    Experiment_with_Changes,
    Settings,
)
from sibylapp2.view.utils import setup
from sibylapp2.compute.context import get_term

setup.setup_page(return_row_ids=True)

pages = {
    "Explore a Prediction": Explore_a_Prediction,
    "Similar %s" % get_term("Entity", plural=True): Similar_Cases,
    "Compare %s" % get_term("Entity", plural=True): Compare_Cases,
    "Experiment with Changes": Experiment_with_Changes,
    "Understand the Model": Understand_the_Model,
    "Settings": Settings,
}
page_select = st.sidebar.radio("Select an explanation", pages.keys())
st.sidebar.divider()

pages[page_select].main()
