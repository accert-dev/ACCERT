.. toctree::
    :maxdepth: 1

ABR-1000 Output
===============

.. admonition:: NOTICE!

    The output given at the bottom of this page is not the standard output. **It will change based on the user input!**

**Explanation of the Output**

*Reading User input*

This section reads any changed user inputs, with the three required changed parameters (reference reactor, MWth, and MWe) being the first ones presented.

*Extracting User Changed Variables*

This section prints an easy to observe chart of all the user changed variables, their value, and their unit.

*Extracting Affected Cost Elements*

This section takes the user changed variables and prints them into an itemized list of what cost elements were affected by which variables.

*Updating Cost Elements*

This section uses various algorithms to update the cost of the affected cost elements. 

*Roll Up Cost Elements*

This section "rolls up" all the cost elements from the lowest level to the highest level. This allows for the charts generated to make more sense with the levels.

*Updating Account Table*

This section updates the final account table with the newly updated cost elements.

*Rolling Up Account Table*

This section "rolls up" all the code of accounts from the lowest level to the highest level. This allows for the final generate chart to make logical sense by level.

*Generating Results Table for Review*

This section prints out the final result table with all the code of accounts, their costs in millions, and whether or not they have been changed.

.. admonition:: NOTICE!

    At the end, ACCERT also prints off three different excel files for the outputs.
    
.. include:: outputabr.out.txt
    :literal: