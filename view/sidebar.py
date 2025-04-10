import streamlit as st
from pathlib import Path

def render_sidebar():
    st.sidebar.markdown("Select a base folder to start exploring your codebase.")
    folder = st.sidebar.text_input("Enter base folder", value=str(Path.cwd()))
    st.session_state["selected_folder"] = Path(folder)
