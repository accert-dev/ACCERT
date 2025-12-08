Introduction
============

Welcome to **ACCERT** (Algorithm for the Capital Cost Estimation of Reactor Technologies), an advanced tool designed to facilitate precise estimation of capital costs for nuclear reactor technologies. ACCERT provides a structured and systematic approach to cost estimation, empowering engineers, researchers, and professionals to make informed decisions in their projects.

For detailed installation instructions, please refer to the :doc:`Installation Guide <install>`.

What is ACCERT?
---------------

ACCERT is a comprehensive software platform that:

- **Generates Detailed Cost Estimates**: Provides itemized cost breakdowns for nuclear facilities with a focus on accuracy and specificity.
- **Employs Advanced Algorithms**: Utilizes a wide array of algorithms to calculate costs based on various parameters, scaling laws, and industry standards.
- **Systematically Organizes Costs**: Implements a hierarchical system to identify and categorize individual cost items effectively.
- **Offers an Interactive Interface**: Seamlessly integrates with the NEAMS Workbench, providing a dynamic graphical user interface for data input, simulation execution, and result visualization.

Key Features
------------

- **Customizable Parameters**: Enables adjustment of variables and parameters to align with specific reactor designs or project requirements.
- **Relational Databases**: Provides access to comprehensive cost data from reference reactor models, which can be tailored to new designs.
- **Advanced Visualization**: Presents results through detailed tables, charts, and graphs to enhance analysis and presentation capabilities.

Understanding the Code of Accounts (COA)
----------------------------------------

Central to ACCERT is the **Code of Accounts (COA)** system, which offers a standardized methodology for categorizing and tracking costs.

- **Hierarchical Structure**: COAs are organized across multiple levels (typically between 0-5), decomposing complex systems into manageable components and subtasks.
- **Unique Identifiers**: Assigns a distinct COA to each component and cost element, facilitating precise tracking and analysis.
- **Cost Categories**: Each COA encompasses three primary cost categories:

  - **Factory Equipment Costs**: Expenses related to equipment and machinery procurement.
  - **Labor Costs**: Costs associated with manpower required for construction, installation, and commissioning processes.
  - **Material Costs**: Expenditures for materials used, quantified in specific units (e.g., tons, cubic yards).

   .. admonition:: Important
      :class: important
      ACCERT now allows cost estimates without cost categories, providing flexibility for users to customize their cost breakdowns.

Using ACCERT with NEAMS Workbench
---------------------------------

ACCERT integrates effectively with the **NEAMS Workbench**, providing a user-friendly environment for cost estimation projects.

- **Intuitive Navigation**: The Workbench interface facilitates effortless navigation through different components and cost data.
- **Interactive Controls**: Allows real-time modification of inputs and parameters, with immediate impact on overall cost estimations.
- **Comprehensive Visualization Tools**: Enables generation of graphs and charts to visualize cost distributions and identify key cost drivers.

Why Use ACCERT?
---------------

- **Precision**: Delivers detailed and accurate cost estimates by considering a multitude of variables and components.
- **Efficiency**: Enhances productivity by automating complex calculations and organizing data systematically.
- **Versatility**: Adaptable to various reactor designs and technologies, making it suitable for a wide range of nuclear projects.
- **Professional Support**: Supported by extensive documentation and a community of experienced users and developers.

New Features
------------

1. **GNCOA vs. EEDB COA Output Ordering**:

   - ACCERT now offers the option to output results ordered by either **GNCOA** (Generalized Nuclear Code of Accounts) or **EEDB COA** (Energy Economic Database Code of Accounts).
   - This flexibility allows users to select the accounting framework that best aligns with their project's requirements.

2. **Fusion Model Integration**:

   - ACCERT has expanded its capabilities to include a new **fusion reactor model**, enabling cost estimation and analysis for fusion-based nuclear reactors.
   - Fusion algorithms are organized within a dedicated Python module (`FusionFunc.py`), enhancing maintainability and scalability, given the distinct cost element structures of fusion reactors.

3. **Refactoring and Database Optimization**:

   - Redundant tables and columns have been eliminated to streamline the database structure.
   - Fusion algorithms have been segregated from the main `accert_algorithm.csv` file, reducing clutter and improving code organization.
   - Unnecessary stored procedures have been removed, simplifying database operations and improving performance.
