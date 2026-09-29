# CRT parameter mapping

This note records the trace for the cryptic factory-allocation inputs exposed by
the integrated GUI. The source workbooks in the read-only EMANES6 reference
folder were inspected but were not modified.

| Parameter | Current value | Source | Meaning | Unit | Used in equation/function | Allowed range/alternatives |
|---|---:|---|---|---|---|---|
| `f_22` | 250,000,000 (GUI default) | `tutorial/gui/crt_iat_gui.py` default; `_crt_config` | Factory-equipment allocation added to CRT account 22 before learning | USD, as represented by the CRT baseline cost columns | `src/crt/model/direct_cost.py:add_factory_cost` and `add_bulk_ordering` | Nonnegative; zero disables this allocation. No independent upper bound is defined by the current model |
| `f_2321` | 150,000,000 (GUI default) | `tutorial/gui/crt_iat_gui.py` default; `_crt_config` | Factory-equipment allocation added to CRT account 232.1 before learning | USD, as represented by the CRT baseline cost columns | `src/crt/model/direct_cost.py:add_factory_cost` and `add_bulk_ordering` | Nonnegative; zero disables this allocation. No independent upper bound is defined by the current model |

For each firm-order case, the implementation adds `f_22 / num_orders` to
account 22 and `f_2321 / num_orders` to account 232.1. The same allocations are
then preserved as the non-learning portion in the bulk-ordering equation. They
therefore affect CRT direct cost for the reactor types where the factory-share
step is enabled (`HTGR` and `SFR`); the current AP1000 implementation does not
apply that factory-share addition.

The available `US_AP1000.xlsx` reference workbook contains the related account
labels, including “20s - Factory equipment costs”, and the account-22 and
account-232.1 relationships, but no cells named `F22`, `F2321`, `f_22`, or
`f_2321`, nor a traceable cell containing the GUI defaults. Those two constants
must therefore remain explicit CRT inputs until the authoritative source sheet
or Excel cell is identified.

The workbook’s relationship sheet also records the following adjacent model
parameters: account 22/232.1 commercial-BOP reductions, a $/acre land input,
construction-duration factors, and ITC multipliers. Those are separate from
`f_22` and `f_2321` and should not be conflated with them.
