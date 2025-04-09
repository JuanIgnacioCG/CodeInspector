import os
import ast
import streamlit as st
from streamlit_tree_select import tree_select
from pathlib import Path
from typing import List

st.set_page_config(page_title="Code Snippet Extractor", page_icon="🧠", layout="wide")

# ---------- Utilities ----------
def extract_definitions(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source, filename=file_path)

        definitions = []

        class Visitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                definitions.append((file_path, node.name, node.lineno, node.end_lineno, 'def'))
                self.generic_visit(node)
            def visit_AsyncFunctionDef(self, node):
                definitions.append((file_path, node.name, node.lineno, node.end_lineno, 'async def'))
                self.generic_visit(node)
            def visit_ClassDef(self, node):
                definitions.append((file_path, node.name, node.lineno, node.end_lineno, 'class'))
                self.generic_visit(node)

        Visitor().visit(tree)
        return definitions
    except Exception as e:
        return f"❌ Error parsing {file_path}: {e}"

def extract_source(file_path: str, lineno: int, end_lineno: int) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return ''.join(f.readlines()[lineno-1:end_lineno])

def build_tree_data(base_dir: Path):
    base = base_dir.resolve()
    tree = {}

    for root, _, files in os.walk(base):
        for file in files:
            if file.endswith(".py"):
                full_path = Path(root) / file
                rel_path = full_path.relative_to(base)
                parts = rel_path.parts
                current = tree
                for part in parts[:-1]:
                    current = current.setdefault(part, {})
                file_node = current.setdefault(parts[-1], {})

                defs = extract_definitions(full_path)
                rel_path = Path(full_path).relative_to(base)
                if isinstance(defs, str):
                    file_node["__error__"] = defs
                else:
                    file_node["__functions__"] = [
                        {
                            "name": f"{kind} {name}",
                            "path": str(full_path),
                            "key": f"{rel_path}::{name}:{lineno}",
                            "lineno": lineno,
                            "end_lineno": end_lineno,
                            "kind": kind
                        }
                        for _, name, lineno, end_lineno, kind in defs
                    ]

    def build_node(name, subtree, parent_path=""):
        if name == "__functions__":
            return [
                {"label": f["name"], "value": f["key"], "key": f["key"]}
                for f in subtree
            ]
        if name == "__error__":
            return [{"label": subtree, "value": parent_path + "/__error__", "disabled": True}]
        return [
            {"label": k, "value": os.path.join(parent_path, k), "children": build_node(k, v, os.path.join(parent_path, k))}
            for k, v in subtree.items()
        ]

    return [{"label": base.name, "value": str(base), "children": build_node(base.name, tree, str(base))}]

# ---------------------- UI ------------------------
st.sidebar.title("📁 Select Folder")
base_dir_input = st.sidebar.text_input("Enter base directory:", str(Path.cwd() / 'nerfstudio'))

try:
    base_path = Path(base_dir_input).expanduser().resolve(strict=False)
except Exception:
    st.error("❌ Invalid path provided.")
    base_path = None

st.title("📦 Code Snippet Extractor for LLM")

if base_path and base_path.is_dir():
    tree_data = build_tree_data(base_path)
    selected = tree_select(tree_data)

    if selected["checked"]:
        st.markdown("## 🧠 Extracted Code Snippets")
        snippets = []

        for key in selected["checked"]:
            if "::" not in key or ":" not in key:
                continue
            try:
                rel_path_str, name_lineno = key.split("::")
                name, lineno = name_lineno.rsplit(":", 1)

                abs_path = str(Path(base_path) / rel_path_str)

                defs = extract_definitions(abs_path)
                if isinstance(defs, list):
                    for path, def_name, start, end, kind in defs:
                        if def_name == name and str(start) == lineno:
                            code = extract_source(path, start, end)
                            snippets.append(f"{kind} {def_name}\n{path}:{start}-{end}\n{code}")
                            # st.markdown(f"### `{kind} {def_name}`")
                            # st.markdown(f"*{path}:{start}-{end}*")
                            # st.code(code, language='python')
            except Exception as e:
                st.warning(f"⚠️ Error processing {key}: {e}")

        if snippets:
            st.markdown("## 📋 Combined Snippets for Easy Copy-Paste")
            st.code("\n\n".join(snippets), language='python')
else:
    st.info("📂 Please select a valid folder from the sidebar.")
