.. toctree::
    :maxdepth: 1

Level 2
=======

*   Level 2:

    *   This is a level lower than level 1. Within this level will be different cost elements that make up the total cost of the level  it follows.
    *   The COA for this level will be a three digit number with the first two digits being the same as the number that precedes it followed by the iteration of the cost element.
    *   In certain cost elements, this is the lowest level of breakdown.

        *   For example, if the cost element is the first cost element in level 2, the code would be written as l2COA(211) or l1COA(212) for the second.

**All the cost elements and their descriptions are broken down in the MySQL database.**

.. toctree::
    :maxdepth: 1
    :caption: Code of Accounts

    level2alg.rst
    level2ce.rst
    level2COA.rst