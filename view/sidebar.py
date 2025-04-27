import streamlit as st
from model.app_state import AppState

def render_sidebar(state: AppState) -> None:
    """Render the sidebar with folder selection.
    
    Args:
        state (AppState): The application state instance
    """
    st.sidebar.markdown("## 📂 Select a base folder to explore")

    folder_input = st.sidebar.text_input(
        "Enter base folder:", 
        value=str(state.selected_folder)
    )
    
    if folder_input != str(state.selected_folder):
        state.set_folder(folder_input)

    st.sidebar.markdown(f"**Current folder:** `{state.selected_folder}`")