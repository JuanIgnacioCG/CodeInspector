import streamlit as st
import logging

from utils.logging_config import setup_logging
from model.app_state import AppState
from logic.tree_builder import TreeBuilder
from view.sidebar import render_sidebar
from view.tree_ui import render_tree
from view.snippets_display import render_snippets
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("coderetriever.app")

def main():
    logger.info("Starting CodeRetriever application")
    
    # Initialize state
    state = AppState.load()
    logger.debug(f"Initial state: selected_folder={state.selected_folder}")
    
    # Render UI components
    render_sidebar(state)
    logger.debug(f"Sidebar rendered with folder: {state.selected_folder}")

    if state.selected_folder.exists():
        # Build and render tree
        logger.info(f"Building tree for folder: {state.selected_folder}")
        builder = TreeBuilder(state.selected_folder)
        tree_data = builder.build_tree()
        logger.debug(f"Tree built with {len(tree_data)} root nodes")
        
        render_tree(tree_data, state)
        logger.debug(f"Tree rendered, selected keys: {state.selected_keys}")
        
        # Use state for rendering snippets
        if state.selected_keys:
            logger.info(f"Rendering snippets for {len(state.selected_keys)} selections")
            render_snippets(state.selected_keys, state.selected_folder)
        else:
            logger.warning("No keys selected for snippet display")
    else:
        logger.info("Waiting for folder selection")
        st.info("Select a folder to begin")

if __name__ == "__main__":
    main()