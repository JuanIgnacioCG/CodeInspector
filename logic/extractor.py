import ast
from typing import List
from pathlib import Path
from model.types import Definition

def extract_source(file_path: str, lineno: int, end_lineno: int) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return ''.join(f.readlines()[lineno-1:end_lineno])

def extract_definitions(file_path: Path) -> List[Definition]:
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