from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Iterator
import os
from logic.extractor import extract_definitions
from model.types import TreeDict

@dataclass
class FunctionNode:
    """Represents a function definition in a Python file."""
    name: str
    path: Path
    lineno: int
    end_lineno: int
    kind: str

    @property
    def key(self) -> str:
        return f"{self.path}::{self.name}:{self.lineno}"

    def to_tree_item(self) -> Dict:
        return {
            "label": f"{self.kind} {self.name}",
            "value": self.key,
            "key": self.key
        }

@dataclass
class FileNode:
    """Represents a Python file with its functions and potential errors."""
    path: Path
    base_path: Path
    functions: List[FunctionNode]
    error: Optional[str] = None

    @property
    def rel_path(self) -> Path:
        return self.path.relative_to(self.base_path)

    @classmethod
    def from_path(cls, path: Path, base_path: Path) -> 'FileNode':
        """Create a FileNode from a path, extracting all function definitions."""
        defs = extract_definitions(path)
        if isinstance(defs, str):
            return cls(path, base_path, [], error=defs)
            
        functions = [
            FunctionNode(
                name=name,
                path=path.relative_to(base_path),
                lineno=lineno,
                end_lineno=end_lineno,
                kind=kind
            )
            for _, name, lineno, end_lineno, kind in defs
        ]
        return cls(path, base_path, functions)

class TreeBuilder:
    """Builds a hierarchical tree of Python files and their functions."""
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir.resolve()

    def collect_files(self) -> Iterator[FileNode]:
        """Collect and process all Python files in the directory."""
        for root, _, files in os.walk(self.base_dir):
            for file in files:
                if file.endswith('.py'):
                    path = Path(root) / file
                    yield FileNode.from_path(path, self.base_dir)

    def build_file_tree(self, files: Iterator[FileNode]) -> Dict:
        """Build hierarchical tree structure from files."""
        tree = {}
        for file in files:
            current = tree
            for part in file.rel_path.parts[:-1]:
                current = current.setdefault(part, {})
            
            file_node = current.setdefault(file.rel_path.parts[-1], {})
            if file.error:
                file_node["__error__"] = file.error
            else:
                file_node["__functions__"] = [
                    f.to_tree_item() for f in file.functions
                ]
        return tree

    def create_ui_nodes(self, name: str, subtree: Dict, parent_path: Path) -> List[Dict]:
        """Create UI tree nodes from the file tree."""
        if name == "__functions__":
            return subtree
        if name == "__error__":
            return [{
                "label": subtree,
                "value": str(parent_path / "__error__"),
                "disabled": True
            }]
        
        return [
            {
                "label": k,
                "value": str(parent_path / k),
                "children": self.create_ui_nodes(k, v, parent_path / k)
            }
            for k, v in subtree.items()
        ]

    def build_tree(self) -> TreeDict:
        """Build the complete tree structure."""
        files = self.collect_files()
        tree = self.build_file_tree(files)
        
        return [{
            "label": self.base_dir.name,
            "value": str(self.base_dir),
            "children": self.create_ui_nodes(
                self.base_dir.name,
                tree,
                self.base_dir
            )
        }]
