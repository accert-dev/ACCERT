International Adjustment Tool
=============================

The International Adjustment Tool (IAT) converts a U.S.-based COA cost
structure to a selected country using account-level localization shares,
country adjustment factors, and import tariffs. It is available as the
``iat`` Python package inside ACCERT.

IAT can run in two modes:

* ACCERT output mode, where the input is an ACCERT/CRT-style COA CSV.
* Standalone OCC mode, where the input is one or more overnight capital cost
  values and IAT allocates the total using packaged COA and cost-category
  shares.

Running IAT
-----------

The tutorial scripts are designed to run from the ACCERT repository root. They
add ``src`` to ``sys.path`` themselves, so you do not need to set
``PYTHONPATH`` for the tutorials.

.. code-block:: bash

   cd ACCERT
   python tutorial/iat/iat_ap1000_china_example.py
   python tutorial/iat/iat_lr_occ_china_example.py

When writing your own short script outside the tutorial folder, either run it
from the repository root with ``PYTHONPATH=src`` or install ACCERT in your
Python environment before importing ``iat``.

Packaged Assumptions
--------------------

The packaged assumptions are stored as CSV files in ``src/iat/data``:

* ``adjustment_factors.csv`` contains IAT v4.5 country-level adjustment
  factors and import tariffs for Korea, China, UAE, Poland, and El Salvador.
* ``lr_localization.csv`` contains large-reactor COA shares, cost-category
  shares, and localization shares.
* ``smr_localization.csv`` contains SMR COA shares, cost-category shares, and
  localization shares.

The localization CSVs store only leaf level-2 COA assumption rows such as
``11``, ``12``, ``21``, and ``22``. They do not store rollup rows such as
``10`` or ``20``, and they do not store detailed level-3 rows such as ``121``
or ``211``. During calculation, detailed input accounts inherit the level-2
superaccount assumptions. For example, ``121`` uses ``12``, ``211`` uses
``21``, and ``232.1`` uses ``23``.

The localization CSVs do not store scenario 1/2/3 U.S. costs. Standalone IAT
uses the user-provided OCC value and the packaged percentage shares to build
the U.S.-based cost structure before applying localization.

Calculation Logic
-----------------

For each cost category, IAT combines the imported and localized portions. In
the packaged IAT v4.5 assumptions, the import tariff is applied to imported
equipment cost only:

.. code-block:: text

   equipment = imported_share * base_cost * (1 + import_tariff)
             + localized_share * base_cost * country_adjustment_factor

   other categories = imported_share * base_cost
                    + localized_share * base_cost * country_adjustment_factor

The cost categories are equipment, material, labor, land, and catch-all.
Land uses an adjustment factor of ``1.0``. Financial cost accounts in the
``60`` series are passed through unchanged because financing is calculated
outside IAT by the country-specific project finance assumptions.

ACCERT CSV Input
----------------

Use ``run_adjustment`` with ``input_csv`` when the input is an ACCERT or CRT
baseline CSV.

The packaged AP1000 example can be run from the repository root with:

.. code-block:: bash

   python tutorial/iat/iat_ap1000_china_example.py

.. code-block:: python

   from pathlib import Path
   from iat import run_adjustment, print_adjustment_result

   result = run_adjustment(
       {
           "reactor_type": "ACCERT output-LR",
           "country": "China",
           "year_dollar": 2024,
           "input_csv": Path("src/crt/data/AP1000_baseline.csv"),
           "output_csv": Path("tutorial/iat/outputs/iat_ap1000_china_adjusted.csv"),
       }
   )
   print_adjustment_result(result)

The output CSV contains the original input columns plus matched IAT account
information and adjusted cost columns such as ``Adjusted Total Cost`` and
``Adjusted Factory Equipment Cost``.

Standalone OCC Input
--------------------

Use ``run_occ_scenarios`` when the input is one or more OCC totals rather than
an ACCERT output CSV.

The packaged standalone example runs large-reactor OCC scenarios for China,
Korea, UAE, Poland, and El Salvador:

.. code-block:: bash

   python tutorial/iat/iat_lr_occ_china_example.py

.. code-block:: python

   from iat import run_occ_scenarios

   result = run_occ_scenarios(
       {
           "reactor_type": "large reactor",
           "country": "Korea",
           "year_dollar": 2024,
           "occ_values": [5250, 5750, 6250],
           "scenario_names": ["LR OCC case 1", "LR OCC case 2", "LR OCC case 3"],
           "output_csv": "tutorial/iat/outputs/iat_lr_occ_korea_adjusted.csv",
       }
   )
   print(result["summary"])

Runnable standalone examples for China, Korea, UAE, Poland, and El Salvador are in
``tutorial/iat/iat_lr_occ_china_example.py``.

Connecting IAT to the Cost Reduction Framework Tool
----------------------------------------------

The IAT output can be used as a CRT baseline without modifying the original
baseline CSV in ``src/crt/data``. Pass the IAT output path to CRT with the
``baseline_csv`` config key.

.. code-block:: python

   from crt import run_one_scenario
   from iat import run_adjustment

   iat_result = run_adjustment(
       {
           "reactor_type": "ACCERT output-LR",
           "country": "China",
           "year_dollar": 2024,
           "input_csv": "src/crt/data/AP1000_baseline.csv",
           "output_csv": "tutorial/combined/iat_ap1000_china_for_crt.csv",
       }
   )

   crt_config = {
       "reactor_type": "AP1000",
       "baseline_csv": "tutorial/combined/iat_ap1000_china_for_crt.csv",
       "f_22": 250_000_000,
       "f_2321": 150_000_000,
       "land_cost_per_acre_0": 22_000,
       "startup_0": 28,
       "staggering_ratio": 0.75,
   }

   crt_result = run_one_scenario(crt_config, levers)

When CRT sees an IAT output CSV, it uses the adjusted total, equipment,
material, and labor columns as the starting baseline. The original AP1000 CSV
is left unchanged.

The connected runnable example is
``tutorial/combined/crt_iat_ap1000_china_example.py``.

Run it from the repository root with:

.. code-block:: bash

   python tutorial/combined/crt_iat_ap1000_china_example.py

Running the GUI
---------------

The IAT and Cost Reduction Framework Tool can also be run through the local GUI:

.. code-block:: bash

   cd ACCERT
   python tutorial/gui/crt_iat_gui.py

Then open ``http://127.0.0.1:8765/`` in a browser. The GUI supports three
workflows:

* ``IAT only`` applies international adjustment to either an ACCERT output CSV
  or standalone OCC values. In standalone mode, enter the scenario count and
  then one OCC value for each scenario.
* ``CRT only`` runs the Cost Reduction Framework Tool using a built-in reactor
  baseline or an optional user-provided baseline CSV.
* ``IAT then CRT`` first writes an IAT-adjusted CSV and then passes that CSV to
  CRT through ``baseline_csv``. This does not modify the packaged baseline CSVs
  in ``src/crt/data``.

The GUI writes generated CSV files and dashboard images under
``tutorial/gui_outputs``. Interactive charts show exact values on hover, and
the result panels include download links for generated CSV and PNG outputs.
