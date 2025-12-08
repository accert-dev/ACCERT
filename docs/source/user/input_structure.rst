Input Structure 
===============


This guide provides a comprehensive explanation of the structure of the ACCERT input file.
ACCERT (The Algorithm for the Capital Cost Estimation of Reactor Technologies) is used for estimating the
costs associated with nuclear reactor systems. The input file is designed to be flexible and
extensible, allowing users to define various parameters, algorithms, and cost elements.

This document outlines the hierarchical structure of the ACCERT input file, detailing each
component and providing examples for clarity.

Overall Structure
-----------------

The ACCERT input file is structured hierarchically, using blocks defined by braces `{}` and
parentheses `()`. The top-level block is the `accert` block, which contains several child
elements:

- `ref_model`
- `power`
- `var`
- `l0COA` (Level 0 Code of Accounts)

Here's a high-level view of the structure:

::

    accert {
        ref_model = <ref_model>

        power ( <id> ) {
            value = <value>
            unit = <unit>
        }

        var ( <id> ) {
            value = <value>
            unit = <unit>
        }

        l0coa: l0COA ( <id> ) {
            l1coa: l1COA ( <id> ) {
                total_cost {
                    value = <value>
                    unit = <unit>
                }
                l2coa: l2COA ( <id> ) {
                    ce ( <id> ) {
                        alg ( <id> ) {
                            var ( <id> ) {
                                value = <value>
                                unit = <unit>
                            }
                        }
                    }
                }
            }
        }
    }

Components Description
----------------------

Below is a detailed description of each component in the ACCERT input file.

ref_model
~~~~~~~~~

**Purpose**: Specifies the reference model for the ACCERT calculations.

**Syntax**::

    ref_model = <ref_model>

**Example**::

    ref_model = PWR12-BE

**Notes**:

- `<ref_model>` is a string indicating the reactor model, e.g., `PWR12-BE`, `ABR1000`, `LFR`.

power
~~~~~

**Purpose**: Defines the power parameters of the reactor.

**Syntax**::

    power ( <id> ) {
        value = <value>
        unit = <unit>
    }

**Parameters**:

- `<id>`: Identifier for the power type (e.g., `Thermal`, `Electric`).
- `<value>`: Numerical value of the power.
- `<unit>`: Unit of the power (e.g., `W`, `kW`, `MW`).

**Example**::

    power ( Thermal ) {
        value = 3000
        unit = MW
    }

    power ( Electric ) {
        value = 1000
        unit = MW
    }

var
~~~

**Purpose**: Defines variables that may affect the calculations.

**Syntax**::

    var ( <id> ) {
        value = <value>
        unit = <unit>
    }

**Parameters**:

- `<id>`: Identifier for the variable.
- `<value>`: Numerical value of the variable.
- `<unit>`: Unit associated with the variable.

**Example**::

    var ( number_of_IO_sensors ) {
        value = 100
        unit = 1
    }

    var ( heat_exchangers_mass ) {
        value = 5000
        unit = kg
    }

Code of Accounts (COA)
~~~~~~~~~~~~~~~~~~~~~~

The COA structure is hierarchical, consisting of levels from 0 to 3. Each level further refines
the cost elements.

Level 0 COA (`l0COA`)
^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Top-level categorization of costs.

**Syntax**::

    l0coa: l0COA ( <id> ) {
        // Level 1 COA entries
    }

**Parameters**:

- `<id>`: Identifier for Level 0 COA (e.g., `1`, `2`, `3`).

**Example**::

    l0coa: l0COA ( 2 ) {
        // Level 1 COA entries
    }

Level 1 COA (`l1COA`)
^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Subdivision of Level 0 COA.

**Syntax**::

    l1coa: l1COA ( <id> ) {
        total_cost {
            value = <value>
            unit = <unit>
        }
        // Level 2 COA entries
    }

**Parameters**:

- `<id>`: Identifier for Level 1 COA (e.g., `21`, `22`, `23`).

**Example**::

    l1coa: l1COA ( 21 ) {
        total_cost {
            value = 500
            unit = million
        }
        // Level 2 COA entries
    }

Level 2 COA (`l2COA`)
^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Subdivision of Level 1 COA, detailing specific cost elements.

**Syntax**::

    l2coa: l2COA ( <id> ) {
        total_cost {
            value = <value>
            unit = <unit>
        }
        ce ( <id> ) {
            alg ( <id> ) {
                var ( <id> ) {
                    value = <value>
                    unit = <unit>
                }
            }
        }
        // Level 3 COA entries
    }

**Parameters**:

- `<id>`: Identifier for Level 2 COA (e.g., `211`, `212`, `213`).

**Example**::

    l2coa: l2COA ( 211 ) {
        ce ( 211_fac ) {
            alg ( esc_1987 ) {
                var ( ref_211_fac ) {
                    value = 0.27
                    unit = million
                }
                var ( ref_211_mat ) {
                    value = 10.3
                    unit = million
                }
            }
        }
    }

