"""Generate reference pages for SQLite procedure replacements."""

from __future__ import annotations

import ast
import os
from pathlib import Path


current_dir = Path(__file__).resolve().parent
procedure_file_path = (current_dir / "../.." / "src" / "accert_sqlite_procedures.py").resolve()
output_dir = current_dir / "reference" / "database"
toctree_file_path = current_dir / "reference" / "database.rst"


def _procedure_names(tree: ast.Module) -> list[str]:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "PROCEDURES":
                    if isinstance(node.value, ast.Dict):
                        return sorted(
                            key.value
                            for key in node.value.keys
                            if isinstance(key, ast.Constant) and isinstance(key.value, str)
                        )
    return []


def clean_output_directory(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for filename in directory.iterdir():
        if filename.suffix == ".md":
            filename.unlink()
            print(f"Removed old Markdown file: {filename}")


def append_to_toctree(sp_name: str) -> None:
    with toctree_file_path.open("a", encoding="utf-8") as toctree_file:
        toctree_file.write(f"   database/{sp_name}\n")


def main() -> None:
    print(f"Reading SQLite procedure replacements from: {procedure_file_path}")
    clean_output_directory(output_dir)

    if toctree_file_path.exists():
        toctree_file_path.unlink()
    with toctree_file_path.open("w", encoding="utf-8") as toctree_file:
        toctree_file.write(
            """
Database Procedure Replacements
===============================

.. toctree::
   :maxdepth: 1
   :caption: Contents:

"""
        )

    tree = ast.parse(procedure_file_path.read_text(encoding="utf-8"))
    function_nodes = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    for sp_name in _procedure_names(tree):
        function_node = function_nodes.get(sp_name)
        if function_node is None:
            continue
        params = [arg.arg for arg in function_node.args.args if arg.arg != "conn"]
        params_table = "\n".join(f"| {param} |" for param in params) or "| None |"
        content = f"""---
title: {sp_name}
---

# {sp_name}

SQLite/Python replacement for the former ACCERT database stored procedure.

## Parameters

| **Name** |
|----------|
{params_table}

## Implementation

See ``src/accert_sqlite_procedures.py``.
"""
        (output_dir / f"{sp_name}.md").write_text(content, encoding="utf-8")
        append_to_toctree(sp_name)

    print("All SQLite procedure replacement docs have been generated successfully.")


if __name__ == "__main__":
    main()
