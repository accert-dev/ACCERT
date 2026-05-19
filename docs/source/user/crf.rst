Cost Reduction Framework
========================

The Cost Reduction Framework estimates how overnight capital cost, total
capital investment, and construction duration change across a sequence of firm
reactor orders. It is available as the ``crf`` Python package inside ACCERT.

Python API
----------

Use ``run_one_scenario`` when you want to evaluate one deterministic set of
cost-reduction levers.

.. code-block:: python

   from crf import run_one_scenario, print_scenario_result

   config = {
       "reactor_type": "AP1000",  # AP1000, SFR, or HTGR
       "f_22": 250_000_000,
       "f_2321": 150_000_000,
       "land_cost_per_acre_0": 22_000,
       "construction_duration_0": 76,
       "startup_0": 28,
       "staggering_ratio": 0.75,
   }

   levers = {
       "num_orders": 10,
       "num_NOAK": 8,
       "itc_percent": 0,
       "n_itc": 0,
       "interest_percent": 6,
       "design_completion_percent": 70,
       "design_maturity": 1,
       "proc_exp": 0.5,
       "N_proc": 3,
       "ce_exp": 0.5,
       "N_cons": 5,
       "ae_exp": 0.5,
       "N_AE": 4,
       "standardization_percent": 80,
       "modularity_code": 0,
       "bop_grade_code": 0,
       "rb_grade_code": 0,
   }

   result = run_one_scenario(config, levers)
   print_scenario_result(result)

The returned dictionary includes the static lever values, per-unit metrics such
as ``OCC_1``, ``TCI_1``, and ``duration_1``, and summary metrics such as
``avg_OCC``, ``avg_TCI``, ``avg_duration``, and
``occ_reduction_from_FOAK_to_NOAK_percent``.

Visualization
-------------

Use ``save_dashboard`` to generate dashboard-style capital-cost figures from a
scenario result. The dashboard includes a lever input table, OCC, TCI,
construction duration, cost breakdowns, a staggered construction timeline, and
the FOAK-to-NOAK Total Capital Investment (TCI) reduction waterfall by lever. 
Set ``show_levers=False`` to omit the lever input table and generate the 
compact chart-only dashboard.

.. code-block:: python

   from crf import run_one_scenario, save_dashboard

   result = run_one_scenario(config, levers)
   save_dashboard(
       result,
       "cost_reduction_framework_dashboard.png",
       title="AP1000 Cost Reduction Framework",
       show_levers=True,
   )

For downstream analysis, ``results_to_dataframe`` converts the scenario result
to a chart-ready ``pandas.DataFrame`` with one row per plant, while
``levers_to_dataframe`` returns the lever table and ``waterfall_to_dataframe``
returns the FOAK-to-NOAK TCI waterfall values using the lever labels from the
Excel dashboard.

Configuration
-------------

``config`` describes the reactor and fixed project assumptions.

.. list-table::
   :header-rows: 1

   * - Key
     - Description
   * - ``reactor_type``
     - Built-in Cost Reduction Framework baseline: ``AP1000``, ``SFR``, or ``HTGR``.
   * - ``baseline_csv``
     - Optional CSV path used instead of the built-in reactor baseline. This is useful when passing an International Adjustment Tool output or an ACCERT-derived baseline into CRF. If the CSV contains International Adjustment Tool (IAT) adjusted columns, CRF uses those adjusted costs as the baseline and leaves the packaged baseline in ``src/crf/data`` unchanged.
   * - ``f_22``
     - Reactor building cost adjustment.
   * - ``f_2321``
     - Turbine generator cost adjustment.
   * - ``land_cost_per_acre_0``
     - Baseline land cost per acre.
   * - ``construction_duration_0``
     - Optional reference construction duration in months. If omitted, CRF uses the built-in duration for the selected reactor type; the current AP1000 base case uses ``76`` months.
   * - ``startup_0``
     - First-unit startup duration in months.
   * - ``staggering_ratio``
     - Fractional overlap between sequential unit construction schedules. The timeline chart delays later plant starts when needed so construction and startup finish dates do not move backward.

Levers
------

``levers`` contains the scenario variables. Percent inputs are entered as
percent values, for example ``6`` for a six-percent interest rate. Binary code
inputs use ``0`` or ``1`` and are converted internally to model labels.

.. list-table::
   :header-rows: 1

   * - Key
     - Meaning
   * - ``num_orders``
     - Number of firm plant orders to evaluate.
   * - ``num_NOAK``
     - Plant number used for nth-of-a-kind learning. Defaults to ``num_orders``.
   * - ``itc_percent``
     - Investment tax credit percentage. Values are rounded to the nearest supported Cost Reduction Framework ITC level.
   * - ``n_itc``
     - Number of first units eligible for ITC.
   * - ``interest_percent``
     - Interest rate in percent.
   * - ``design_completion_percent``
     - Initial design completion in percent.
   * - ``design_maturity``
     - Initial technology/design maturity factor.
   * - ``proc_exp``, ``N_proc``
     - Supply chain proficiency and number of plants to reach best proficiency.
   * - ``ce_exp``, ``N_cons``
     - Construction proficiency and number of plants to reach best proficiency.
   * - ``ae_exp``, ``N_AE``
     - Architect-engineer proficiency and number of plants to reach best proficiency.
   * - ``standardization_percent``
     - Cross-site standardization in percent.
   * - ``modularity_code``
     - ``0`` for stick-built, ``1`` for modularized.
   * - ``bop_grade_code``
     - ``0`` for nuclear-grade BOP, ``1`` for non-nuclear-grade BOP.
   * - ``rb_grade_code``
     - ``0`` for nuclear-grade reactor building, ``1`` for non-nuclear-grade reactor building.

