import streamlit as st
from streamlit_tree_select import tree_select

def render_tree(tree_data):
    selected = tree_select(tree_data)
    st.session_state["selected_keys"] = selected.get("checked", [])