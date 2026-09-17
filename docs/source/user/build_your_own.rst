Build Your Own Reference Model
==============================

ACCERT accepts user-defined models with a custom code-of-account structure.

Build your own account table
-----------------------------

Create a ``raw_account.csv`` file with the following columns: ``ind``,
``code_of_account``, ``account_description``, ``total_cost``, ``level``,
``supaccount``, ``alg_name``, ``fun_unit``, and ``variables``.

- **ind**: [REQUIRED] Unique identifier for each account
- **code_of_account**: [REQUIRED] Code of account 
- **account_description**: [Optional] Description of the account
- **total_cost**: [REQUIRED] Total cost of the account unit in dollars
- **level**: [REQUIRED] Level of the account
- **supaccount**: [REQUIRED] Superior account
- **alg_name**: [Optional] Algorithm name to calculate the cost of the account
- **fun_unit**: [Optional] Algorithm function output unit
- **variables**:[Optional] Variables used in the algorithm


.. csv-table:: [Example account Table]
   :header-rows: 1
   :file: ../../../tutorial/accert/user_defined/raw_account_example.csv
   :widths: auto
   :class: normal-table

Make sure every account is connected from the top level to the bottom level.
For each account, ``supaccount`` should be the ``code_of_account`` of its parent
account. If an algorithm is applied to the account, specify ``alg_name``.
``fun_unit`` is the output unit of the algorithm function, and ``variables``
lists the variables used by the algorithm. ``total_cost`` is in dollars.

Run the following commands from the repository root to generate the
user-defined account table.

.. code-block:: bash

    cd tutorial/accert/user_defined
    python ../../../src/scripts/gen_user_defined.py

The script generates ``user_defined_account.csv`` and
``raw_variable_automated_generated.csv`` in the same directory.
``user_defined_account.csv`` is used in the next step to generate the
user-defined algorithm table. Fill in ``raw_variable_automated_generated.csv``
with the values of the variables used in the algorithm.

.. csv-table:: [Generated account Table with added review_status and prn columns]
   :header-rows: 1
   :file: ../../../tutorial/accert/user_defined/user_defined_account.csv
   :widths: auto
   :class: normal-table

The following columns are required in the filled variable file:

   - **var_value**: value of the variable
   - **var_unit**: unit of the variable
   

.. csv-table:: [Generated variable Table]
   :header-rows: 1
   :file: ../../../tutorial/accert/user_defined/raw_variable_automated_generated.csv
   :widths: auto
   :class: normal-table

If some variables are calculated from other variables, the user can fill in the algorithm name in the `var_alg` column, and the variables in the `var_need` column:

   - **var_alg**: algorithm associated with the variable if any
   - **var_need**: variables needed to calculate the variable if any
   - **v_linked**: superior variable if any

.. csv-table:: [Example filled in variable Table]
   :header-rows: 1
   :file: ../../../tutorial/accert/user_defined/raw_variable_example.csv
   :widths: auto
   :class: normal-table

Fill in your own algorithm
---------------------------

Save the filled variable file as ``raw_variable.csv``, then run the command
again from ``tutorial/accert/user_defined`` to generate the algorithm table,
SQLite load script, and algorithm Python file.

.. code-block:: bash

    python ../../../src/scripts/gen_user_defined.py

The script generates three files:

- ``user_defined_algorithm.csv`` is the algorithm reference table.
- ``user_defined.sql`` creates and loads the user-defined SQLite tables.
- ``user_defined_func.py`` calculates the total cost of each account or variable.

.. csv-table:: [Generated algorithm Table]
   :header-rows: 1
   :file: ../../../tutorial/accert/user_defined/user_defined_algorithm.csv
   :widths: auto
   :class: normal-table

This table is used to create the database table. The ``alg_for`` column
identifies whether the algorithm is applied to an account or a variable:
``c`` means account, and ``v`` means variable. ``alg_name`` is the name of the
algorithm. ``alg_unit`` is the output unit of the algorithm function.

The ``user_defined_func.py`` file calculates the total cost of each account.
Modify ``user_defined_func.py`` to implement the algorithms. Each generated
algorithm function includes notes explaining the variables it needs.

.. include:: ../../../tutorial/accert/user_defined/user_defined_func_generated.py
   :literal:


After filling in the algorithm functions, save them as ``user_defined_func.py``
in the same directory. Here is an example of a filled algorithm function.

.. include:: ../../../tutorial/accert/user_defined/user_defined_func.py
   :literal:


Create the database table
-------------------------

In the same folder, ``user_defined.sql`` is generated. Run the following command
to create and load the user-defined tables in the SQLite database.

.. code-block:: bash

    python ../../../src/scripts/run_sql.py

The script creates the database tables and inserts the data from
``user_defined_account.csv``, ``user_defined_variable.csv``, and
``user_defined_algorithm.csv``.

To apply the SQL to a different SQLite database file, pass ``--db``:

.. code-block:: bash

    python ../../../src/scripts/run_sql.py user_defined.sql --db /path/to/accertdb.sqlite


Prepare the input file
----------------------

After the database table is created, you can start preparing the input file for your user-defined reference model. The input file should be in the son format.  Run the following command to make changes to ACCERT schema to accept the user-defined reference model.

.. code-block:: bash

    python ../../../src/scripts/prepared_input.py

The script will generate a list of accepted values for the user-defined reference model. The user can fill in the input file with the accepted values. The input file should be in the son format. Here is an example of the input file.

.. include:: ../../../tutorial/accert/user_defined/user_defined_input.son
   :literal:

Run your own reference model
----------------------------

After the input file is prepared, you can run the reference model with the following command.

.. code-block:: bash

    python ../../../src/Main.py -i user_defined_input.son

The script will generate the output file in the same directory. The output file will be in the son format. Here is an example of the output file, that just created.

.. include:: ../../../tutorial/accert/user_defined/output.out
   :literal:


    
