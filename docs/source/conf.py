# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
# from urllib.parse import quote

#password = '@Darn12213529L'
#encoded_password = quote(password)
#
#sys.path.insert(0, os.path.abspath('./inputsIndex'))
#
#sqltable_connection_string = 'mysql+pymysql://root:{encoded_password}@localhost:3306/variables'
current_dir = os.getcwd()

relative_path=r'.\inputsIndex'

relative_path_to_main_py = r'.\inputsIndex\Main.py'

absolute_path = os.path.join(current_dir, relative_path)

accert_path = os.path.join(current_dir, relative_path_to_main_py)

sys.path.append(absolute_path)

sys.path.append(accert_path)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ACCERT User Manual'
copyright = '2023, Argonne National Laboratory'
author = 'Argonne National Laboratory'
release = '0.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_rtd_theme',
    'sphinx.ext.autodoc',
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
