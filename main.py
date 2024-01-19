import streamlit as st

from sibylapp2.compute.context import get_term
from sibylapp2.config import get_pages_to_show
from sibylapp2.pages import (
    # Compare_Entities,
    # Experiment_with_Changes,
    Explore_a_Prediction,
    # Settings,
    # Similar_Entities,
    # Understand_the_Model,
)
from sibylapp2.view.utils import setup

setup.setup_page(return_row_ids=True)

ALL_PAGES = {
    "Explore a Prediction": Explore_a_Prediction,
    # "Similar Entities": Similar_Entities,
    # "Compare Entities": Compare_Entities,
    # "Experiment with Changes": Experiment_with_Changes,
    # "Understand the Model": Understand_the_Model,
    # "Settings": Settings,
}

pages_to_show = get_pages_to_show()
if pages_to_show == "all":
    pages_to_show = ALL_PAGES.keys()


def rename_page(key):
    if key == "Similar Entities":
        return "Similar %s" % get_term("Entity", plural=True)
    if key == "Compare Entities":
        return "Compare %s" % get_term("Entity", plural=True)
    return key


# Select and rename pages from config
pages = {
    rename_page(key): (
        ALL_PAGES[key]
        if key in ALL_PAGES
        else st.sidebar.warning("Requested non-existent page %s" % key)
    )
    for key in pages_to_show
}

page_select = st.sidebar.radio("Select an explanation", pages.keys())
st.sidebar.divider()

pages[page_select].main()
