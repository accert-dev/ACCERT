Build Your Own Reference Model
=====================

ACCERT now accept user-defined model with user defined code of account structure. 

Build your own account table
-----------------------------

Create a raw_account.csv file, that table should includes with the following columns: ind, code_of_account, account_description, total_cost, level, supaccount, alg_name, fun_unit, variables. 

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
   :file: ../../../tutorial/user_defined/raw_account_example.csv
   :widths: auto
   :class: normal-table

Make sure that all the hierarchy accounts can be connected from the top level to the bottom level. And for each account, the supaccount should be the code_of_account of its parent account. If any algorithm is applied to the account, the alg_name should be specified. The fun_unit is the unit of the algorithm function. The variables are the variables that are used in the algorithm. Total cost is the in the unit of dollar.

Run the following command to generate the user-defined account table.

.. code-block:: bash

    python ACCERT/src/scripts/gen_user_defined.py

The script will generate a `user_defined_account.csv` file in the same directory, and also generate a `raw_variable_automated_generated.csv` file. The `user_defined_account.csv` file will be used in the next step to generate the user-defined algorithm table. The `raw_variable_automated_generated.csv` file will be filled in by the user to provide the values of the variables used in the algorithm.

.. csv-table:: [Generated account Table with added review_status and prn columns]
   :header-rows: 1
   :file: ../../../tutorial/user_defined/user_defined_account.csv
   :widths: auto
   :class: normal-table

The `raw_variable_automated_generated.csv` file will be filled in by the user to provide the values of the variables used in the algorithm, the following columns are required:

   - **var_value**: value of the variable
   - **var_unit**: unit of the variable
   

.. csv-table:: [Generated variable Table]
   :header-rows: 1
   :file: ../../../tutorial/user_defined/raw_variable_automated_generated.csv
   :widths: auto
   :class: normal-table

If some variables are calculated from other variables, the user can fill in the algorithm name in the `var_alg` column, and the variables in the `var_need` column:

   - **var_alg**: algorithm associated with the variable if any
   - **var_need**: variables needed to calculate the variable if any
   - **v_linked**: superior variable if any

.. csv-table:: [Example filled in variable Table]
   :header-rows: 1
   :file: ../../../tutorial/user_defined/raw_variable_example.csv
   :widths: auto
   :class: normal-table

Fill in your own algorithm
---------------------------

Save the filled in variable file as `raw_variable.csv`, run the command again to generate the algorithm table, databse sql file and the algorithm python file.

.. code-block:: bash

    python ACCERT/src/scripts/gen_user_defined.py

The script will generate 3 files:
- `user_defined_algorithm.csv` will a reference table.
- `user_defined_algorithm.sql` will be used to create the database table.
- `user_defined_func.py` will be used to calculate the total cost of each account or variable.

.. csv-table:: [Generated algorithm Table]
   :header-rows: 1
   :file: ../../../tutorial/user_defined/user_defined_algorithm.csv
   :widths: auto
   :class: normal-table

This table will be used to create the database table. the column `alg_for` is the account or variable that the algorithm is applied to, `c` means the algorithm is applied to the account, `v` means the algorithm is applied to the variable. The `alg_name` is the name of the algorithm. The `alg_unit` is the unit of the algorithm function output. 

And the `user_defined_func.py` file will be used to calculate the total cost of each account. User can modify the `user_defined_func.py` file to implement the algorithm. Each algorithm function will have the notes to explain the algorithm with the needed variables.

.. include:: ../../../tutorial/user_defined/user_defined_func_generated.py
   :literal:


After filled in the algorithm function, it should be saved as `user_defined_func.py` in the same directory. Here is an example of the filled in algorithm function.

.. include:: ../../../tutorial/user_defined/user_defined_func.py
   :literal:


Create the database table
-------------------------

In the same folder a `user_defined_algorithm.sql` file will be generated. Run the following command to implement all the tables in the database.

.. code-block:: bash

    python ACCERT/src/scripts/run_sql.py 

The script will create the database table and insert the data from the `user_defined_account.csv`, `user_defined_variable.csv` and `user_defined_algorithm.csv` files into the database.

You can also run mysql command and source the `user_defined_algorithm.sql` file to create the database table.

.. code-block:: bash

    $ mysql -h localhost -u root -p
    Enter password:
    Welcome to the MySQL monitor.  Commands end with ; or \g.
    Your MySQL connection id is 2475
    Server version: 8.0.27 MySQL Community Server - GPL

    Copyright (c) 2000, 2018, Oracle and/or its affiliates. All rights reserved.

    Oracle is a registered trademark of Oracle Corporation and/or its
    affiliates. Other names may be trademarks of their respective
    owners.

    Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

    mysql>source user_defined_algorithm.sql


Prepare the input file
----------------------

After the database table is created, you can start preparing the input file for your user-defined reference model. The input file should be in the son format.  Run the following command to make changes to ACCERT schema to accept the user-defined reference model.

.. code-block:: bash

    python ACCERT/src/scripts/prepared_input.py

The script will generate a list of accepted values for the user-defined reference model. The user can fill in the input file with the accepted values. The input file should be in the son format. Here is an example of the input file.

.. include:: ../../../tutorial/user_defined/user_defined_input.son
   :literal:

Run your own reference model
---------------------------

After the input file is prepared, you can run the reference model with the following command.

.. code-block:: bash

    python ACCERT/src/Main.py -i user_defined_input.son

The script will generate the output file in the same directory. The output file will be in the son format. Here is an example of the output file, that just created.

.. include:: ../../../tutorial/user_defined/output.out
   :literal:


    

