import streamlit as st
from sibylapp2.pages import (
    Similar_Entities,
    Explore_a_Prediction,
    Compare_Entities,
    Understand_the_Model,
    Experiment_with_Changes,
    Settings,
)
from sibylapp2.view.utils import setup
from sibylapp2.compute.context import get_term
from sibylapp2 import config

setup.setup_page(return_row_ids=True)

pages = {
    "Explore a Prediction": Explore_a_Prediction,
    "Similar Entities": Similar_Entities,
    "Compare Entities": Compare_Entities,
    "Experiment with Changes": Experiment_with_Changes,
    "Understand the Model": Understand_the_Model,
    "Settings": Settings,
}

pages_to_show = config.get_pages_to_show()
if pages_to_show is "all":
    pages_to_show = pages.keys()


def rename_page(key):
    if key == "Similar Entities":
        return "Similar %s" % get_term("Entity", plural=True)
    if key == "Compare Entities":
        return "Compare %s" % get_term("Entity", plural=True)
    return key


# Select and rename pages from config
pages = {
    rename_page(key): (
        pages[key] if key in pages else st.sidebar.warning("Requested non-existent page %s" % key)
    )
    for key in pages_to_show
}

page_select = st.sidebar.radio("Select an explanation", pages.keys())
st.sidebar.divider()

pages[page_select].main()

# "Similar %s" % get_term("Entity", plural=True): Similar_Cases,
# "Compare %s" % get_term("Entity", plural=True): Compare_Cases,
