# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]


Address #30 #16 #22 
### Fixed

 **Table and Column Cleanup**:
   - Removed redundant tables, including the `variable links` table, which was previously used across all models.
   - Removed the following columns from the `account` table:
     - `lft`
     - `rgt`
     - `cost elements`
     - `main subaccounts`
     - `unit`
     - `cost_2011`
     - `cost_1987`
   - These changes streamline the database structure, removing unnecessary complexity.

 **Stored Procedure Usage**:
   - Removed previous usage of the `execute` method in the Python MySQL connector. The system now exclusively uses stored procedures for database interactions, ensuring consistency and improved performance.
   - Removed redundant stored procedures to streamline database operations and eliminate outdated or unnecessary functionality.
### Added 
 **Fusion Model Addition**: 
   - A new fusion model has been integrated into ACCERT to extend its functionality and coverage for fusion-related cost assessments.

 **Refactor of Algorithm Handling**:
   - All fusion-related functions have been migrated from the `algorithm` table in the database to a dedicated Python file, improving maintainability and separating model logic from the database structure.

 **Print and Result Handling**:
   - Updated the print messages for better clarity during the execution of different models.
   - Refactored the method for handling results to accommodate the specific needs of various models.

 **Account Table Acceptance**:
   - ACCERT now supports account tables that do not include split categories for cost elements, enhancing its flexibility for different input formats, this feature is needed for the Fusion model.

**Reference Table Updates**:
   
 - All reference tables have been updated to reflect the structural changes and new functionality.

**Workbench Template update**
- All templates have been updated and tested in Workbench.
   

## [0.1.0]

### Added

* ACCERT relational database
* PWR-12BE case
* ABR1000 case
* initial documentation