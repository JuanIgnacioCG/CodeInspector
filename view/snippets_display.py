from dataclasses import dataclass
from typing import Optional, List
import streamlit as st
from pathlib import Path
from logic.extractor import extract_definitions, extract_source

@dataclass
class CodeSnippet:
    kind: str
    name: str
    path: Path
    start: int
    end: int
    code: str

    def format(self) -> str:
        return f"{self.kind} {self.name}\n{self.path}:{self.start}-{self.end}\n{self.code}"

@dataclass
class SnippetKey:
    filepath: str
    name: str
    line_number: str

    @classmethod
    def parse(cls, key: str) -> Optional['SnippetKey']:
        if not "::" in key or not ":" in key:
            return None
        try:
            filepath, name_lineno = key.split("::")
            name, lineno = name_lineno.rsplit(":", 1)
            return cls(filepath, name, lineno)
        except ValueError:
            return None

def render_snippets(selected_keys: List[str], base_path: Path) -> None:
    """Main function to render code snippets."""
    if not selected_keys:
        return

    st.markdown("## 🧠 Extracted Code Snippets")
    snippets = extract_snippets(selected_keys, base_path)
    if snippets:
        display_snippets(snippets)

def extract_snippets(keys: List[str], base_path: Path) -> List[CodeSnippet]:
    """Extract all valid snippets from the given keys."""
    return [
        snippet for key in keys
        if (parsed_key := SnippetKey.parse(key)) is not None
        if (snippet := find_snippet(parsed_key, base_path)) is not None
    ]

def find_snippet(key: SnippetKey, base_path: Path) -> Optional[CodeSnippet]:
    """Find and extract a single snippet based on the key."""
    try:
        abs_path = base_path / key.filepath
        definitions = extract_definitions(abs_path)
        
        if not isinstance(definitions, list):
            return None

        for path, def_name, start, end, kind in definitions:
            if def_name == key.name and str(start) == key.line_number:
                code = extract_source(path, start, end)
                return CodeSnippet(kind, def_name, path, start, end, code)
                
    except Exception as e:
        st.warning(f"⚠️ Error processing snippet: {e}")
        return None

def display_snippets(snippets: List[CodeSnippet]) -> None:
    """Display the formatted snippets."""
    st.markdown("## 📋 Combined Snippets for Easy Copy-Paste")
    formatted_snippets = [snippet.format() for snippet in snippets]
    st.code("\n\n".join(formatted_snippets), language='python')