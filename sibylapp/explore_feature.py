import streamlit as st
from sibylapp import api
from sibylapp.context import get_term
from sibylapp.helpers import process_options


def view(features):
    st.selectbox("Select a %s" % get_term("feature"), features)