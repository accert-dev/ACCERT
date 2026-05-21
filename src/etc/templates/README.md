# Workbench Autocomplete Templates

These templates are used by the SON schemas in `src/etc` for Workbench
autocomplete. Keep template filenames aligned with each schema `InputTmpl`
value.

## ACCERT

Top-level ACCERT templates live in this directory. The root `accert.tmpl`
starts from the AP1000 pattern with thermal and electric power, OCC
post-processing, one optional variable, and one editable account block.

## NEcost

NEcost templates are grouped by input section:

- `fuel_cycles/` for EG case weighting by reactor island.
- `reactors/` for reactor performance, cost scaling, and reload quantities.
- `capital_costs/`, `om_costs/`, and `fuels/` for reusable cost and fuel data.

The root `necost.tmpl` is a complete one-island EG-style starter case. For EG13
or EG23, duplicate the `reactor(...)` entries inside a cycle and set
`energy_fraction`, `mass_fraction`, or `fleet_capacity` for each island.
