International Adjustment Tool
=============================

The International Adjustment Tool (IAT) converts a U.S.-based COA cost
structure to a selected country using account-level localization shares,
country adjustment factors, and import tariffs. It is available as the
``iat`` Python package inside ACCERT.

IAT can run in two modes:

* ACCERT output mode, where the input is an ACCERT/CRF-style COA CSV.
* Standalone OCC mode, where the input is one or more overnight capital cost
  values and IAT allocates the total using packaged COA and cost-category
  shares.

Packaged Assumptions
--------------------

The packaged assumptions are stored as CSV files in ``src/iat/data``:

* ``adjustment_factors.csv`` contains country-level adjustment factors and
  import tariffs for Korea, China, and UAE.
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

For each cost category, IAT combines the imported and localized portions:

.. code-block:: text

   adjusted = imported_share * base_cost * (1 + import_tariff)
            + localized_share * base_cost * country_adjustment_factor

The cost categories are equipment, material, labor, land, and catch-all.
Land uses an adjustment factor of ``1.0``. Financial cost accounts in the
``60`` series are passed through unchanged because financing is calculated
outside IAT by the country-specific project finance assumptions.

ACCERT CSV Input
----------------

Use ``run_adjustment`` with ``input_csv`` when the input is an ACCERT or CRF
baseline CSV.

.. code-block:: python

   from pathlib import Path
   from iat import run_adjustment, print_adjustment_result

   result = run_adjustment(
       {
           "reactor_type": "ACCERT output-LR",
           "country": "China",
           "year_dollar": 2024,
           "input_csv": Path("src/crf/data/AP1000_baseline.csv"),
           "output_csv": Path("tutorial/iat_ap1000_china_adjusted.csv"),
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

.. code-block:: python

   from iat import run_occ_scenarios

   result = run_occ_scenarios(
       {
           "reactor_type": "large reactor",
           "country": "Korea",
           "year_dollar": 2024,
           "occ_values": [5250, 5750, 6250],
           "scenario_names": ["LR OCC case 1", "LR OCC case 2", "LR OCC case 3"],
           "output_csv": "tutorial/iat_lr_occ_korea_adjusted.csv",
       }
   )
   print(result["summary"])

Runnable standalone examples for China, Korea, and UAE are in
``tutorial/iat_lr_occ_china_example.py``.

Connecting IAT to the Cost Reduction Framework
----------------------------------------------

The IAT output can be used as a CRF baseline without modifying the original
baseline CSV in ``src/crf/data``. Pass the IAT output path to CRF with the
``baseline_csv`` config key.

.. code-block:: python

   from crf import run_one_scenario
   from iat import run_adjustment

   iat_result = run_adjustment(
       {
           "reactor_type": "ACCERT output-LR",
           "country": "China",
           "year_dollar": 2024,
           "input_csv": "src/crf/data/AP1000_baseline.csv",
           "output_csv": "tutorial/iat_ap1000_china_for_crf.csv",
       }
   )

   crf_config = {
       "reactor_type": "AP1000",
       "baseline_csv": "tutorial/iat_ap1000_china_for_crf.csv",
       "f_22": 250_000_000,
       "f_2321": 150_000_000,
       "land_cost_per_acre_0": 22_000,
       "startup_0": 28,
       "staggering_ratio": 0.75,
   }

   crf_result = run_one_scenario(crf_config, levers)

When CRF sees an IAT output CSV, it uses the adjusted total, equipment,
material, and labor columns as the starting baseline. The original AP1000 CSV
is left unchanged.

The connected runnable example is
``tutorial/crf_iat_ap1000_china_example.py``.
