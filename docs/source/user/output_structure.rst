Output Structure
================

The ACCERT output file is designed to provide detailed feedback on how user inputs influence the calculated costs of nuclear reactor components. The file is structured into several key sections, each offering insight into the process and results of the cost estimation. Below is a description of these sections and their typical contents.

Reading User Input
----------------------

This section summarizes the parameters entered by the user. These inputs guide the recalculations of specific cost elements. Key parameters typically include:

- **Reference Model**: The reactor model being analyzed. Current options are "PWR12-BE", "ABR1000", "LFR", "Heatpipe", and "Fusion".
- **Thermal Power (MWth)**: The thermal power input provided by the user.
- **Electric Power (MWe)**: The electric power input provided by the user.
  
ACCERT uses these values to determine which cost elements require updating and recalculation. ACCERT employs sophisticated algorithms to update cost elements based on input variables. Since common algorithms include scales costs according to thermal power or electric power, these inputs are crucial for accurate cost estimation.

Variable Updates
--------------------

In this section, ACCERT displays how key variables, which influence cost calculations, are updated. These variables may include material weights, unit costs, or factory, labor, and material cost adjustments. Each updated variable is listed along with its previous and new values. If necessary, unit conversions (e.g., pounds to tons) are also shown.

Examples of typical variable updates might include:

- Reference costs for specific components.
- Material weights for reactor vessels.
- Scaling factors for certain parameters like power output.

Extracting User-Changed Variables
-------------------------------------

This section provides a consolidated list of all variables that have been modified by user inputs or recalculations. For each variable, the following information is typically provided:

- **Variable Name**: The name of the variable that was updated.
- **Description**: A brief description of what the variable represents.
- **Updated Value**: The new value of the variable after recalculation.
- **Units**: The units of measurement for the variable.

Extracting Affected Cost Elements
-------------------------------------

When a variable is updated, certain cost elements are directly affected. In this section, ACCERT lists all cost elements impacted by the updated variables. This ensures that changes to input parameters are reflected in the appropriate areas of the cost structure. Cost elements may be affected by variables such as power outputs, material weights, or labor costs.

Updating Cost Elements
--------------------------

ACCERT uses a set of predefined or user-specified algorithms to recalculate cost elements. Each cost element is updated based on changes in the relevant variables. For each cost element, the following details are typically included:

- **Cost Element**: The identifier for the cost element being updated.
- **Algorithm**: The formula or algorithm used for recalculating the cost.
- **Formulation**: The detailed calculation process, showing how the variables are applied.
- **Updated Value**: The new cost for that particular element after recalculation.


Roll-Up of Cost Elements
----------------------------

Once all cost elements are updated, ACCERT performs a "roll-up" to aggregate costs from lower levels (e.g., component-level costs) to higher levels (e.g., system-level or total project costs). The roll-up occurs in stages:

- **Level 3**: Represents detailed cost elements (e.g., specific components).
- **Level 2**: Aggregates costs from Level 3 into subsystem-level totals.
- **Level 1**: Aggregates subsystem costs into larger categories.
- **Level 0**: The final total cost for the project.

Updating the Account Table
------------------------------

In this section, the account table is updated based on the recalculated cost elements. Each account represents a specific part of the project, and the table shows updated factory, labor, and material costs for each account. The total costs for each account are also updated accordingly.

Generating the Results Table
--------------------------------

The final section of the output presents a comprehensive summary table. This table displays the rolled-up costs, including:

- **Code of Account**: The identifier for each account.
- **Account Description**: A brief description of the account (e.g., turbine plant equipment).
- **Costs**: The factory, labor, material, and total costs for each account.
- **Review Status**: Whether the costs for each account have been updated, left unchanged, or require review:

  - **Unchanged**: Cost elements not affected by input modifications.
  - **Ready for Review**: Updated cost elements that may require verification.
  - **User Input**: Costs directly modified by user inputs.
  - **Updated**: Costs recalculated based on applied algorithms.

Generated Files
-------------------

At the end of the process, ACCERT generates several files for further review:

- **Variable-Affected Cost Elements**: Shows the cost elements affected by updated variables, ordered by variable name.
- **Updated Cost Elements**: Lists all cost elements with recalculated values, ordered by cost element name.
- **Updated Account Table**: Provides the total rolled-up costs for each account.

These files can be used for deeper analysis and review.

Example Output
----------------

