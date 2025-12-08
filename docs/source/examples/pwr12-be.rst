PWR12-BE Example
================

The PWR12-BE example demonstrates the use of the PWR12-BE model for a typical Westinghouse four-loops plant with a core thermal power of 3,431 MWt (`EEDB 1988b <https://www.osti.gov/biblio/5042875>`_).

General Input Structure
------------------------

The example input file is loacted at ``ACCERT/tutorial/PWR12-BE.son``. 

Reactor Model
~~~~~~~~~~~~~

.. code-block:: console

    accert{
    ref_model = "PWR12-BE"
    ...
    }

- **accert{}**: Denotes the start of the ACCERT input configuration.
- **ref_model**: Specifies the reference model as ``PWR12-BE``.

Power Parameters
~~~~~~~~~~~~~~~~

These parameters are essential for scaling cost estimates based on the reactor's power output. The power output can be electrical or thermal, depending on the specific reactor design.

.. code-block:: console

    accert{
    ...
    power(Thermal){ value = 3000   unit = MW }  % Reference value for PWR-12BE is 3431 MW
    power(Electric){ value = 1000   unit = MW } % Reference value for PWR-12BE is 1143 MW
    ...
    }

- **power(Thermal)**: Specifies the thermal power output of the reactor.
- **power(Electric)**: Specifies the electrical power output of the reactor.

Codes of Accounts (COA) Hierarchy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The COA hierarchy for the fusion model is structured as follows:

.. code-block:: console

    l0COA(2){
        l1COA(21){
            l2COA(211){
                ...
            }
            ...
        }
        ...
    }

- **l0COA(2)**: Represents the top-level COA category, it is the level 0 COA, 2 is the COA identifier which is the direct cost.
- **l1COA(21)**: Represents the first-level COA category, it is the level 1 COA, 21 is the COA identifier which is the Structures and improvements subtotal.
- **l2COA(211)**: Represents the second-level COA category, it is the level 2 COA, 211 is the COA identifier which is the Yardwork.

Cost Element (CE) Hierarchy
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The cost element hierarchy for the Account 211 as follows:

.. code-block:: console

    ce("211_fac"){
        alg("esc_1987"){
            var(ref_211_fac){ value = 1.0 }
            var(ref_211_mat){ value = 1.0 }
        }
    }

- **ce("211_fac")**: Represents the cost element, it is the factory cost element of the Yardwork.
- **alg("esc_1987")**: Represents the algorithm used to calculate the cost element, which is the escalating based on the year 1987.
- **var(ref_211_fac)**: Represents the reference value for the cost element factory cost of 211 in 1987.
- **var(ref_211_mat)**: Represents the reference value for the cost element material cost of 211 in 1987.

Super Variables
~~~~~~~~~~~~~~~

The super variables are used to define the variables that will be depending on other variables. Here is an example of the super variable:

.. code-block:: console

    l1COA(23){
        l2COA("231"){
                ce("231_fac"){
                    alg("dev_factor_ref"){
                        var("n_231"){
                            alg("tur_exp_n"){
                                var(p_in){ value = 68  unit = bar }
                            }
                        }
                    }  
                }
            }
        }
    }

- **l1COA(23)**: Represents the first-level COA category, it is the level 1 COA, 23 is the COA identifier which is the Turbine plant equipment.
- **l2COA("231")**: Represents the second-level COA category, it is the level 2 COA, 231 is the COA identifier which is the Turbine generator.
- **ce("231_fac")**: Represents the cost element, it is the factory cost element of the Turbine generator.
- **alg("dev_factor_ref")**: Represents the algorithm used to calculate the cost element, which is the develped factory equipment cost.
- **var("n_231")**: Represents the super variable `The power function exponen` that will be depending on the variable p_in.
- **alg("tur_exp_n")**: Represents the algorithm used to calculate the super variable, which is the `interpolating equation`.
- **var(p_in)**: Represents the variable that the super variable will be depending on, which is `HP steam turbine inlet pressure`.

