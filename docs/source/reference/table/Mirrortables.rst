Mirror Tables
=============

The Mirror model is a magnetic-mirror fusion cost model ported from upstream
ACCERT PR #50. Its reference data currently contains account, variable, and
algorithm tables. Unlike PWR12-BE, AP1000, LPSR, and ABR1000, the Mirror model
does not use a separate cost-element table.

The default input table is generated from ``MirrorFunc.generate_inputs``. Boolean
defaults are stored as ``0`` or ``1`` so they can be loaded into SQLite with the
other ACCERT variable values.

Mirror Account Table
--------------------

.. csv-table:: Mirror Account Table
   :file: ../../../../tutorial/accert/ref_tables/mirror_account.csv
   :header-rows: 1

Mirror Algorithm Table
----------------------

.. csv-table:: Mirror Algorithm Table
   :file: ../../../../tutorial/accert/ref_tables/mirror_algorithm.csv
   :header-rows: 1

Mirror Variable Table
---------------------

.. csv-table:: Mirror Variable Table
   :file: ../../../../tutorial/accert/ref_tables/mirror_variable.csv
   :header-rows: 1

Mirror Default Input Table
--------------------------

.. csv-table:: Mirror Default Input Table
   :file: ../../../../tutorial/accert/ref_tables/mirror_default_inputs.csv
   :header-rows: 1
