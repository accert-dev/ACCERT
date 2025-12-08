Getting Started
===============

This user guide will assist you in:

- **Running ACCERT via Python**: Executing ACCERT from the command line using a Python script.
- **Running ACCERT via NEAMS Workbench**: Utilizing ACCERT within the NEAMS Workbench environment.
- **Running Your First Estimation**: Instructions on inputting parameters, executing calculations, and interpreting results.
- **Exploring Advanced Features**: Insights into advanced functionalities, such as customizing algorithms and integrating new data sets.


Setting Up ACCERT
-----------------

Prior to running ACCERT, please ensure that you have completed the installation steps as outlined in the :doc:`Installation Guide <install>`.

Using ACCERT via Python
-----------------------

1. **Prepare Your Input File**

   - ACCERT requires an input file in SON format (`.son`), which specifies the parameters and variables for your reactor model.
   - You may utilize one of the provided reference models or create a custom input file.
   - Example reference models include:

     - `PWR12-BE.son`
     - `ABR1000.son`
     - `heatpipe.son`
     - `Fusion.son`

   -  Open a terminal and navigate to the directory containing your input file (e.g., `tutorial`):

   .. code-block:: shell

      $ cd ACCERT/tutorial

2. **Modify Reactor Parameters**

   -  For this guide, we will use the `PWR12-BE.son` reference model, feel free to replace it with your preferred model. Open the `.son` file using a text editor or an Integrated Development Environment (IDE) such as Visual Studio Code.
   - Specify the required parameters for your reactor model:

     - **Thermal Power (`mwth`)**: The reactor's thermal power output in megawatts (MW).
     - **Electric Power (`mwe`)**: The reactor's electric power output in megawatts (MW).

   - Optionally, adjust additional variables to align with your reactor design.

     **Example Variable Modification:**

     .. code-block:: text

         var(Cont_rad_out_m) { value = 30 unit = m }

     This modification sets the containment radius to 30 meters.

3. **Run ACCERT**

   - Execute ACCERT using the `Main.py` script and specify your input file:

     .. code-block:: shell

         $ python ../src/Main.py -i myinput.son

     Replace `myinput.son` with the path to your specific input file. ACCERT will process the input parameters and generate cost estimates based on the provided data.

4. **View the Output**

   - ACCERT generates an output file named `output.out`.
   - Open `output.out` in your text editor to review the results.
   - The output includes:

     - **User Input Summary**: Details the reference model and parameters utilized.
     - **Extracted Variables**: Lists the variables that have been modified and their corresponding values.
     - **Affected Cost Elements**: Identifies which cost elements are influenced by the modified variables.
     - **Updated Cost Elements**: Provides details on how each cost element was recalculated based on the applied algorithms.
     - **Roll-up of Cost Elements**: Aggregates cost elements from lower levels to higher levels within the COA hierarchy.
     - **Results Table**: Presents a summary table of COAs, descriptions, costs, and review statuses.
     - **GNCOA or EEDB COA Ordering**: Results are ordered according to the selected COA framework.

     **Example Output Snippet:**

     .. code-block:: text

         ======================================== Reading user input ========================================

         [USER_INPUT] Reference model is "PWR12-BE"

         Parameter "mwe" is required for cost elements:
         241_fac, 242_fac, 245_fac, 246_fac, 241_lab, ...

         [USER_INPUT] Thermal power is 3000 MW

         [USER_INPUT] Electric power is 1000 MW

     *Note*: The complete output is extensive; please refer to `output.out` for full details.

5. **Review Results**

   - Analyze the `output.out` file to understand the impact of your input parameters on the cost estimates.
   - Consult the **Results Table** to assess costs and review statuses of various components.

6. **Output Files**

   - ACCERT may generate additional output files in Excel format for in-depth analysis:

     - `pwr12-be_variable_affected_cost_elements.xlsx`
     - `pwr12-be_updated_cost_element.xlsx`
     - `pwr12-be_updated_account.xlsx`

     These files contain comprehensive data on the cost elements and accounts affected by your inputs.

Using ACCERT via NEAMS Workbench
--------------------------------

