import os
import ast
import streamlit as st
from streamlit_tree_select import tree_select
from pathlib import Path
from typing import List, Tuple
from collections import defaultdict


st.set_page_config(page_title="Code Snippet Extractor", page_icon="🧠", layout="wide")

# ---------- Utilities ----------
def find_python_files(base_dir: str) -> List[str]:
    return [str(p) for p in Path(base_dir).rglob("*.py")]

def extract_definitions(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source, filename=file_path)

        definitions = []

        class DefinitionVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                definitions.append((
                    str(Path(file_path).resolve()), 
                    node.name, node.lineno, node.end_lineno, 'def'))
                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node):
                definitions.append((file_path, node.name, node.lineno, node.end_lineno, 'async def'))
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                definitions.append((file_path, node.name, node.lineno, node.end_lineno, 'class'))
                self.generic_visit(node)

        DefinitionVisitor().visit(tree)
        return definitions

    except (SyntaxError, UnicodeDecodeError) as e:
        return f"❌ Error parsing {file_path}: {e}"

def extract_source(file_path: str, lineno: int, end_lineno: int) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return ''.join(lines[lineno-1:end_lineno])

def build_tree_data(base_dir):
    base = Path(base_dir)
    tree = {}

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                full_path = Path(root) / file
                rel_path = full_path.relative_to(base)
                parts = rel_path.parts

                current = tree
                for part in parts[:-1]:
                    current = current.setdefault(part, {})

                # Now we're at the file level
                file_node = current.setdefault(parts[-1], {})

                try:
                    defs = extract_definitions(full_path)
                    if isinstance(defs, str):  # error message
                        file_node["__error__"] = defs
                    else:
                        file_node["__functions__"] = [
                            {
                                "name": f"{kind} {name}",
                                "path": str(full_path),
                                "key": f"{full_path}::{name}",
                                "lineno": lineno,
                                "end_lineno": end_lineno,
                                "kind": kind
                            }
                            for full_path, name, lineno, end_lineno, kind in defs
                        ]
                except Exception as e:
                    print(f"❌ Error parsing {full_path}: {e}")

    def build_node(name, subtree, parent_path=""):
        if name == "__functions__":
            return [ 
                {
                    "label": f["name"],  # Human-readable name
                    "value": f'{str(Path(f["path"]).resolve())}::{f["name"]}:{f["lineno"]}',
                    "key": f'{f["key"]}:{f["lineno"]}'
                }
                for f in subtree
            ]
        if name == "__error__":
            return [{"label": subtree, "value": parent_path + "/__error__", "disabled": True}]

        children = []
        for k, v in subtree.items():
            path = os.path.join(parent_path, k)
            if k == "__functions__":
                children.extend(build_node(k, v, parent_path))
            else:
                children.append({
                    "label": k,
                    "value": path,  # Full path as unique identifier
                    "children": build_node(k, v, path)
                })
        return children


    return [{
        "label": base.name,
        "value": str(base.resolve()),  # Unique base path
        "children": build_node(base.name, tree, str(base.resolve()))
    }]

# UI
st.title("📦 Code Snippet Extractor for LLM")
base_dir = st.text_input("Enter the base directory to scan:", "./nerfstudio")

if os.path.isdir(base_dir):
    tree_data = build_tree_data(base_dir)
    selected = tree_select(tree_data)
    
    st.markdown("### ✅ Selected Items")
    for item in selected["checked"]:
        st.write(item)

    # ----------- Display Code Blocks -----------
    if selected["checked"]:
        st.markdown("## 🧠 Extracted Code Snippets")

        def_key_lookup = {}

        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    defs = extract_definitions(full_path)
                    if isinstance(defs, list):
                        for file_path, name, lineno, end_lineno, kind in defs:
                            key = f"{file_path}::{kind} {name}:{lineno}"
                            def_key_lookup[key] = (file_path, name, lineno, end_lineno, kind)

        all_snippets = []  # List to store all code snippets for combined output

        for key in selected["checked"]:
            if "::" not in key:
                continue

            lookup_key = key

            if lookup_key in def_key_lookup:
                file_path, name, start, end, kind = def_key_lookup[lookup_key]
                try:
                    code = extract_source(file_path, start, end)
                    snippet_header = f"{kind} {name}\n{file_path}:{start}-{end}\n\n"
                    snippet_body = f"{code}\n"
                    full_snippet = snippet_header + snippet_body
                    all_snippets.append(full_snippet)

                    # Display snippet individually (nice for visualization)
                    st.markdown(f"### `{kind} {name}`")
                    st.markdown(f"*{file_path}:{start}-{end}*")
                    st.code(code, language='python')

                except Exception as e:
                    st.warning(f"Could not extract {lookup_key}: {e}")
            else:
                st.warning(f"Definition not found for {lookup_key}")

        # Display combined snippets for single copy-paste convenience
        combined_code = "\n\n".join(all_snippets)
        st.markdown("## 📋 Combined Snippets for Easy Copy-Paste")
        st.code(combined_code, language='python')