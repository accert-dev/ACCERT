Running the Combined IAT and CRF GUI Case
=========================================

The ACCERT GUI can run a connected International Adjustment Tool (IAT) and
Cost Reduction Framework (CRF) workflow. In this workflow, IAT first converts a
U.S.-based ACCERT or CRF baseline CSV to the selected country. CRF then uses
that IAT-adjusted CSV as its baseline, without changing the packaged baseline
files in ``src/crf/data``.

Start the GUI
-------------

Run the GUI from the ACCERT repository root:

.. code-block:: bash

   cd ACCERT
   python tutorial/gui/crf_iat_gui.py

Then open ``http://127.0.0.1:8765/`` in a browser.

Choose the Workflow
-------------------

In the ``Workflow`` panel:

* Set ``Mode`` to ``IAT then CRF``.
* Set ``Output name`` to a short name for the generated files, such as
  ``ap1000_china_gui``.

This workflow creates an IAT-adjusted CSV first, then passes that CSV to CRF
through the CRF ``baseline_csv`` setting.

Set the IAT Inputs
------------------

In the ``IAT Inputs`` panel:

* Set ``Input type`` to ``ACCERT output``.
* Set ``Reactor type`` to ``Large Reactor`` for AP1000-style large-reactor
  COA inputs, or ``SMR`` for SMR-style inputs.
* Set ``Country`` to the destination country, such as ``China``, ``Korea``, or
  ``UAE``.
* Set ``Year dollar`` to the cost year, such as ``2024``.
* Set ``ACCERT CSV file`` to the input CSV path. This can be either a
  CRF/IAT-ready baseline such as ``src/crf/data/AP1000_baseline.csv`` or a raw
  ACCERT updated-account CSV such as ``ap1000_upd_acc_*.csv``. When a raw
  ACCERT account CSV is selected, the GUI automatically converts it to the
  CRF/IAT baseline format before running IAT.
* Set ``Electric output (MWe)`` to the plant electric output used for
  ``$/kWe`` displays.

IAT adjusts accounts ``10`` through ``50``. Financial cost accounts in the
``60`` series are not internationally adjusted because financing is handled by
country-specific project finance assumptions.

Set the CRF Fixed Inputs
------------------------

In the ``CRF Fixed Inputs`` panel:

* Set ``Reactor type`` to the CRF reactor baseline, such as ``AP1000``.
* Leave ``Optional CRF baseline CSV`` blank for the combined workflow. The GUI
  automatically passes the IAT output CSV to CRF.
* Set fixed project values such as ``f_22``, ``f_2321``, ``Land $/acre``,
  ``Startup months``, ``Construction duration months``, ``20s labor hours``,
  and ``Staggering ratio``.
* ``Construction duration months`` defaults to ``76`` for AP1000, ``80`` for
  SFR, and ``125`` for HTGR. ``20s labor hours`` is used when converting a raw
  ACCERT account CSV into a CRF/IAT baseline.
* Keep ``Include lever table in dashboard image`` unchecked for a compact
  dashboard image, or check it when you want the lever table included in the
  exported PNG.

Set the CRF Levers
------------------

In the ``CRF Levers`` panel, set the orderbook and reduction levers:

* ``Firm orders`` is the number of reactors in the orderbook.
* ``NOAK unit`` is the plant number used as the nth-of-a-kind comparison case.
* ``ITC %`` and ``ITC units`` define investment tax credit assumptions.
* ``Interest %`` sets the financing interest rate used by CRF.
* ``Design compl. %`` and ``Design maturity`` set first-unit design readiness.
* ``N supply chain``, ``N A/E``, and ``N construction`` set how many plants are
  needed to reach best proficiency for each category.
* ``Supply chain prof.``, ``A/E prof.``, and ``Construction prof.`` set the
  initial proficiency values.
* ``Standardization %``, ``Commercial BOP``, ``Non-safety-related RB``, and
  ``Modular civil constr.`` set the remaining CRF reduction levers.

Hover over the question-mark icons in the GUI to see each lever definition and
expected input range.

Run and Read the Results
------------------------

Click ``Run workflow``. The result area will show:

* An IAT result table comparing the original U.S. OCC baseline with the
  adjusted country OCC result, including factory, material, and labor cost
  category breakdowns for each displayed COA row.
* A CRF result summary with FOAK, NOAK, average OCC, average TCI, construction
  duration, and reduction percentage metrics.
* Interactive plots for capital cost, reduction levers, construction duration,
  cost breakdown, and the dashboard image.

Hover over bars and chart points to see exact values. Use the result buttons to
download the generated IAT CSV and CRF dashboard PNG.

Generated Outputs
-----------------

The GUI writes generated files under ``tutorial/gui_outputs``. For the combined
workflow, the important outputs are:

* The IAT-adjusted CSV, which becomes the CRF baseline for this run.
* The CRF dashboard PNG.
* Any additional CSV or image outputs linked in the result panel.

The original CSV in ``src/crf/data`` is not modified.
