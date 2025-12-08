.. _devguide_release:

ACCERT Release Notes
====================

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
   - Redundant stored procedures have been eliminated to streamline database operations.
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

- **Stored Procedure Usage**:

  - Replaced instances of the `execute` method with stored procedures for database interaction, leading to better performance and more consistent operations.

Version 0.1.0 (04/05/2023)
--------------------------

`ACCERT relational database <https://github.com/accert-dev/ACCERT/blob/main/src/accertdb.sql>`_

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