Level 3 COA (`l3COA`)
^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Further subdivision for detailed cost elements.

**Syntax**::

    l3coa: l3COA ( <id> ) {
        total_cost {
            value = <value>
            unit = <unit>
        }
        ce ( <id> ) {
            // Algorithm and variables
        }
    }

**Parameters**:

- `<id>`: Identifier for Level 3 COA.

**Example**::

    l3coa: l3COA ( 221_12 ) {
        ce ( 221_12_fac ) {
            alg ( unit_weights ) {
                var ( c_221_12_cs_weight ) {
                    value = 538
                    unit = ton
                }
                var ( c_221_12_ss_weight ) {
                    value = 40340
                    unit = lbs
                }
            }
        }
    }

cost elements (`ce`)
~~~~~~~~~~~~~~~~~~~~

**Purpose**: Represents specific cost elements within a COA.

**Syntax**::

    ce ( <id> ) {
        alg ( <id> ) {
            // Variables
        }
    }

**Parameters**:

- `<id>`: Identifier for the cost element.

**Example**::

    ce ( 211_fac ) {
        alg ( esc_1987 ) {
            var ( ref_211_fac ) {
                value = 0.27
                unit = million
            }
            var ( ref_211_mat ) {
                value = 10.3
                unit = million
            }
        }
    }

algorithms (`alg`)
~~~~~~~~~~~~~~~~~~

**Purpose**: Defines the algorithm used to calculate costs.

**Syntax**::

    alg ( <id> ) {
        var ( <id> ) {
            value = <value>
            unit = <unit>
            // Nested algorithm (optional)
        }
    }

**Parameters**:

- `<id>`: Identifier for the algorithm (e.g., `esc_1987`, `MWth_scale`).

**Example**::

    alg ( esc_1987 ) {
        var ( ref_211_fac ) {
            value = 0.27
            unit = million
        }
        var ( ref_211_mat ) {
            value = 10.3
            unit = million
        }
    }

Variables within `alg`
~~~~~~~~~~~~~~~~~~~~~~

Variables within an algorithm are defined similarly to the top-level `var` but may also include nested algorithms.

**Syntax**::

    var ( <id> ) {
        value = <value>
        unit = <unit>
        alg ( <id> ) {
            // Nested variables
        }
    }

**Example**::

    var ( n_231 ) {
        alg ( tur_exp_n ) {
            var ( p_in ) {
                value = 68
                unit = bar
            }
        }
    }

total_cost
~~~~~~~~~~

**Purpose**: Specifies the total cost at a given COA level.

**Syntax**::

    total_cost {
        value = <value>
        unit = <unit>
    }

**Example**::

    total_cost {
        value = 28149700
        unit = dollar
    }

newCOA
~~~~~~

**Purpose**: Allows users to define new Codes of Accounts not included in the predefined structure.

**Syntax**::

    newCOA ( <id> ) {
        descr = "<description>"
    }

**Parameters**:

- `<id>`: Identifier for the new COA.
- `<description>`: A description of the new COA.

**Example**::

    newCOA ( useraddcoa ) {
        descr = "a user added coa"
    }

Complete Example
----------------

Here's a complete example of an ACCERT input file:

::

    accert {
        ref_model = PWR12-BE

        power ( Thermal ) {
            value = 3000
            unit = MW
        }

        power ( Electric ) {
            value = 1000
            unit = MW
        }

        var ( number_of_IO_sensors ) {
            value = 100
            unit = 1
        }

        l0coa: l0COA ( 2 ) {
            l1coa: l1COA ( 21 ) {
                total_cost {
                    value = 500
                    unit = million
                }
                l2coa: l2COA ( 211 ) {
                    ce ( 211_fac ) {
                        alg ( esc_1987 ) {
                            var ( ref_211_fac ) {
                                value = 0.27
                                unit = million
                            }
                            var ( ref_211_mat ) {
                                value = 10.3
                                unit = million
                            }
                        }
                    }
                }
            }
        }
    }

Notes and Best Practices
------------------------

- **Identifiers**: Ensure that all identifiers (`id` values) start with a letter or underscore and contain only letters, numbers, and underscores. If an identifier contains special characters or starts with a number, enclose it in quotes.

- **Units**: Always specify units where applicable to avoid ambiguity in calculations.

- **Optional Elements**: Some elements like `total_cost`, `var`, and nested `alg` blocks are optional. Include them as needed.

- **Comments**: Use `%` for comments in the ACCERT input file.

- **Extensibility**: Use `newCOA` to add new Codes of Accounts when the predefined ones do not cover all necessary aspects.

- **Validation**: It's recommended to validate the input file using NEAMS Workbench against the ACCERT schema to ensure correctness before processing.