Unit Conversion
~~~~~~~~~~~~~~~

The unit conversion is used to convert the units of the variables. Here is an example of the unit conversion:

.. code-block:: console


    alg("unit_weights"){
        var("c_221.12_cs_weight"){value = 538 unit = ton} 
        var("c_221.12_ss_weight"){value = 40340 unit = lbs}
    }


- **alg("unit_weights")**: Represents the algorithm used to calculate the cost element, which is the unit weights.
- **var("c_221.12_cs_weight")**: Represents the variable carben steel weight of the Vessel Structure unit in ton.
- **var("c_221.12_ss_weight")**: Represents the variable stainless steel weight of the Vessel Structure unit in lbs.

Since the algorithm function required both parameters to be in the unit ton, the stainless steel weight will be converted to ton in ACCERT.

Add User-defined COA 
~~~~~~~~~~~~~~~~~~~~~

The user can add a new COA to the hierarchy. Here is an example of adding a new COA:

.. code-block:: console

    l0COA(2){
        l1COA(21){
            ...
            l2COA(new){ 
                newCOA(useraddcoa){descr = 'a user added coa'}
                total_cost{value = 9 unit = million}       
            }
        }
    }

- **l2COA(new)**: Represents the second-level COA category, it is the level 2 COA, new is the COA identifier which is the user added COA. The user added COA will assign under the COA 21.
- **newCOA(useraddcoa)**: Represents the new COA that will be added to the hierarchy, useraddcoa is the COA identifier.
- **total_cost**: Represents the cost element, it is the total cost of the user added COA.
- **value = 9 unit = million**: Represents the value of the total cost of the user added COA in million.


Add User-defined total cost
~~~~~~~~~~~~~~~~~~~~~~~~~~~

User can add a new total cost to the any account or cost element. Here is an example of adding a new total cost:

.. code-block:: console

    l0COA(2){
        l1COA(21){
            l2COA(217){
                total_cost{value = 28149700 unit = dollar}       
            }
        }
    }


- **l2COA(217)**: Represents the second-level COA category, it is the level 2 COA, 217 is the COA identifier which is the Fuel storage building.
- **total_cost**: Represents the cost element, it is the total cost of the Fuel storage building.
- **value = 28149700 unit = dollar**: Represents the value of the total cost of the Fuel storage building in dollar.

.. admonition:: Important
    :class: important
    
    ACCERT is a buttom-up cost estimator, adding total cost to higher level COA will not affect the total cost of the lower level COA, if a higher level COA has been assign a total cost, the cost element and all the lower level COA might not be accurate.

Running the Example
-------------------

Please follow the :doc:`Installation Guide <../user/install>` before running the PWR12-BE example.


Using command line
~~~~~~~~~~~~~~~~~~~

To run the PWR12-BE example with Python, execute the following command:

.. code-block:: console

    > cd ACCERT/tutorial
    > python ../src/Main.pi -i PWR12-BE.son

The output will be saved in the ``tutorial`` directory as ``output.out``, ``pwr12-be_variable_affected_cost_elements.xlsx``, ``pwr12-be_updated_cost_element.xlsx``, and ``pwr12-be_updated_account.xlsx``. The ``output.out`` file contains the cost estimation results, while the Excel files provide detailed information on the cost elements and accounts affected by the input variables.


Using NEAMS Workbench
~~~~~~~~~~~~~~~~~~~~~~

To run the PWR12-BE example using the NEAMS Workbench, follow these steps:

1. Open the NEAMS Workbench.
2. Click on the **file** menu and select **open file**, then navigate to the ``ACCERT/tutorial`` directory and select the ``PWR12-BE.son`` file.
3. In the main window, select App as `Accert`, then click on the **Run** button to execute the simulation.
4. Click on the **file** menu and select **open file**, then navigate to the ``ACCERT/tutorial`` directory and select the ``output.out`` file to view the cost estimation results.

