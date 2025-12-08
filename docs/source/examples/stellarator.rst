Stellarator Example
===============================

The fusion example demonstrates the integration of ACCERT with a large tokamak fusion reactor model 
This tutorial demonstrates how to run the **Stellarator** model introduced in :ghpull:`47`.  
It extends ACCERT’s fusion modeling capabilities to include stellarator‐specific cost elements,
variables, and LCOE evaluation, the algorithms are leveraged from UKAEA's `PROCESS <https://github.com/ukaea/PROCESS>`_.


Prerequisites
--------------

- ACCERT installation (see :doc:`Installation Guide <install>`).
- MySQL database initialized with the updated schema containing the *stellarator* algorithms and variables.
- ACCERT main branch after PR #47.

New Features
-------------

- Added stellarator-specific cost elements and algorithms.
- Extended LCOE framework to support stellarator plants.
- Unified fusion output file naming convention.

General Input Structure
------------------------

The input file for the fusion model is located at ``accert/tutorial/stellarator.son``.

.. code-block:: json

   accert{
       ref_model = "stellarator"
       var("csi"){value = 16 unit = million} 
       var("lsa"){value = 2 unit = N/A}
       var("denstl"){value = 7800 unit = 'kg/m3'}
   }

- **accert{}**: Denotes the start of the ACCERT input configuration.
- **ref_model**: Specifies the reference model as "stellarator".
- **var("csi"){value = 16 unit = million}**: Represents the variable for the algorithm, it is the allowance for site costs in million USD.
- **var("lsa"){value = 2 unit = N/A}**: Represents the variable for the algorithm, it is the Level of safety assurance switch, 1 is truly passively safe plant, 2 and 3 are in-between, 4 is like the current fission plant.
- **var("denstl"){value = 7800 unit = 'kg/m3'}**: Represents the variable for the algorithm, it is the density of steel in kg/m3.



Running the Example
-------------------

Please follow the :doc:`Installation Guide <../user/install>` before running the fusion example.

Using command line
~~~~~~~~~~~~~~~~~~~

To run the fusion example with Python, execute the following command:

.. code-block:: console

    > cd ACCERT/tutorial
    > python ../src/Main.pi -i stellarator.son 

Interpreting the Results
------------------------

The output will be generated in the ``tutorial`` directory, as ``output.out``, which contains screen outputs and the following Excel files: 

- **stellarator_updated_account.xlsx**: Contains the updated cost breakdown for the stellarator model.
- **stellarator_LCOE_results.xlsx**: Contains the LCOE analysis results specific to the stellarator configuration.


