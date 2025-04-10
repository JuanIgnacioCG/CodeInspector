import streamlit as st

def init_state():
    st.session_state.setdefault("selected_folder", None)
    st.session_state.setdefault("selected_keys", [])

