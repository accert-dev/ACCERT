.. _style_guide:

Style Guide
-----------

ACCERT is written in **Python 3** and **MySQL 8**. 

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

Style for MySQL code should follow Google coding style

New MySQL code uses the `Google C++ coding style <https://google.github.io/styleguide/cppguide.html>`_, with two exceptions:

Member variable names: Do not use `foo_.` Instead, use `m_foo` (non-static) or `s_foo` (static).
Old projects and modifications to old code use an older MySQL-specific style for the time being. Since 8.0, MySQL style uses the same formatting rules as Google coding style (e.g., brace placement, indentation, line lengths, etc.), but differs in a few important aspects:

Class names: Do not use MyClass. Instead, use My_class.

Function names: Use snake_case().

Comment Style: Use either the // or /* */ syntax. // is much more common but both syntaxes are permitted for the time being.
Doxygen comments: Use /** ... */ syntax and not ///.

Doxygen commands: Use '@' and not '\' for doxygen commands.

You may see structs starting with st_ and being typedef-ed to some UPPERCASE (e.g. typedef struct st_foo { ... } FOO). However, this is legacy from when the codebase contained C. Do not make such new typedefs nor structs with st_ prefixes, and feel free to remove those that already exist, except in public header files that are part of libmysql (which need to be parseable as C99).

Code formatting is enforced by use of clang-format throughout the code base. However, note that formatting is only one part of coding style; you are required to take care of non-formatting issues yourself, such as following naming conventions, having clear ownership of code or minimizing the use of macros. See the Google coding style guide for the entire list.

Consistent style is important for us, because everyone must know what to expect. Knowing our rules, you'll find it easier to read our code, and when you decide to contribute (which we hope you'll consider!) we'll find it easier to read and review your code.