1. **Open NEAMS Workbench**

   - Launch the NEAMS Workbench application on your system.

2. **Add ACCERT Configuration**

   - Navigate to `Workbench` > `Configurations`.
   - Click `Add` and select `ACCERT` from the list of available configurations.
   - Set the **Executable** path to `Main.py` located in the `ACCERT/src/` directory.
   - Load the grammar by clicking `Load Grammar`.

   .. admonition:: Windows Users!

    To begin using ACCERT, please change the `Main.py` file with executable permissions. You can do this by right-clicking the file, selecting `Properties`, and enabling the `Execute` permission under the `Permissions` tab.

3. **Run ACCERT**

   - Open your input file within the Workbench environment.
   - Click the `Run` button to execute ACCERT.
   - Review the results in `output.out` directly within Workbench.

4. **Analyze Output**
   
   - Examine the output file to understand the cost estimates and review statuses of various components.

   
   - Utilize the Excel files generated by ACCERT for detailed analysis of cost elements and accounts.



Example Output
--------------

Below is an example of ACCERT's output for a Lead-cooled Fast Reactor (LFR) model:

.. code-block:: text

   ======================================== Reading user input ========================================

   [USER_INPUT] Reference model is "PWR12-BE"

   Parameter "mwth" is required for cost elements:
   213_fac, 222.11_fac, 222.12_fac, 222.14_fac, 222_fac, 226.4_fac, 226.7_fac, 233_fac, 234_fac,
   262_fac, 213_lab, 222.11_lab, 222.12_lab, 222.14_lab, 222_lab, 226.4_lab, 226.7_lab, 233_lab,
   234_lab, 237_lab, 262_lab, 213_mat, 222.11_mat, 222.12_mat, 222.14_mat, 222_mat, 226.4_mat,
   226.7_mat, 233_mat, 234_mat, 237_mat, 262_mat

   Parameter "mwe" is required for cost elements:
   241_fac, 242_fac, 246_fac, 241_lab, 242_lab, 245_lab, 246_lab, 241_mat, 242_mat, 245_mat, 246_mat

   [USER_INPUT] Thermal power is 3000 MW 

   [USER_INPUT] Electric power is 1000 MW 

   [Updating] Variable ref_211_fac
   [Updated]  Changed from 0.284275 million to 0.27 million

   ..... (additional output details) .....

   =================================Extracting user changed variables==================================


   +---------------------+------------------------------------------------------+-----------+----------+
   |       var_name      |                   var_description                    | var_value | var_unit |
   +---------------------+------------------------------------------------------+-----------+----------+
   |      c_213_fac      |       Turbine building structure factory cost        |    1.79   | million  |
   |  c_221.12_cs_weight |    weight of the carbon steel parts of the vessel    |   538.00  |   ton    |
   |  c_221.12_ss_weight | weight of the stainless steel cladding of the vessel |   18.30   |   ton    |
   | c_221.12_tol_weight |         weight of the reactor primary vessel         |   556.30  |   ton    |
   |         mwe         |                    user_input MWE                    |  1,000.00 |    MW    |
   |         mwth        |                   user_input mwth                    |  3,000.00 |    MW    |
   |        n_231        |                 Scaling exponent law                 |    1.03   |    1     |
   |         p_in        |                Inlet turbine pressure                |   68.00   |   bar    |
   |     ref_211_fac     |                yardwork factory cost                 |    0.27   | million  |
   |     ref_211_mat     |                yardwork material cost                |   10.30   | million  |
   +---------------------+------------------------------------------------------+-----------+----------+

   ================================ Extracting affected cost elements =================================

   variable "n_231" affects cost element(s):
   231_fac

   variable "mwth" affects cost element(s):
   213_fac, 222.11_fac, 222.12_fac, 222.14_fac, 222_fac, 226.4_fac, 226.7_fac, 233_fac, 234_fac,
   262_fac, 213_lab, 222.11_lab, 222.12_lab, 222.14_lab, 222_lab, 226.4_lab, 226.7_lab, 233_lab,
   234_lab, 237_lab, 262_lab, 213_mat, 222.11_mat, 222.12_mat, 222.14_mat, 222_mat, 226.4_mat,
   226.7_mat, 233_mat, 234_mat, 237_mat, 262_mat

   variable "c_221.12_cs_weight" affects cost element(s):
   220A.211_fac

   ... (additional affected cost elements)
   ====================================== Updating cost elements ======================================

   [Updating] Cost element [222_mat], running algorithm: [MWth_scale],
   [Updating] with formulation: cost_of_ref * (thermal_power / thermal_power_of_ref) ^ thermal_power_scale
   [Updated]  Reference value: $523,270    , Calculated value: $523,270

   ... (additional cost elements updated)

   +-----+--------------+-----------------+--------------+----------+---------+
   | ind | cost_element |    cost_2017    | sup_cost_ele | account  | updated |
   +-----+--------------+-----------------+--------------+----------+---------+
   |  1  |   211_fac    |    769339.89    |    21_fac    |   211    |    1    |
   |  3  |   213_fac    |   1607731.2757  |    21_fac    |   213    |    1    |
   |  24 | 220A.211_fac |    80992349.0   |   220A_fac   | 220A.211 |    1    |
   |  56 |  222.11_fac  |  3305891.38618  |   222_fac    |  222.11  |    1    |
   |  57 |  222.12_fac  |  3842334.19324  |   222_fac    |  222.12  |    1    |
   |  59 |  222.14_fac  |   13140.40834   |   222_fac    |  222.14  |    1    |

   ... (additional cost elements table entries)
   ====================================== Roll up cost elements =======================================


   [Updating] Roll up cost elements from level 3 to level 2
   [Updating] Roll up cost elements from level 2 to level 1
   [Updating] Roll up cost elements from level 1 to level 0
   [Updated] Cost elements rolled up

   ====================================== Updating account table ======================================


   [Updating] Updating account table by cost elements
   [Updated]  Account table updated from cost elements

   ========================================== IMPORTANT NOTE ==========================================
   Some cost have changed by user inputs and may not be reflected correctly in the cost elements table.

   [Updating] Total cost of account 217
   [Updated]  Changed from 28,149,600.00 dollar to 28,149,700.00 dollar

   [Updating] Total cost of account useraddcoa
   [Updated]  Changed from 9,000,000.00 dollar to 9,000,000.00 dollar

   ===================================== Rolling up account table =====================================


   [Updating] Rolling up account table from level 3 to level 2 
   [Updating] Rolling up account table from level 2 to level 1 
   [Updating] Rolling up account table from level 1 to level 0 
   [Updated]  Account table rolled up

   =============================== Generating results table for review ================================


   +-------+-----------------+-------------------------------------------------+----------+----------+----------+------------+------------------+
   | level | code_of_account |               account_description               | fac_cost | lab_cost | mat_cost | total_cost |  review_status   |
   +-------+-----------------+-------------------------------------------------+----------+----------+----------+------------+------------------+
   |   0   | 2               | TOTAL DIRECT COST                               | 1,419.43 |   767.38 |   341.93 |   2,537.74 |     Updated      |
   |   1   |  21             | Structures and improvements subtotal            |    23.33 |   320.64 |   219.52 |     572.49 |     Updated      |
   |   2   |   useraddcoa    | 'a user added coa'                              |        0 |        0 |        0 |       9.00 |    User Input    |
   |   2   |   211           | Yardwork                                        |     0.77 |    41.33 |    29.35 |      71.45 | Ready for Review |
   |   2   |   212           | Reactor containment building                    |        0 |   101.95 |    80.75 |     182.70 |    Unchanged     |
   |   2   |   213           | Turbine room and heater bay                     |     1.61 |    28.59 |    29.07 |      59.27 | Ready for Review |

For the complete output, please refer to the `output.out` file generated by ACCERT.

Next Steps
----------

- **Experiment with Variables**: Adjust different input parameters to observe their impact on cost estimates.
- **Understand Algorithms**: Familiarize yourself with the cost scaling algorithms employed by ACCERT.
- **Consult Documentation**: Refer to the User's Guide for comprehensive explanations of ACCERT's features and functionalities.
