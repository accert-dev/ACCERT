import ast
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
toc_file_path = os.path.join(current_dir, 'reference', 'main.rst')


def class_methods(file_path, class_name):
    with open(file_path, 'r', encoding='utf-8') as source_file:
        tree = ast.parse(source_file.read())
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return [item.name for item in node.body if isinstance(item, ast.FunctionDef)]
    return []


main_methods = class_methods(os.path.join(current_dir, '../..', 'src', 'Main.py'), 'Accert')
utility_methods = class_methods(os.path.join(current_dir, '../..', 'src', 'utility_accert.py'), 'Utility_methods')

if os.path.exists(toc_file_path):
    os.remove(toc_file_path)

with open(toc_file_path, 'w', encoding='utf-8') as toctree_file:
    toctree_file.write(
        """
Accert Code Reference
=====================

This section lists the main ACCERT classes and methods. It is generated from
the source tree so the documentation does not need copied Python files.

Accert Class
------------

The ``Accert`` class is defined in ``src/Main.py``. It includes these methods:

"""
    )
    for method_name in main_methods:
        toctree_file.write(f"- ``{method_name}``\n")

    toctree_file.write(
        """

Accert Utility Functions
------------------------

The ``Utility_methods`` class is defined in ``src/utility_accert.py``. It
includes these methods:

"""
    )
    for method_name in utility_methods:
        toctree_file.write(f"- ``{method_name}``\n")

print(f"Generated {toc_file_path}")