Using ACCERT Output as a Baseline
---------------------------------

ACCERT updated-account CSV files, such as ``ap1000_upd_acc_*.csv``, contain
account totals but not the CRF category split or labor-hour inputs. Use
``accert_output_to_crf_baseline`` to convert that ACCERT output into the same
CSV shape as ``AP1000_baseline.csv``. The converter maps ACCERT accounts into
the CRF/IAT account structure, uses the selected CRF base case to allocate
factory, material, and labor cost shares, and distributes a user-provided total
20s labor-hour value using the selected CRF base case labor-hour proportions.

The AP1000 mapping is:

.. list-table::
   :header-rows: 1

   * - ACCERT output account
     - CRF/IAT input account
   * - ``211``
     - ``211``
   * - ``212``
     - ``212``
   * - ``213``
     - ``213``
   * - ``214``
     - ``216``
   * - ``215``
     - ``214``
   * - ``216``
     - ``215``
   * - ``217``
     - ``214``
   * - ``218A`` through ``218V``
     - ``214``
   * - ``22``
     - ``22``
   * - ``23``
     - ``232.1``
   * - ``24``
     - ``24``
   * - ``25``
     - ``26``
   * - ``26``
     - ``233``

.. code-block:: python

   from crf import accert_output_to_crf_baseline, run_one_scenario

   converted = accert_output_to_crf_baseline(
       "ap1000_upd_acc_20260518_215922.csv",
       "ap1000_accert_for_crf_iat.csv",
       reactor_type="AP1000",
       total_20s_labor_hours=28_902_455.46,
   )

   result = run_one_scenario(
       {**config, "baseline_csv": "ap1000_accert_for_crf_iat.csv"},
       levers,
   )

The same converted CSV can be passed to IAT as ``input_csv`` because it has the
standard ``Account``, ``Title``, ``Total Cost (USD)``, ``Factory Equipment
Cost``, ``Site Labor Hours``, ``Site Labor Cost``, and ``Site Material Cost``
columns.

Sampling from Excel
-------------------

Use ``run_sampling_from_excel`` to run Monte Carlo samples from an Excel workbook
with a sheet named ``Levers``.

.. code-block:: python

   from crf import run_sampling_from_excel

   run_sampling_from_excel(
       config=config,
       levers_xlsx="crf_levers.xlsx",
       n_samples=100,
       out_csv="crf_samples.csv",
       out_pkl="crf_samples.pkl",
       seed=42,
   )

The ``Levers`` sheet must include these columns:

.. code-block:: text

   Levers, Min, Low, Median, High, Max, Distribution, Type, Set, Probabilities

The lever rows must follow the order expected by the Cost Reduction Framework
because several rows share the same display name:

.. code-block:: text

   Number of firm orders
   ITC amount
   Number of plants claiming ITC
   Interest rate
   Design completion
   Design maturity (technology maturity)
   Supply chain proficiency
   Number of plants to achieve best proficiency
   Construction proficiency
   Number of plants to achieve best proficiency
   A/E proficiency
   Number of plants to achieve best proficiency
   Cross-site standardization
   Modular civil construction
   Commercial BOP
   Non-safety-related RB

Running Examples
----------------

The tutorial scripts are designed to run from the ACCERT repository root. They
add ``src`` to ``sys.path`` themselves, so you do not need to set
``PYTHONPATH`` for these examples.

.. code-block:: bash

   cd ACCERT
   python tutorial/crf/crf_ap1000_example.py
   python tutorial/crf/crf_htgr_example.py
   python tutorial/crf/crf_sfr_example.py

The connected IAT-to-CRF example first creates an IAT-adjusted AP1000 China
CSV and then passes that CSV to CRF without modifying ``src/crf/data``:

.. code-block:: bash

   python tutorial/combined/crf_iat_ap1000_china_example.py

The ACCERT-to-CRF/IAT example first runs the AP1000 ACCERT tutorial, converts
the generated ``ap1000_upd_acc_*.csv`` file into a CRF/IAT baseline, then runs
both CRF and IAT from that converted file:

.. code-block:: bash

   python tutorial/combined/accert_output_to_crf_iat_example.py

To use the local GUI for CRF, IAT, or the connected IAT-then-CRF workflow, run:

.. code-block:: bash

   python tutorial/gui/crf_iat_gui.py

Then open ``http://127.0.0.1:8765/`` in a browser.
