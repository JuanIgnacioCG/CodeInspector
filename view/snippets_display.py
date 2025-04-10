import streamlit as st
from pathlib import Path
from logic.extractor import extract_definitions, extract_source

def render_snippets(selected_keys, base_path: Path):
    if not selected_keys:
        return

    st.markdown("## 🧠 Extracted Code Snippets")
    snippets = []

    for key in selected_keys:
        if "::" not in key or ":" not in key:
            continue

        try:
            rel_path_str, name_lineno = key.split("::")
            name, lineno = name_lineno.rsplit(":", 1)
            abs_path = base_path / rel_path_str

            defs = extract_definitions(abs_path)
            if isinstance(defs, list):
                for path, def_name, start, end, kind in defs:
                    if def_name == name and str(start) == lineno:
                        code = extract_source(path, start, end)
                        snippet = f"{kind} {def_name}\n{path}:{start}-{end}\n{code}"
                        snippets.append(snippet)

                        # Individual display
                        # st.markdown(f"### `{kind} {def_name}`")
                        # st.markdown(f"*{path}:{start}-{end}*")
                        # st.code(code, language='python')

        except Exception as e:
            st.warning(f"⚠️ Error processing `{key}`: {e}")

    if snippets:
        st.markdown("## 📋 Combined Snippets for Easy Copy-Paste")
        st.code("\n\n".join(snippets), language='python')
