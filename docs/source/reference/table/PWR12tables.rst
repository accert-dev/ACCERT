PWR12-BE Tables
===================================
The PWR12-BE model is a cost model that estimates the cost of PWR12-BE from EEDB. The model contains three main tables: `account`, `cost element`, and `variable`. The account table contains the main cost estimation for PWR12-BE model. Each account is divided into three main cost categories: Factory Equipment Costs, Labor Costs, and Material Costs. The cost element table contains the cost element information for the PWR12-BE model. Some cost element are calculated using algorithms, that need variables to calculate the cost. The variable table contains the variable information for the PWR12-BE model.
Each table is associated with a unique identifier, which is used to track and categorize costs. The tables are connected to each other through the different columns.



PWR12-BE Account Table
-----------------------------
This table contains the account information for the PWR12-BE model.
PWR12-BE account table can also ordered by GNCOA. Each entity in the account table is associated with a unique identifier, which is used to track and categorize costs. The table is organized into multiple levels, with each level representing a different component or subtask.

The table includes the following columns:

   - **ind**: unique identifier for each account
   - **code_of_account**: code of account 
   - **account_description**: description of the account
   - **total_cost**: total cost of the account unit in dollars
   - **level**: level of the account
   - **supaccount**: superior account
   - **review_status**: review status of the account, note that the default value should always be `Unchanged`
   - **prn**: percentage of the account cost in the total direct cost
   - **gncoa**: generalized nuclear code of account
   - **gn_level**: generalized nuclear code of account level
   - **gn_supaccount**: generalized nuclear code of account superior account
   - **gn_ind**: generalized nuclear code of account unique identifier

.. csv-table:: [PWR12-BE Account Table]
   :header-rows: 1
   :file: ../../../../tutorial/ref_tables/PWR12-BE_accounts.csv
   :widths: auto
   :class: normal-table

PWR12-BE Cost Element Table
----------------------------
This table contains the cost element information for the PWR12-BE model. Each entitiy in the account
table is divided into 3 main cost categories: Factory Equipment Costs, Labor Costs, and Material Costs.
The cost element table is associated with a unique identifier, which is used to track and categorize costs. The table is connected to the account table through the `account` column, which links each cost element to a specific account. It is also connected to the variable table through the `variables` column, and the algorithm table through the `alg_name` column.

The table includes the following columns:

   - **ind**: unique identifier for each cost element
   - **cost_element**: cost element name
   - **cost_2017**: cost of the element in 2017 dollars
   - **sup_cost_ele**: superior cost element
   - **alg_name**: algorithm name
   - **fun_unit**: algorithm function output unit
   - **variables**: variables used in the algorithm
   - **account**: account associated with the cost element
   - **algno**: algorithm number in the algorithm table
   - **updated**: updated status of the cost element, 0 for unchanged and 1 for updated, note that the default value should always be 0

.. csv-table:: [PWR12-BE Cost Element Table]
   :header-rows: 1
   :file: ../../../../tutorial/ref_tables/PWR12-BE_cost_element.csv
   :widths: auto
   :class: wide-table

PWR12-BE Variable Table
--------------------------
This table contains the variable information for the PWR12-BE model. Each variable. All variables are needed to calculate the cost of the PWR12-BE model, either directly or indirectly. Some variables are connected to the algorithm table through the `var_alg` column, which links each variable to a specific algorithm. The table is also connected to itself through the `v_linked` and `var_needed` column, which links each variable to a superior variable and the variables needed to calculate it.

The table includes the following columns:

   - **ind**: unique identifier for each variable
   - **var_name**: variable name
   - **var_description**: description of the variable
   - **var_value**: value of the variable
   - **var_unit**: unit of the variable
   - **var_alg**: algorithm associated with the variable if any
   - **var_need**: variables needed to calculate the variable if any
   - **v_linked**: superior variable if any
   - **user_input**: user input status of the variable, 0 for not user input and 1 for user input, note that the default value should always be 0

.. csv-table:: [PWR12-BE Variable Table]
   :header-rows: 1
   :file: ../../../../tutorial/ref_tables/PWR12-BE_variable.csv
   :widths: auto
   :class: wide-table
