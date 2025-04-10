import streamlit as st

from model.state import init_state
from logic.tree_builder import build_tree_data
from view.sidebar import render_sidebar
from view.tree_ui import render_tree
from view.snippets_display import render_snippets

init_state()
render_sidebar()

folder = st.session_state["selected_folder"]
if folder and folder.exists():
    tree_data = build_tree_data(folder)
    render_tree(tree_data)
    render_snippets(st.session_state["selected_keys"], folder)
else:
    st.info("Select a folder to begin")