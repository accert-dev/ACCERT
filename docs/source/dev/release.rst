.. _devguide_release:

ACCERT Release Notes
====================

Version 2.0.0 (09/14/2026)
----------------------------

New Features
~~~~~~~~~~~~

1. **SQLite Database Backend**:

   - ACCERT now ships a SQLite database (`accertdb.sqlite`) and reads it directly, replacing the MySQL server requirement.
   - Database interaction is handled through `sqlite_accert_connection.py` and `accert_sqlite_procedures.py`.
   - The schema and seed data are maintained in `accertdb_sqlite_schema_data.sql` for reproducible rebuilds.
   - Results are written to CSV alongside the standard output file.

2. **Indigenization Adjustment Tool (IAT)**:

   - New `iat` package estimates cost adjustments for building a reference design in a different country.
   - Ships localization factors for large reactors (LR) and small modular reactors (SMR).
   - Examples for AP1000 and generic LR overnight capital cost in China are provided under `tutorial/iat`.

3. **Cost Reduction Tool (CRT) Integration**:

   - `accert_bridge.py` feeds ACCERT output directly into the CRT workflow.
   - Combined ACCERT to IAT to CRT examples and a Jupyter notebook walkthrough are provided under `tutorial/combined`.

4. **Graphical User Interface**:

   - A GUI (`tutorial/gui/crt_iat_gui.py`) drives the IAT and CRT workflows interactively.
   - Walkthrough animations are included for IAT standalone and connected IAT to CRT use.

5. **Mirror Fusion Reference Model**:

   - A Mirror reactor model has been added with dedicated algorithms in `MirrorFunc.py`.
   - Account, algorithm, variable, and default input tables are provided, validated against TEAm.

6. **AP1000 and LPSR Direct Cost Models**:

   - New direct cost algorithms for AP1000 and LPSR, with reference tables and example inputs.
   - Helper scripts build the corresponding ACCERT tables from source data.

7. **Expanded NEcost Examples**:

   - Forty evaluation group inputs (EG01 through EG40) covering once-through, single-stage limited recycle, multi-stage limited recycle, and continuous recycle scenarios.
   - Additional LCOE scenario, two-island, and report-check example scripts.

8. **Standalone SON Parser**:

   - `son_parser.py` provides a fallback parser so command-line runs no longer require a NEAMS Workbench installation.

9. **Continuous Integration**:

   - A GitHub Actions workflow runs the test suite, builds the package, and validates package metadata on every push and pull request.

Changes
~~~~~~~

.. note::

   This is a major release and contains breaking changes. Review the items below before upgrading.

1. **MySQL Support Removed**:

   - The MySQL workflow and its tests have been removed. SQLite is now the only supported backend.

2. **CRF Renamed to CRT**:

   - The `crf` package is now `crt`. Update any `import crf` or `from crf import ...` statements to use `crt`.

3. **Template Reorganization**:

   - Workbench templates are now namespaced under `etc/templates/accert` and `etc/templates/necost`. The previous flat template locations have been removed.

4. **Large Tokamak Selector**:

   - The large tokamak tutorial now uses ``ref_model = "large_tokamak"`` rather than the generic ``fusion`` selector.
   - ``fusion`` remains supported as a backward-compatible alias, so existing inputs continue to run.

5. **Post-Process Column Naming**:

   - Overnight capital cost summaries now use generic ``value_escalated_*`` column names tied to the configured target dollar year, replacing hard-coded year suffixes.

6. **Tutorial Layout**:

   - The `tutorial` directory has been reorganized into tool-specific subdirectories: `accert`, `necost`, `iat`, `gui`, and `combined`.

7. **Declared Dependencies**:

   - Runtime dependencies are now declared in `pyproject.toml`, so `pip install` resolves them automatically.

Bug Fixes
~~~~~~~~~~~~

- **Cross-Platform Compatibility**:

  - Corrected test import paths that failed on Windows.

- **Fusion Cost Aggregation**:

  - Resolved account cost scaling and rollup errors in the Mirror model.

- **Integration Baselines**:

  - Refreshed gold output files to match corrected calculations.

Removed
~~~~~~~

- Legacy MySQL workflow and `test_mysql.py`.
- The generated `inputsIndex` documentation tree and obsolete reference pages.
- Superseded template locations under `etc/templates`.

Version 1.0.0 (09/30/2024)
----------------------------

New Features
~~~~~~~~~~~~

1. **GNCOA vs. EEDB COA Output Ordering**:

   - ACCERT now supports choosing between two output formats:

     - **GNCOA (Generalize Nuclear Code of Accounts )**
     - **EEDB COA (Energy Economic Database Cost Code of Acounts)**

   - This provides flexibility depending on the user's needs and the project’s cost accounting framework.

2. **Fusion Model Integration**:

   - Added support for a new **fusion reactor model**, enabling users to estimate and analyze costs for fusion-based nuclear reactors.
   - All fusion algorithms have been moved to a separate Python file (`FusionFunc`) to improve organization and scalability, as fusion models do not follow the same cost element division as other reactor types.

3. **Beyond 20**:

   - Added support for Indirect Cost in cost estimation.

4. **Improved Scalability and Maintainability**:

   - Removed redundant tables and columns from the database, simplifying its structure.
   - Redundant database procedures have been eliminated to streamline database operations.
   - Fusion-related algorithms are now separate from the main database, housed in Python files for easier updates.

5. **Refactored Algorithm Storage**:

   - The fusion algorithms previously stored in the `accert_algorithm.csv` file have been relocated to improve code clarity and efficiency.
   - This separation ensures easier updates for the fusion algorithms without needing to modify the database directly.

6. **Updated Print Messages and Result Handling**:

   - Print messages have been improved to provide clearer feedback during execution across different models.
   - Refactored how results are handled to accommodate different model-specific requirements.

7. **Enhanced Documentation**:

   - Updated the documentation to reflect the new features and provide detailed instructions on how to use them.
   - Added examples and explanations to help users understand the changes and how they can leverage the new functionality.

Bug Fixes
~~~~~~~~~~~~


- **Cross-Platform Compatibility**: 

  - Addressed issues with unit tests that passed on macOS but failed on Linux, improving cross-platform consistency.

Performance Enhancements
~~~~~~~~~~~~~~~~~~~~~~~~

- **Database Procedure Usage**:

  - Consolidated database interactions through named database procedures, leading to more consistent operations.

Version 0.1.0 (04/05/2023)
--------------------------

`ACCERT relational database <https://github.com/accert-dev/ACCERT/blob/main/src/accertdb.sqlite>`_

`PWR-12BE case <https://github.com/accert-dev/ACCERT/blob/main/tutorial/PWR12-BE.son>`_

`ABR1000 case <https://github.com/accert-dev/ACCERT/blob/main/tutorial/ABR1000.son>`_

`Initial documentation <https://github.com/accert-dev/ACCERT/blob/main/README.md>`_

`Installation automation <https://github.com/accert-dev/ACCERT/blob/main/src/setup_accert.sh>`_

New Features
~~~~~~~~~~~~

- **Customizable Parameters**: Enables adjustment of variables and parameters to align with specific reactor designs or project requirements.
- **Relational Databases**: Provides access to comprehensive cost data from reference reactor models, which can be tailored to new designs.
- **Hierarchical Structure**: COAs are organized across multiple levels (typically between 0-5), decomposing complex systems into manageable components and subtasks.
- **Installation automating**: Provides a script to automate the installation process.

