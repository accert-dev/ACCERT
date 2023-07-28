.. toctree::
    :maxdepth: 2
     
Variable Inputs and Explanations
================================


.. sqltable
    :connection_string: mysql+pymysql://root:{encoded_password}@localhost:3306/variables

    select ind as "Index", var_name as "Name", var_description as "Description", var_unit as "Unit" from variables
    order by Index asc