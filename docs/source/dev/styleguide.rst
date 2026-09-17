.. _style_guide:

Style Guide
-----------

ACCERT is written in **Python 3** and uses **SQLite** for the bundled database.

Style for Python code should follow `PEP 8`_.

Python code should be annotated with type hints according to `PEP 484`_.
Docstrings for functions and methods should follow numpydoc_ style.

Python code should work with all currently `supported versions`_ of Python.

.. _PEP 8: https://www.python.org/dev/peps/pep-0008/
.. _PEP 484: https://www.python.org/dev/peps/pep-0484/
.. _numpydoc: https://numpydoc.readthedocs.io/en/latest/format.html
.. _supported versions: https://devguide.python.org/#status-of-python-branches
.. _os: https://docs.python.org/3/library/os.html
.. _Path: https://docs.python.org/3/library/pathlib.html#pathlib.Path

SQLite procedure logic lives in ``src/accert_sqlite_procedures.py``. New
database code should use parameterized queries for values and validate table or
column identifiers before interpolation.

Consistent style is important for us, because everyone must know what to expect. Knowing our rules, you'll find it easier to read our code, and when you decide to contribute (which we hope you'll consider!) we'll find it easier to read and review your code.
