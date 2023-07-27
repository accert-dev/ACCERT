.. toctree::
    :maxdepth: 2
     
Variable Inputs and Explanations
================================

.. sqltable:: PWR12-BE Variables
    :connection_string: sqltable_connection_string

    select ind as 'Index', var_name as 'Name', var_description as 'Description', var_unit as 'Unit' from accert_db
    order by Index asc

