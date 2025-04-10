from pathlib import Path
from typing import NamedTuple, Dict, Any

class Definition(NamedTuple):
    file_path: Path
    name: str
    lineno: int
    end_lineno: int
    kind: str

TreeDict = Dict[str, Any]