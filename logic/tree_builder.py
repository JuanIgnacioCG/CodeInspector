import os
from pathlib import Path
from logic.extractor import extract_definitions
from model.types import TreeDict

def build_tree_data(base_dir: Path) -> TreeDict:
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
