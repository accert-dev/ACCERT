
Using NECOST
==================

This guide provides instructions to use  NE-COST, to calculate the levelized cost of electricity at equilibrium (LCAE).

Using NE-COST via Python
-------------------------

1. Installation
   
   Navigate to the ACCERT/src directory and run the setup.py file to install the package.

   .. code-block:: shell

      $ cd ACCERT/src
      $ ./setup_necost.sh

2. Prepare Your Input File

   NECOST requires an input file in the SON format. The input file should contain the following information:

   construction_interest_rate
   operations_interest_rate
   fuel_cycles
   reactors
   capital_costs
   om_costs
   fuel_costs
   fuel_inputs

   Example input files are provided in ``tutorial/necost``:

   * ``EG01.son``: once-through PWR UOX reference case.
   * ``EG13.son``: two-stage PWR UOX and PWR MOX case with report energy-fraction LCAE weighting.
   * ``EG23.son``: fast-reactor driver and blanket case with two explicit islands.
   * ``AP1000_ACCERT_NECost.son``: runs ACCERT first, reads the ACCERT OCC post-process CSV, and uses that OCC as the NEcost capital cost input.

3. Run NECOST
   
   To run NECOST, navigate to the directory contain the input file and run the following command:

   .. code-block:: shell

      $ python src/necostmain.py -i tutorial/necost/EG01.son
      $ python src/necostmain.py -i tutorial/necost/EG13.son
      $ python src/necostmain.py -i tutorial/necost/EG23.son

   To run ACCERT and NEcost together:

   .. code-block:: shell

      $ python src/necostmain.py -i tutorial/necost/AP1000_ACCERT_NECost.son

   You can also run the Python workflow driver:

   .. code-block:: shell

      $ python tutorial/necost/accert_necost_workflow.py

   To run the EG23 two-island Python example:

   .. code-block:: shell

      $ python tutorial/necost/eg23_two_island_example.py

   The output file 'NECOST_results.csv' will contain the LCAE and other relevant information.
   Multi-reactor cases also write ``NECOST_reactor_results.csv`` with the per-reactor details before the weighted cycle result is calculated.

   In a ``fuel_cycles`` reactor block, ``fleet_capacity`` is the reactor island's electric capacity in MWe. It is calculated from the reactor power block as ``reference_thermal * net_thermal_efficiency / 100 / 1e6`` when the reactor is specified by thermal power, or from ``reference_net_electrical / 1e6`` when the reactor is specified by net electrical power. ``fleet_capacity`` is optional when ``fleet_energy``, ``energy_fraction``, or ``mass_fraction`` is supplied. If ``fleet_capacity`` is supplied together with ``energy_fraction`` or ``mass_fraction``, ACCERT checks that the MWe value is consistent with the reactor power block.

   ``EG13.son`` follows the report's two-island LCAE weighting. The UOX LWR island uses ``energy_fraction = 0.902`` and the MOX PWR island uses ``energy_fraction = 0.098``.
   ``EG23.son`` follows the report's two-island structure. The driver island uses ``energy_fraction = 0.954`` and the blanket island uses ``energy_fraction = 0.046`` for the weighted LCAE calculation. The supporting report mass fractions are retained as ``mass_fraction = 0.8`` for driver fuel and ``mass_fraction = 0.2`` for blanket fuel. Its ``fleet_capacity`` values are derived from the report's thermal power and efficiency: driver ``9.54E8 Wt * 40% / 1e6 = 381.6 MWe`` and blanket ``4.57E7 Wt * 40% / 1e6 = 18.28 MWe``. The report table's low/mode/high values are represented in each ``distribution`` block, while the table's mean suggested defaults are retained in ``cost_value`` where the schema supports that field.

ACCERT to NEcost coupling
-------------------------

The optional ``accert_coupling`` block lets a NEcost SON file use ACCERT's total OCC as the NEcost ``capital_cost`` input.
The bridge reads ACCERT post-processing metric ``total_OCC`` from ``value_2024_dollar_per_kw`` and writes it into the selected NEcost capital cost item in ``$/kWe``.

.. code-block:: son

   accert_coupling {
      accert_input = "../accert/AP1000.son"
      capital_cost_id = "capital_cost"
      occ_metric = "total_OCC"
      uncertainty_fraction = 0.0
   }

If ``accert_post_csv`` is provided instead of ``accert_input``, NEcost uses the existing ACCERT post-process CSV without rerunning ACCERT.

4. Analyze the Results
   
   The output file 'NECOST_results.csv' contains the following information:

   - Levelized Hydride Cap
   - Levelized Hydride Cost
   - Levelized Hydride OM
   - Levelized FCC
   - HM_mass_direct_spec
   - t_cyc
   - L_direct_spec


   **The Levelized Hydride Cap** is the capital cost of the reactor divided by the net electrical energy produced.

   **The Levelized Hydride Cost** is the total cost of the reactor divided by the net electrical energy produced.

   **The Levelized Hydride OM** is the operational and maintenance cost of the reactor divided by the net electrical energy produced.

   **The Levelized FCC** is the fuel cycle cost divided by the net electrical energy produced.

   **HM_mass_direct_spec** is the heavy metal mass in the core (tonn).

   **t_cyc** is the cycle length of the reactor.

   **L_direct_spec** is the capacity factor of the reactor.


Using NE-COST via NEAMS Workbench
---------------------------------

1. **Open NEAMS Workbench**

   - Launch the NEAMS Workbench application on your system.

2. **Add NECOST Configuration**
   
   Navigate to the ACCERT/src directory and run the setup file to install the package.

   .. code-block:: shell

      $ cd ACCERT/src
      $ ./setup_necost.sh   


   - Navigate to `Workbench` > `Configurations`.
   - Click `Add` and select `Necost` from the list of available configurations.
   - Set the **Executable** path to ``necostmain.py`` located in the ``ACCERT/src/`` directory.
   - Load the grammar by clicking `Load Grammar`.

   .. admonition:: Windows Users!

    To begin using ACCERT, please change the `necostmain.py` file with executable permissions. You can do this by right-clicking the file, selecting `Properties`, and enabling the `Execute` permission under the `Permissions` tab.

3. **Run Necost**

   - Open one of the ``tutorial/necost/*.son`` input files within the Workbench environment.
   - Click the `Run` button to execute Necost.
   - Review the results in `NECOST_results.csv` directly within Workbench.
