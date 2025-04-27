import logging
from typing import List, Dict
import streamlit as st
from streamlit_tree_select import tree_select

from model.app_state import AppState


logger = logging.getLogger('coderetriever.tree_ui')

def render_tree(tree_data: List[Dict], state: AppState) -> None:
    """Render the tree selection component and manage its state.
    
    Args:
        tree_data (List[Dict]): The tree structure to display
    """
    logger.debug(f"Rendering tree with {len(tree_data)} items")
    
    st.markdown("## 🌳 Code Tree")
    
    selection = tree_select(tree_data)
    logger.debug(f"Tree selection: {selection}")

    checked = selection.get("checked", [])
    state.set_selected_keys(checked)