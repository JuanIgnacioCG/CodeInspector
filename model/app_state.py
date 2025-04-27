from dataclasses import dataclass, field
from pathlib import Path
import streamlit as st

@dataclass
class AppState:
    selected_folder: Path = field(default_factory=lambda: Path(".").resolve())
    selected_keys: list = field(default_factory=list)

    @classmethod
    def load(cls) -> "AppState":
        """Load or initialize the AppState from session_state."""
        if "app_state" not in st.session_state:
            st.session_state.app_state = cls()
        return st.session_state.app_state

    def set_folder(self, folder_str: str):
        """Validate and set a new selected folder."""
        try:
            path = Path(folder_str).expanduser().resolve()
            if path.is_dir():
                self.selected_folder = path
            else:
                st.warning(f"⚠️ The folder {path} does not exist.")
        except Exception as e:
            st.error(f"❌ Invalid path: {e}")

    def set_selected_keys(self, keys: list):
        self.selected_keys = keys
