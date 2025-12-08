
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

   An example input file is provided in the tutorial directory `necost.son`.

3. Run NECOST
   
   To run NECOST, navigate to the directory contain the input file and run the following command:

   .. code-block:: shell

      $ python necostmain.py -i <input_file> 

   The output file 'NECOST_results.csv' will contain the LCAE and other relevant information.

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
   - Set the **Executable** path to `Main.py` located in the `ACCERT/src/` directory.
   - Load the grammar by clicking `Load Grammar`.

   .. admonition:: Windows Users!

    To begin using ACCERT, please change the `necostmain.py` file with executable permissions. You can do this by right-clicking the file, selecting `Properties`, and enabling the `Execute` permission under the `Permissions` tab.

3. **Run Necost**

   - Open your input file within the Workbench environment.
   - Click the `Run` button to execute Necost.
   - Review the results in `NECOST_results.csv` directly within Workbench.

