Fusion Tables
=============

The Fusion model is a cost model that estimates the cost of TETRA (Tokamak Engineering Test Reactor Analysis), which is a large tokamak fusion reactor based on UKAEA's `PROCESS <https://github.com/ukaea/PROCESS>`_.

The model contains three main tables: `account`, `algorithm`, and `variable`. The account table contains the main cost estimation for the Fusion model. The variable table contains the variable information for the Fusion model, while the algorithm table contains the algorithm information for the Fusion model. Each table is associated with a unique identifier, which is used to track and categorize costs. The tables are connected to each other through different columns.

Fusion Account Table
---------------------

This table contains the account information for the Fusion model. Each entity in the account table is associated with a unique identifier, which is used to track and categorize costs. The table is organized into multiple levels, with each level representing a different component or subtask.

The table includes the following columns:

- **ind**: Unique identifier for each account
- **code_of_account**: Code of account 
- **account_description**: Description of the account
- **total_cost**: Total cost of the account unit in dollars
- **level**: Level of the account
- **supaccount**: Superior account
- **review_status**: Review status of the account; note that the default value should always be `Unchanged`
- **prn**: Percentage of the account cost in the total direct cost
- **alg_name**: Algorithm name to calculate the cost of the account
- **fun_unit**: Algorithm function output unit
- **variables**: Variables used in the algorithm

.. csv-table:: Fusion Account Table
   :header-rows: 1
   :file: ../../../../tutorial/ref_tables/fusion_acc.csv
   :widths: auto
   :class: wide-table

Fusion Algorithm Table
----------------------

This table contains the algorithm information for the Fusion model. Each algorithm is associated with a unique identifier, which is used to track and categorize costs. The table is connected to the account table through the `account` column, which links each algorithm to a specific account. It is also connected to the variable table through the `variables` column.

The table includes the following columns:

- **ind**: Unique identifier for each algorithm
- **alg_name**: Algorithm name
- **alg_for**: Algorithm for a cost element or a variable, `c` for cost and `v` for variable
- **alg_description**: Description of the algorithm
- **alg_python**: Python file name in the Algorithm folder
- **alg_formulation**: Formulation of the algorithm
- **alg_units**: Unit of the algorithm output

.. csv-table:: Fusion Algorithm Table
   :header-rows: 1
   :file: ../../../../tutorial/ref_tables/fusion_alg.csv
   :widths: auto
   :class: wide-table

Fusion Variable Table
---------------------

This table contains the variable information for the Fusion model. All variables are needed to calculate the cost in the account table or a super variable. Some variables are connected to the algorithm table through the `var_alg` column, which links each variable to a specific algorithm. The table is also connected to itself through the `v_linked` and `var_needed` columns, which link each variable to a superior variable and the variables needed to calculate it.

The table includes the following columns:

- **ind**: Unique identifier for each variable
- **var_name**: Variable name
- **var_description**: Description of the variable
- **var_value**: Value of the variable
- **var_unit**: Unit of the variable
- **var_alg**: Algorithm associated with the variable, if any
- **var_need**: Variables needed to calculate the variable, if any
- **v_linked**: Linked variable, if any
- **user_input**: User input variable, if any

.. csv-table:: Fusion Variable Table
   :header-rows: 1
   :file: ../../../../tutorial/ref_tables/fusion_var.csv
   :widths: auto
   :class: wide-table