output.out ::



    ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    :::'###:::::'######:::'######::'########:'########::'########:
    ::'## ##:::'##... ##:'##... ##: ##.....:: ##.... ##:... ##..::
    :'##:. ##:: ##:::..:: ##:::..:: ##::::::: ##:::: ##:::: ##::::
    '##:::. ##: ##::::::: ##::::::: ######::: ########::::: ##::::
    #########: ##::::::: ##::::::: ##...:::: ##.. ##:::::: ##::::
    ##.... ##: ##::: ##: ##::: ##: ##::::::: ##::. ##::::: ##::::
    ##:::: ##:. ######::. ######:: ########: ##:::. ##:::: ##::::
    ..:::::..:::.......::::......::........::..:::::..:::::..:::::


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

    [Updating] Variable ref_211_mat
    [Updated]  Changed from 10.203885 million to 10.3 million

    [Updating] Variable c_213_fac
    [Updated]  Changed from 1.7706643 million to 1.79 million

    [USER_INPUT] New account useraddcoa 'a user added coa' 9000000.0 

    [Updating] Inserting new COA under COA 21
    [Updating] Current COAs under COA 21: 211, 212, 213, 214, 215, 216, 217, 218
    
    [Updating] Variable c_221.12_cs_weight
    [Updated]  Changed from 536.0 ton to 538.0 ton

    [Updating] Sup Variable c_221.12_tol_weight, running algorithm: [rpv_mass], 
    [Updating] with formulation: weight_of_carbon_steel+weight_of_stainless_steel
    [Updated]  Reference value is : 5.54e+02 ton, calculated value is: 5.56e+02 ton
    
    [Updating] Variable c_221.12_ss_weight
    [Unit Changed] Converted input from 40340.0 lbs to 18.29790128 ton
    [Updated]  Changed from 18.3 ton to 18.29790128 ton

    [Updating] Sup Variable c_221.12_tol_weight, running algorithm: [rpv_mass], 
    [Updating] with formulation: weight_of_carbon_steel+weight_of_stainless_steel
    [Updated]  Reference value is : 5.56e+02 ton, calculated value is: 5.56e+02 ton
    
    [Updating] Sub Variable p_in
    [Updated]  Changed from 67.0 bar to 68.0 bar

    [Updating] Sup Variable n_231, running algorithm: [tur_exp_n], 
    [Updating] with formulation: (-0.0032) *v_1+ 1.2497
    [Updated]  Reference value is : 1.03e+00 , calculated value is: 1.03e+00 
    
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

    variable "c_221.12_ss_weight" affects cost element(s):
    220A.211_fac

    variable "c_221.12_tol_weight" affects cost element(s):
    221.12_lab, 221.12_mat

    variable "ref_211_fac" affects cost element(s):
    211_fac

    variable "ref_211_mat" affects cost element(s):
    211_mat

    variable "c_213_fac" affects cost element(s):
    213_fac

    variable "mwe" affects cost element(s):
    241_fac, 242_fac, 246_fac, 241_lab, 242_lab, 245_lab, 246_lab, 241_mat, 242_mat, 245_mat, 246_mat

    ====================================== Updating cost elements ======================================


    [Updating] Cost element [220A.211_fac], running algorithm: [unit_weights], 
    [Updating] with formulation: weight_of_carbon_steel*0.14+weight_of_stainless_steel*0.31
    [Updated]  Reference value is : $70,000,000 , calculated value is: $80,992,349  
    
    [Updating] Cost element [262_mat], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $4,510,480  , calculated value is: $4,051,196   
    
    [Updating] Cost element [237_mat], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $9,795,180  , calculated value is: $8,797,774   
    
    [Updating] Cost element [234_mat], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $2,022,430  , calculated value is: $1,816,496   
    
    [Updating] Cost element [233_mat], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $3,277,750  , calculated value is: $2,943,986   
    
    [Updating] Cost element [226.7_mat], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $2,393,290  , calculated value is: $2,092,649   
    
    [Updating] Cost element [226.4_mat], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $2,705,780  , calculated value is: $2,365,884   
    
    [Updating] Cost element [222_mat], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $1,795,340  , calculated value is: $1,569,811   
    
    [Updating] Cost element [222.14_mat], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $28,193     , calculated value is: $24,651      
    
    [Updating] Cost element [222.12_mat], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $1,119,110  , calculated value is: $978,525     
    
    [Updating] Cost element [222.11_mat], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $437,412    , calculated value is: $382,465     
    
    [Updating] Cost element [213_mat], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $32,364,600 , calculated value is: $29,069,025  
    
    [Updating] Cost element [262_lab], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $35,896,600 , calculated value is: $32,241,396  
    
    [Updating] Cost element [237_lab], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $13,130,900 , calculated value is: $11,793,800  
    
    [Updating] Cost element [234_lab], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $20,317,400 , calculated value is: $18,248,523  
    
    [Updating] Cost element [233_lab], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $22,964,300 , calculated value is: $20,625,921  
    
    [Updating] Cost element [226.7_lab], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $24,625,600 , calculated value is: $21,532,141  
    
    [Updating] Cost element [226.4_lab], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $18,621,600 , calculated value is: $16,282,395  
    
    [Updating] Cost element [222_lab], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $18,143,900 , calculated value is: $15,864,698  
    
    [Updating] Cost element [222.14_lab], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $281,935    , calculated value is: $246,518     
    
    [Updating] Cost element [222.12_lab], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $11,381,600 , calculated value is: $9,951,838   
    
    [Updating] Cost element [222.11_lab], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $4,374,120  , calculated value is: $3,824,650   
    
    [Updating] Cost element [213_lab], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $31,835,200 , calculated value is: $28,593,512  
    
    [Updating] Cost element [262_fac], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $86,813,900 , calculated value is: $77,974,010  
    
    [Updating] Cost element [234_fac], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $44,874,300 , calculated value is: $40,304,926  
    
    [Updating] Cost element [233_fac], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $56,339,400 , calculated value is: $50,602,616  
    
    [Updating] Cost element [226.7_fac], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $28,179,300 , calculated value is: $24,639,456  
    
    [Updating] Cost element [226.4_fac], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $19,443,300 , calculated value is: $17,000,820  
    
    [Updating] Cost element [222_fac], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $8,265,360  , calculated value is: $7,227,068   
    
    [Updating] Cost element [222.14_fac], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $15,028     , calculated value is: $13,140      
    
    [Updating] Cost element [222.12_fac], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $4,394,350  , calculated value is: $3,842,334   
    
    [Updating] Cost element [222.11_fac], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $3,780,840  , calculated value is: $3,305,891   
    
    [Updating] Cost element [213_fac], running algorithm: [MWth_scale], 
    [Updating] with formulation: cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale
    [Updated]  Reference value is : $1,770,660  , calculated value is: $1,607,731   
    
    [Updating] Cost element [231_fac], running algorithm: [dev_factor_ref], 
    [Updating] with formulation: cost_of_ref*scale/factor
    [Updated]  Reference value is : $356,031,000, calculated value is: $357,314,737 
    
    [Updating] Cost element [211_mat], running algorithm: [esc_1987], 
    [Updating] with formulation: escalator*cost_in_1987
    [Updated]  Reference value is : $29,075,000 , calculated value is: $29,348,892  
    
    [Updating] Cost element [211_fac], running algorithm: [esc_1987], 
    [Updating] with formulation: escalator*cost_in_1987
    [Updated]  Reference value is : $810,015    , calculated value is: $769,340     
    
    [Updating] Cost element [221.12_mat], running algorithm: [cost_by_weight], 
    [Updating] with formulation: tol_weight*coat_per_unit
    [Updated]  Reference value is : $639,771    , calculated value is: $712,061     
    
    [Updating] Cost element [221.12_lab], running algorithm: [cost_by_weight], 
    [Updating] with formulation: tol_weight*coat_per_unit
    [Updated]  Reference value is : $6,397,710  , calculated value is: $7,120,613   
    
    [Updating] Cost element [246_mat], running algorithm: [MWe_scale], 
    [Updating] with formulation: cost_of_ref*(electric_power/electric_power_of_ref)^electric_power_scale
    [Updated]  Reference value is : $20,755,500 , calculated value is: $19,668,071  
    
    [Updating] Cost element [245_mat], running algorithm: [MWe_scale], 
    [Updating] with formulation: cost_of_ref*(electric_power/electric_power_of_ref)^electric_power_scale
    [Updated]  Reference value is : $12,309,900 , calculated value is: $11,664,966  
    
    [Updating] Cost element [242_mat], running algorithm: [MWe_scale], 
    [Updating] with formulation: cost_of_ref*(electric_power/electric_power_of_ref)^electric_power_scale
    [Updated]  Reference value is : $849,719    , calculated value is: $805,202     
    
    [Updating] Cost element [241_mat], running algorithm: [MWe_scale], 
    [Updating] with formulation: cost_of_ref*(electric_power/electric_power_of_ref)^electric_power_scale
    [Updated]  Reference value is : $251,723    , calculated value is: $238,535     
    
    [Updating] Cost element [246_lab], running algorithm: [MWe_scale], 
    [Updating] with formulation: cost_of_ref*(electric_power/electric_power_of_ref)^electric_power_scale
    [Updated]  Reference value is : $33,434,500 , calculated value is: $31,682,879  
    
    [Updating] Cost element [245_lab], running algorithm: [MWe_scale], 
    [Updating] with formulation: cost_of_ref*(electric_power/electric_power_of_ref)^electric_power_scale
    [Updated]  Reference value is : $51,236,700 , calculated value is: $48,552,394  
    
    [Updating] Cost element [242_lab], running algorithm: [MWe_scale], 
    [Updating] with formulation: cost_of_ref*(electric_power/electric_power_of_ref)^electric_power_scale
    [Updated]  Reference value is : $4,446,170  , calculated value is: $4,213,231   
    
    [Updating] Cost element [241_lab], running algorithm: [MWe_scale], 
    [Updating] with formulation: cost_of_ref*(electric_power/electric_power_of_ref)^electric_power_scale
    [Updated]  Reference value is : $1,720,620  , calculated value is: $1,630,477   
    
    [Updating] Cost element [246_fac], running algorithm: [MWe_scale], 
    [Updating] with formulation: cost_of_ref*(electric_power/electric_power_of_ref)^electric_power_scale
    [Updated]  Reference value is : $4,510,910  , calculated value is: $4,274,583   
    
    [Updating] Cost element [242_fac], running algorithm: [MWe_scale], 
    [Updating] with formulation: cost_of_ref*(electric_power/electric_power_of_ref)^electric_power_scale
    [Updated]  Reference value is : $52,157,800 , calculated value is: $49,425,260  
    
    [Updating] Cost element [241_fac], running algorithm: [MWe_scale], 
    [Updating] with formulation: cost_of_ref*(electric_power/electric_power_of_ref)^electric_power_scale
    [Updated]  Reference value is : $32,067,500 , calculated value is: $30,387,462  
    


    +-----+--------------+-----------------+--------------+----------+---------+
    | ind | cost_element |    cost_2017    | sup_cost_ele | account  | updated |
    +-----+--------------+-----------------+--------------+----------+---------+
    |  1  |   211_fac    |    769339.89    |    21_fac    |   211    |    1    |
    |  3  |   213_fac    |   1607731.2757  |    21_fac    |   213    |    1    |
    |  24 | 220A.211_fac |    80992349.0   |   220A_fac   | 220A.211 |    1    |
    |  56 |  222.11_fac  |  3305891.38618  |   222_fac    |  222.11  |    1    |
    |  57 |  222.12_fac  |  3842334.19324  |   222_fac    |  222.12  |    1    |
    |  59 |  222.14_fac  |   13140.40834   |   222_fac    |  222.14  |    1    |
    |  60 |   222_fac    |  7227068.03119  |    22_fac    |   222    |    1    |
    |  70 |  226.4_fac   |  17000819.51909 |   226_fac    |  226.4   |    1    |
    |  72 |  226.7_fac   |  24639455.98951 |   226_fac    |  226.7   |    1    |
    |  79 |   231_fac    | 357314736.94409 |    23_fac    |   231    |    1    |
    |  80 |   233_fac    |  50602616.17799 |    23_fac    |   233    |    1    |
    |  81 |   234_fac    |  40304926.41671 |    23_fac    |   234    |    1    |
    |  86 |   241_fac    |  30387462.00698 |    24_fac    |   241    |    1    |
    |  87 |   242_fac    |  49425260.42616 |    24_fac    |   242    |    1    |
    |  91 |   246_fac    |  4274583.42751  |    24_fac    |   246    |    1    |
    | 100 |   262_fac    |  77974010.29805 |    26_fac    |   262    |    1    |
    | 105 |   213_lab    |  28593511.51632 |    21_lab    |   213    |    1    |
    | 153 |  221.12_lab  |    7120613.12   |   221_lab    |  221.12  |    1    |
    | 158 |  222.11_lab  |  3824649.97319  |   222_lab    |  222.11  |    1    |
    | 159 |  222.12_lab  |  9951838.39114  |   222_lab    |  222.12  |    1    |
    | 161 |  222.14_lab  |   246518.13699  |   222_lab    |  222.14  |    1    |
    | 162 |   222_lab    |  15864698.41154 |    22_lab    |   222    |    1    |
    | 172 |  226.4_lab   |  16282394.82075 |   226_lab    |  226.4   |    1    |
    | 174 |  226.7_lab   |  21532140.6995  |   226_lab    |  226.7   |    1    |
    | 182 |   233_lab    |  20625921.3511  |    23_lab    |   233    |    1    |
    | 183 |   234_lab    |  18248522.96556 |    23_lab    |   234    |    1    |
    | 186 |   237_lab    |  11793800.44898 |    23_lab    |   237    |    1    |
    | 188 |   241_lab    |  1630476.88411  |    24_lab    |   241    |    1    |
    | 189 |   242_lab    |  4213230.93233  |    24_lab    |   242    |    1    |
    | 192 |   245_lab    |  48552393.97536 |    24_lab    |   245    |    1    |
    | 193 |   246_lab    |  31682879.09389 |    24_lab    |   246    |    1    |
    | 202 |   262_lab    |  32241395.7319  |    26_lab    |   262    |    1    |
    | 205 |   211_mat    |    29348892.1   |    21_mat    |   211    |    1    |
    | 207 |   213_mat    |  29069025.43541 |    21_mat    |   213    |    1    |
    | 255 |  221.12_mat  |    712061.312   |   221_mat    |  221.12  |    1    |
    | 260 |  222.11_mat  |   382464.99767  |   222_mat    |  222.11  |    1    |
    | 261 |  222.12_mat  |   978525.48003  |   222_mat    |  222.12  |    1    |
    | 263 |  222.14_mat  |   24650.98339   |   222_mat    |  222.14  |    1    |
    | 264 |   222_mat    |  1569810.65229  |    22_mat    |   222    |    1    |
    | 274 |  226.4_mat   |  2365883.97552  |   226_mat    |  226.4   |    1    |
    | 276 |  226.7_mat   |  2092649.01457  |   226_mat    |  226.7   |    1    |
    | 284 |   233_mat    |   2943986.3474  |    23_mat    |   233    |    1    |
    | 285 |   234_mat    |  1816495.55638  |    23_mat    |   234    |    1    |
    | 288 |   237_mat    |  8797773.63743  |    23_mat    |   237    |    1    |
    | 290 |   241_mat    |   238534.78189  |    24_mat    |   241    |    1    |
    | 291 |   242_mat    |   805202.41029  |    24_mat    |   242    |    1    |
    | 294 |   245_mat    |  11664966.33165 |    24_mat    |   245    |    1    |
    | 295 |   246_mat    |  19668070.89779 |    24_mat    |   246    |    1    |
    | 304 |   262_mat    |  4051196.01256  |    26_mat    |   262    |    1    |
    +-----+--------------+-----------------+--------------+----------+---------+


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
    |   2   |   214           | Security building                               |     0.15 |     2.69 |     1.05 |       3.88 |    Unchanged     |
    |   2   |   215           | Primary auxiliary building and tunnels          |     8.95 |    29.98 |    13.71 |      52.63 |    Unchanged     |
    |   2   |   216           | Waste processing building                       |     1.86 |    25.71 |    13.37 |      40.94 |    Unchanged     |
    |   2   |   217           | Fuel storage building                           |     2.84 |    12.84 |    12.47 |      28.15 |    User Input    |
    |   2   |   218           | Other structures                                |     7.15 |    77.56 |    39.76 |     124.47 |     Updated      |
    |   3   |    218A         | Control Room/Diesel Generator Building          |     4.17 |    31.86 |    15.54 |      51.57 |    Unchanged     |
    |   3   |    218B         | Administration + Services Building              |     2.34 |     9.66 |     6.94 |      18.94 |    Unchanged     |
    |   3   |    218D         | Fire Pump House, Including Foundations          |     0.11 |     0.68 |     0.42 |       1.22 |    Unchanged     |
    |   3   |    218E         | Emergency Feed Pump Building                    |     0.06 |     4.87 |     2.18 |       7.12 |    Unchanged     |
    |   3   |    218F         | Manway Tnls. (Radiological Ctrl Access Tunnels) |        0 |     1.54 |     0.64 |       2.17 |    Unchanged     |
    |   3   |    218G         | Elec. Tunnels                                   |     0.03 |     0.12 |     0.05 |       0.19 |    Unchanged     |
    |   3   |    218H         | Non- Essen. Switchgear Bldg.                    |     0.05 |     0.82 |     0.65 |       1.53 |    Unchanged     |
    |   3   |    218J         | Main Steam + Feedwater Pipe Enc.                |     0.09 |    15.06 |     7.26 |      22.42 |    Unchanged     |
    |   3   |    218K         | Pipe Tunnels                                    |        0 |     0.58 |     0.32 |       0.90 |    Unchanged     |
    |   3   |    218L         | Technical Support Center                        |     0.15 |     1.42 |     0.68 |       2.25 |    Unchanged     |
    |   3   |    218P         | Containment Equipment Hatch Missile Shield      |        0 |     0.48 |     0.15 |       0.63 |    Unchanged     |
    |   3   |    218S         | Waste Water Treatment                           |     0.02 |     1.38 |     0.78 |       2.19 |    Unchanged     |
    |   3   |    218T         | Ultimate Heat Sink Structures                   |     0.12 |     8.91 |     4.07 |      13.10 |    Unchanged     |
    |   3   |    218V         | Control Rm Emergency Air Intake Building        |        0 |     0.17 |     0.08 |       0.25 |    Unchanged     |
    |   1   |  22             | Reactor plant equipment                         |   690.49 |   134.21 |    39.01 |     863.71 |     Updated      |
    |   2   |   220A          | Nuclear steam supply (NSSS)                     |   525.71 |        0 |        0 |     525.71 |     Updated      |
    |   3   |    220A.211     | Vessel Structure (NSSS)                         |    80.99 |        0 |        0 |      80.99 | Ready for Review |
    |   3   |    220A.2121    | Lower Internals (NSSS)                          |    31.78 |        0 |        0 |      31.78 |    Unchanged     |
    |   3   |    220A.2122    | Upper Internals (NSSS)                          |    31.78 |        0 |        0 |      31.78 |    Unchanged     |
    |   3   |    220A.2131    | Control Rods (NSSS)                             |     3.10 |        0 |        0 |       3.10 |    Unchanged     |
    |   3   |    220A.2132    | Control Rod Drives (NSSS)                       |    34.90 |        0 |        0 |      34.90 |    Unchanged     |
    |   3   |    220A.221     | Main Coolant Pumps (NSSS)                       |   125.24 |        0 |        0 |     125.24 |    Unchanged     |
    |   3   |    220A.222     | Reactor Coolant Piping (NSSS)                   |    11.40 |        0 |        0 |      11.40 |    Unchanged     |
    |   3   |    220A.223     | Steam Generators (NSSS)                         |   149.80 |        0 |        0 |     149.80 |    Unchanged     |
    |   3   |    220A.224     | Pressurizer (NSSS)                              |     8.30 |        0 |        0 |       8.30 |    Unchanged     |
    |   3   |    220A.225     | Pressurizer Relief Tank (NSSS)                  |     1.85 |        0 |        0 |       1.85 |    Unchanged     |
    |   3   |    220A.2311    | Residual Heat Removal Pumps & Drives (NSSS)     |     1.94 |        0 |        0 |       1.94 |    Unchanged     |
    |   3   |    220A.2312    | Residual Heat Removal Heat Exchanger (NSSS)     |     6.26 |        0 |        0 |       6.26 |    Unchanged     |
    |   3   |    220A.2321    | Safety Injection Pumps And Drives (NSSS)        |     1.72 |        0 |        0 |       1.72 |    Unchanged     |
    |   3   |    220A.2322    | Accumulator Tank (NSSS)                         |    15.30 |        0 |        0 |      15.30 |    Unchanged     |
    |   3   |    220A.2323    | Boron Injection Tank (NSSS)                     |     0.90 |        0 |        0 |       0.90 |    Unchanged     |
    |   3   |    220A.2324    | Boron Injection Surge Tank (NSSS)               |     0.05 |        0 |        0 |       0.05 |    Unchanged     |
    |   3   |    220A.2325    | Boron Injection Recirc. Pump & Drives (NSSS)    |     0.04 |        0 |        0 |       0.04 |    Unchanged     |
    |   3   |    220A.251     | Fuel Handling Tools (NSSS)                      |     0.40 |        0 |        0 |       0.40 |    Unchanged     |
    |   3   |    220A.254     | Fuel Storage Racks (NSSS)                       |     2.51 |        0 |        0 |       2.51 |    Unchanged     |
    |   3   |    220A.2611    | Rotating Machinery (Pumps And Motors) (NSSS)    |     2.22 |        0 |        0 |       2.22 |    Unchanged     |
    |   3   |    220A.2612    | Heat Transfer Equipment (NSSS)                  |     2.45 |        0 |        0 |       2.45 |    Unchanged     |
    |   3   |    220A.2613    | Tanks And Pressure Vessels (NSSS)               |     1.14 |        0 |        0 |       1.14 |    Unchanged     |
    |   3   |    220A.2614    | Purification And Filtration Equipment (NSSS)    |     2.45 |        0 |        0 |       2.45 |    Unchanged     |
    |   3   |    220A.262     | Maintenance Equipment (NSSS)                    |     9.19 |        0 |        0 |       9.19 |    Unchanged     |
    |   3   |    220A.27      | Instrumentation And Control (NSSS)              |        0 |        0 |        0 |          0 |    Unchanged     |
    |   2   |   221           | Reactor equipment                               |     2.39 |    11.45 |    16.93 |      30.76 |     Updated      |
    |   3   |    221.11       | Reactor Support (Field Cost 221)                |     2.32 |     1.45 |     0.14 |       3.91 |    Unchanged     |
    |   3   |    221.12       | Vessel Structure (Field Cost 221)               |        0 |     7.12 |     0.71 |       7.83 | Ready for Review |
    |   3   |    221.13       | Vessel Internals (Field Cost 221)               |        0 |     1.55 |     0.15 |       1.70 |    Unchanged     |
    |   3   |    221.14       | Transport To Site (Field Cost 221)              |        0 |        0 |    15.78 |      15.78 |    Unchanged     |
    |   3   |    221.21       | Control Rod System (Field Cost 221)             |     0.07 |     1.33 |     0.13 |       1.53 |    Unchanged     |
    |   2   |   222           | Main heat transfer transport system             |     7.24 |    16.13 |     1.60 |      24.96 |     Updated      |
    |   3   |    222.11       | Fluid Circulation Drive System (Field Cost 222) |     3.31 |     3.82 |     0.38 |       7.51 | Ready for Review |
    |   3   |    222.12       | Reactor Coolant Piping System (Field Cost 222)  |     3.84 |     9.95 |     0.98 |      14.77 | Ready for Review |
    |   3   |    222.13       | Steam Generator Equipment (Field Cost 222)      |     0.08 |     2.11 |     0.21 |       2.39 |    Unchanged     |
    |   3   |    222.14       | Pressurizing System (Field Cost 222)            |     0.01 |     0.25 |     0.02 |       0.28 | Ready for Review |
    |   2   |   223           | Safeguards system                               |    17.83 |    15.62 |     1.93 |      35.38 |     Updated      |
    |   3   |    223.1        | Residual Heat Removal Sys (Field Cost 223)      |     2.97 |     3.51 |     0.33 |       6.81 |    Unchanged     |
    |   3   |    223.3        | Safety Injection System (Field Cost 223)        |     3.74 |     5.69 |     0.95 |      10.38 |    Unchanged     |
    |   3   |    223.4        | Containment Spray System (Field Cost 223)       |     8.66 |     5.86 |     0.59 |      15.11 |    Unchanged     |
    |   3   |    223.5        | Combustible Gas Control System (Field Cost 223) |     2.46 |     0.56 |     0.06 |       3.08 |    Unchanged     |
    |   2   |   224           | Radwaste processing                             |    46.05 |    11.43 |     2.19 |      59.67 |    Unchanged     |
    |   2   |   225           | Fuel handling and storage                       |     6.28 |     2.44 |     0.30 |       9.02 |    Unchanged     |
    |   2   |   226           | Other reactor plant equipment                   |    47.45 |    43.00 |     5.09 |      95.54 |     Updated      |
    |   3   |    226.1        | Inert Gas Sys                                   |     2.06 |     1.34 |     0.13 |       3.53 |    Unchanged     |
    |   3   |    226.3        | Reactor Makeup Water Sys                        |     2.27 |     1.56 |     0.41 |       4.25 |    Unchanged     |
    |   3   |    226.4        | Coolant Treatment & Recycle                     |    17.00 |    16.28 |     2.37 |      35.65 | Ready for Review |
    |   3   |    226.6        | Fluid Leak Detection Sys                        |     0.44 |     0.05 |     0.00 |       0.49 |    Unchanged     |
    |   3   |    226.7        | Aux Cool Sys (Broken Down Further)              |    24.64 |    21.53 |     2.09 |      48.26 | Ready for Review |
    |   3   |    226.8        | Maintenance Equipment                           |        0 |     1.52 |        0 |       1.52 |    Unchanged     |
    |   3   |    226.9        | Sampling Equip                                  |     1.04 |     0.72 |     0.08 |       1.83 |    Unchanged     |
    |   2   |   227           | Reactor instrumentation and control             |    37.54 |    21.96 |     1.92 |      61.42 |    Unchanged     |
    |   2   |   228           | Reactor plant miscellaneous items               |        0 |    12.18 |     9.06 |      21.23 |    Unchanged     |
    |   1   |  23             | Turbine plant equipment                         |   485.39 |   113.82 |    22.11 |     621.33 |     Updated      |
    |   2   |   231           | Turbine generator                               |   357.31 |    21.75 |     4.00 |     383.06 | Ready for Review |
    |   2   |   233           | Condensing systems                              |    50.60 |    20.63 |     2.94 |      74.17 | Ready for Review |
    |   2   |   234           | Feedwater heating system                        |    40.30 |    18.25 |     1.82 |      60.37 | Ready for Review |
    |   2   |   235           | Other turbine plant equipment                   |    31.85 |    28.33 |     3.43 |      63.61 |    Unchanged     |
    |   2   |   236           | Instrumentation and control                     |     5.32 |    13.08 |     1.12 |      19.53 |    Unchanged     |
    |   2   |   237           | Turbine plant miscellaneous items               |        0 |    11.79 |     8.80 |      20.59 | Ready for Review |
    |   1   |  24             | Electric plant equipment                        |    88.56 |    94.19 |    37.77 |     220.52 |     Updated      |
    |   2   |   241           | Switchgear                                      |    30.39 |     1.63 |     0.24 |      32.26 | Ready for Review |
    |   2   |   242           | Station service equipment                       |    49.43 |     4.21 |     0.81 |      54.44 | Ready for Review |
    |   2   |   243           | Switchboards                                    |     4.48 |     1.01 |     0.36 |       5.84 |    Unchanged     |
    |   2   |   244           | Protective equipment                            |        0 |     7.10 |     5.04 |      12.14 |    Unchanged     |
    |   2   |   245           | Electric structure and wiring contnr.           |        0 |    48.55 |    11.66 |      60.22 | Ready for Review |
    |   2   |   246           | Power and control wiring                        |     4.27 |    31.68 |    19.67 |      55.63 | Ready for Review |
    |   1   |  25             | Miscellaneous plant equipment subtotal          |    53.18 |    64.63 |    15.26 |     133.07 |     Updated      |
    |   2   |   251           | Transportation and lifting equipment            |    14.42 |     2.42 |     0.24 |      17.08 |    Unchanged     |
    |   2   |   252           | Air, water and steam service systems            |    24.87 |    44.37 |    12.61 |      81.85 |    Unchanged     |
    |   2   |   253           | Communications equipment                        |     5.55 |    11.04 |     1.69 |      18.28 |    Unchanged     |
    |   2   |   254           | Furnishings and fixtures                        |     6.18 |     1.43 |     0.18 |       7.80 |    Unchanged     |
    |   2   |   255           | Waste water treatment equipment                 |     2.16 |     5.37 |     0.54 |       8.07 |    Unchanged     |
    |   1   |  26             | Main condenser heat rejection system            |    78.47 |    39.88 |     8.26 |     126.61 |     Updated      |
    |   2   |   261           | Structures                                      |     0.50 |     7.64 |     4.20 |      12.35 |    Unchanged     |
    |   2   |   262           | Mechanical equipment                            |    77.97 |    32.24 |     4.05 |     114.27 | Ready for Review |
    +-------+-----------------+-------------------------------------------------+----------+----------+----------+------------+------------------+
    Successfully created excel file pwr12-be_variable_affected_cost_elements.xlsx
    Successfully created excel file pwr12-be_updated_cost_element.xlsx
    Successfully created excel file pwr12-be_updated_account.xlsx

