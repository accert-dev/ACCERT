Table References
================

This section contains reference tables used in ACCERT.

.. note::

   ACCERT reference tables use different base-dollar years by model. PWR12-BE,
   ABR1000, and LFR reference costs are in 2017 dollars; AP1000, Heatpipe, and
   LPSR reference costs are in 2018 dollars; Fusion and Stellarator reference
   costs are in 2015 dollars. Runtime account-result tables are displayed in
   the configured target dollar year using CPI-U escalation. Output account and
   cost-element CSV files retain their reference-year cost columns; ACCERT
   writes target-year OCC summary values in the separate ``*_post_*.csv`` file.

Reference-model context:

* PWR12-BE represents a Better Experience reference model for a standard
  four-loop 1,144 MWe PWR derived from DOE's `Energy Economic Data Base
  <https://www.osti.gov/servlets/purl/1963917>`_.
* ABR1000 represents the `Advanced Burner Reactor 1000 MWth reference concept
  <https://publications.anl.gov/anlpubs/2017/04/134264.pdf>`_.
* Heatpipe represents a heat-pipe-cooled fast microreactor from
  `Technoeconomic Evaluation of Microreactor Using Detailed Design
  Information <https://inldigitallibrary.inl.gov/sites/sti/sti/Sort_129862.pdf>`_.
* LFR follows `Technoeconomic Design Optimization for Fast Reactors. Part I:
  Workflow Development and Case Study for Small LFR District Energy
  Application <https://www.osti.gov/biblio/3016125>`_.
* LPSR represents a 1117 MWe Large Passively Safe Reactor.
* Fusion estimates the cost of TETRA, a large tokamak fusion reactor based on
  UKAEA's `PROCESS <https://github.com/ukaea/PROCESS>`_.
* Stellarator is also based on UKAEA's `PROCESS
  <https://github.com/ukaea/PROCESS>`_.


.. toctree::
   :maxdepth: 1

   table/ABR1000tables
   table/Fusiontables
   table/Heatpipetables
   table/PWR12tables
