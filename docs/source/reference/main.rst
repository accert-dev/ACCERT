

Accert Code Reference
==========================
This section provides detailed information on the Accert codebase. The Accert codebase is divided into two main sections: the main Accert class and utility functions. The main Accert class contains the main functions and methods for the Accert model, while the utility functions contain helper functions for the Accert model.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

Accert Class 
--------------------

.. autosummary::
   :toctree: main/
   :template: function.rst
                         
                             
   Main.Accert.__init__
   Main.Accert.setup_table_names
   Main.Accert.load_obj
   Main.Accert.get_current_COAs
   Main.Accert.update_account_before_insert
   Main.Accert.insert_new_COA
   Main.Accert.insert_COA
   Main.Accert.extract_variable_info_on_name
   Main.Accert.extract_super_val
   Main.Accert.update_input_variable
   Main.Accert.update_variable_info_on_name
   Main.Accert.update_super_variable
   Main.Accert.extract_total_cost_on_name
   Main.Accert.check_unit_conversion
   Main.Accert.convert_unit
   Main.Accert.convert_unit_scale
   Main.Accert.update_total_cost
   Main.Accert.update_total_cost_on_name
   Main.Accert.get_var_value_by_name
   Main.Accert.run_pre_alg
   Main.Accert.update_account_value
   Main.Accert.update_cost_element_on_name
   Main.Accert.update_new_cost_elements
   Main.Accert.update_new_accounts
   Main.Accert.update_account_table_by_cost_elements
   Main.Accert.roll_up_cost_elements
   Main.Accert.roll_up_cost_elements_by_level
   Main.Accert.roll_up_account_table
   Main.Accert.roll_up_account_table_by_level
   Main.Accert.roll_up_account_table_GNCOA
   Main.Accert.sum_cost_elements_2C
   Main.Accert.fetch_sum_and_update
   Main.Accert.roll_up_lmt_account_2C
   Main.Accert.roll_up_lmt_direct_cost
   Main.Accert.cal_direct_cost_elements
   Main.Accert.roll_up_lmt_account_table
   Main.Accert.print_logo
   Main.Accert.execute_accert
   Main.Accert.process_reference_model
   Main.Accert.process_power_inputs
   Main.Accert.process_variables
   Main.Accert.process_super_values
   Main.Accert.process_COA
   Main.Accert.process_level_accounts
   Main.Accert.process_ce
   Main.Accert.process_var
   Main.Accert.process_alg
   Main.Accert.check_and_process_total_cost
   Main.Accert.check_total_cost_changed
   Main.Accert.check_total_cost_accounts
   Main.Accert.process_total_cost
   Main.Accert.process_total_cost_accounts
   Main.Accert.exit_with_error
   Main.Accert.finalize_process
   Main.Accert.generate_results
   Main.Accert._generate_common_results
   Main.Accert._common_cost_processing
   Main.Accert._print_results
   Main.Accert._pwr12be_processing
   Main.Accert._no_cost_element_processing
   Main.Accert.generate_results_table_with_cost_elements
   Main.Accert._generate_excel
   Main.Accert.generate_results_table

                           
Accert Utility Functions
--------------------------
.. autosummary::
   :toctree: utility/
   :template: function.rst
                                
   utility_accert.Utility_methods.__init__
   utility_accert.Utility_methods.setup_table_names
   utility_accert.Utility_methods.print_table
   utility_accert.Utility_methods.print_account
   utility_accert.Utility_methods.print_leveled_accounts
   utility_accert.Utility_methods.print_leveled_accounts_gncoa
   utility_accert.Utility_methods.print_algorithm
   utility_accert.Utility_methods.print_cost_element
   utility_accert.Utility_methods.print_facility
   utility_accert.Utility_methods.print_escalation
   utility_accert.Utility_methods.print_variable
   utility_accert.Utility_methods.print_user_request_parameter
   utility_accert.Utility_methods.print_updated_cost_elements
   utility_accert.Utility_methods.extract_affected_cost_elements
   utility_accert.Utility_methods.extract_affected_accounts
   utility_accert.Utility_methods.extract_user_changed_variables
   utility_accert.Utility_methods.extract_changed_cost_elements
