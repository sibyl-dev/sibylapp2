import streamlit as st
from sibylapp.context import get_term
from sibylapp.entities import get_eids


def generate_feature_plot(feature):
   pass


def view(features):
    st.selectbox("Select a %s" % get_term("feature"), features)