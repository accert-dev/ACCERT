Installation Guide
==================

This guide describes how to install ACCERT on Windows, macOS, and Linux.
ACCERT uses the bundled SQLite database at ``src/accertdb.sqlite``.

Prerequisites
-------------

- **Git**: Install from `Git Downloads <https://git-scm.com/downloads>`_ if needed.
- **Python**: Python 3.9 or newer is recommended.
- **NEAMS Workbench**: Optional for command-line Python runs; required for the Workbench interface and full SON schema validation tools.

Clone ACCERT
------------

1. Create a directory for ACCERT.
2. Open Git Bash, Terminal, or another shell.
3. Clone the repository:

   .. code-block:: shell

      $ cd /path/to/CODE
      $ git clone https://github.com/accert-dev/ACCERT.git
      $ cd ACCERT

Optional: Install NEAMS Workbench
---------------------------------

Download NEAMS Workbench from
`NEAMS Workbench Downloads <https://code.ornl.gov/neams-workbench/downloads>`_.

- Windows: download and run the ``.exe`` installer.
- macOS: download and open the ``.dmg`` installer.
- Linux: download and extract the ``.tar.gz`` package, then follow the bundled instructions.

Launch Workbench once before running the ACCERT setup script if you plan to use
the Workbench interface or Workbench's SON validation executable.

Configure Workbench Path
------------------------

Edit ``src/workbench.sh`` and set ``workbench_path`` to your Workbench
installation. Examples:

.. code-block:: shell

   # Windows, from Git Bash
   workbench_path="C:/Path/To/Workbench-5.3.1"

   # macOS
   workbench_path="/Applications/Workbench-5.3.1.app/Contents"

   # Linux
   workbench_path="/path/to/Workbench-5.3.1"

Run Setup
---------

From the ``src`` directory, run:

.. code-block:: shell

   $ cd src
   $ chmod +x setup_accert.sh
   $ ./setup_accert.sh

The setup script installs Python requirements, refreshes
``src/accertdb.sqlite`` from ``src/accertdb_sqlite_schema_data.sql``, copies the
Workbench integration file when Workbench is available, and creates the local
``bin/sonvalidxml`` link when the Workbench executable can be found.

Running Without Workbench
-------------------------

ACCERT command-line runs can parse ACCERT SON input files without Workbench. If
``bin/sonvalidxml`` is available, ACCERT uses it for WASP/HIVE schema validation.
If it is not available, ACCERT falls back to its built-in Python parser for the
SON subset used by ACCERT tutorial inputs.

To use a specific Workbench or WASP-built ``sonvalidxml`` executable, set
``ACCERT_SONVALIDXML``:

.. code-block:: shell

   $ ACCERT_SONVALIDXML=/path/to/sonvalidxml python src/Main.py -i tutorial/accert/LargeTokamak.son

SQLite Database
---------------

The default database file is:

.. code-block:: shell

   src/accertdb.sqlite

To rebuild it manually, run:

.. code-block:: shell

   $ python src/database_install.py

To use a different database file for a run, set ``ACCERT_SQLITE_DB``:

.. code-block:: shell

   $ ACCERT_SQLITE_DB=/path/to/accertdb.sqlite python src/Main.py tutorial/accert/ABR1000.son

Testing the Installation
------------------------

Run the test suite from the repository root:

.. code-block:: shell

   $ pytest test

Troubleshooting
---------------

- If setup cannot find Workbench, check the ``workbench_path`` value in
  ``src/workbench.sh``. Command-line ACCERT runs can still use the built-in SON
  parser.
- If ``sonvalidxml`` is missing, verify that Workbench has a ``bin`` directory
  and rerun ``src/setup_accert.sh``. You can also set ``ACCERT_SONVALIDXML`` to
  a WASP-built ``sonvalidxml`` executable.
- If the SQLite database is missing or stale, rerun
  ``python src/database_install.py``.
