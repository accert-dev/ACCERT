Fusion Example
==============

The fusion example demonstrates the integration of ACCERT with a large tokamak fusion reactor model leveraging from UKAEA's `PROCESS <https://github.com/ukaea/PROCESS>`_.

General Input Structure
------------------------

The input file for the fusion model is located at ``accert/tutorial/fusion.son``.

Reactor Model
~~~~~~~~~~~~~~

The beginning of the input file specifies the reference model as "fusion".

.. code-block:: console

   accert{
       ref_model = "fusion"
       ...
   }

- **accert{}**: Denotes the start of the ACCERT input configuration.
- **ref_model**: Specifies the reference model as "fusion".

Codes of Accounts (COA) Hierarchy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The COA hierarchy for the fusion model is structured as follows:

.. code-block:: console

    l0COA(2){  
        l1COA(21){
            l2COA("211"){
                alg("acc211"){
                    var("csi"){value = 16 unit = million} 
                    var("lsa"){value = 4 unit = 1}
                }
            }
        }
    }

- **l0COA(2)**: Represents the top-level COA category, it is the level 0 COA, 2 is the COA identifier which is the direct cost.
- **l1COA(21)**: Represents the next-level COA category, it is the level 1 COA, 21 is the COA identifier which is the Structures and site facilities cost.
- **l2COA("211")**: Represents the next-level COA category, it is the level 2 COA, 211 is the COA identifier which is the Site improvements, facilities and land cost.
- **alg("acc211")**: Represents the algorithm for the COA category, it is the algorithm for the COA identifier 211.
- **var("csi"){value = 16 unit = million}**: Represents the variable for the algorithm, it is the allowance for site costs in million USD.
- **var("lsa"){value = 4 unit = 1}**: Represents the variable for the algorithm, it is the Level of safety assurance switch, 1 is truly passively safe plant, 2 and 3 are in-between, 4 is like the current fission plant.

Running the Example
-------------------

Please follow the :doc:`Installation Guide <../user/install>` before running the fusion example.

Using command line
~~~~~~~~~~~~~~~~~~~

To run the fusion example with Python, execute the following command:

.. code-block:: console

    > cd ACCERT/tutorial
    > python ../src/Main.pi -i fusion.son

The output will be generated in the ``tutorial`` directory as ``output.out``, and ``fusion_updated_account.xlsx``. The ``output.out`` file contains the cost estimation results, while the Excel files provide detailed information on the accounts affected by the input variables. Note that the fusion example does not generate the ``*_variable_affected_cost_elements.xlsx`` file as it does not have any cost elements associated with the input variables, there is only one account affected by the input variables.