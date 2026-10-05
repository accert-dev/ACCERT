# ACCERT Workflow-Specific Results and IAT Country Comparison

## Overview

Refine the ACCERT GUI so that IAT-only, IAT-then-CRT, and CRT-only runs present only the results that belong to that workflow. The change is presentation and state-management focused: existing IAT/CRT calculation models, public payload keys, CSV formats, and dashboard export contracts remain unchanged unless investigation proves that a wrong input is crossing a workflow boundary.

## Current findings

- `render()` adds generic summary cards whenever `data.iat` is absent, so CRT-only results receive cards intended for a broader result template.
- `baseCaseBlock()` is reused across workflows, which makes CRT-only and IAT-only show baseline content that is not always a distinct user-facing scenario.
- `run_workflow()` adds synthetic `Base case` rows to IAT comparison data. Those rows are then combined with country rows and create duplicate or ambiguous categories.
- The IAT factor editor uses the first selected country as its active context. Multi-country overrides are stored by country, but there is no control to select which country is being edited.
- `occComparisonChart()` assigns colors by scenario rather than country and computes category positions from a global scenario list. `localForeignChart()` uses fixed Local/Foreign colors, so the country identity is lost across related charts.
- Combined IAT data already contains the original input total and adjusted total. The first summary card is therefore a labeling/data-selection problem, not a reason to recalculate OCC.

## Architecture decisions

### 1. Workflow-specific rendering branches

Introduce small display-policy helpers in the existing client-side renderer rather than hiding generic cards with CSS:

- `iat_only`: render country results and country-comparison charts; do not render CRT sections or a separate synthetic baseline.
- `iat_crt`: render an IAT transformation section first, using the actual input OCC as `Original OCC (United States)` and the selected country output as `Adjusted OCC (Country)`, then render the existing CRT result cards and CRT details.
- `crt_only`: render selected CRT baseline/source identification followed directly by CRT results; do not call the IAT summary-card or country-comparison rendering paths.

The CRT card layout and tooltips remain unchanged except for workflow placement.

### 2. Single scenario identity source

Keep the existing API structures but normalize IAT display rows at the boundary between response data and charts. Each display row will carry:

- `country`: the user-visible country name;
- `scenario`: a real scenario label only when the workflow has an independent OCC scenario dimension;
- `label`: the final display label;
- adjusted OCC and Local/Foreign component values.

For ordinary country comparison, one selected country produces one country case. Synthetic `Base case` rows are not added when the U.S. country case already represents the reference. If an OCC-only run has multiple independent scenario values, those scenario labels remain, but they are not duplicated as separate country cases.

### 3. Country-specific IAT assumptions

Add an explicit country selector beside Advanced IAT Assumptions. In IAT-only mode it is populated from the currently selected countries and defaults to the first selected country, with United States selected initially. Changing it calls the existing save/load override functions so each country keeps an independent editable factor set. Connected IAT→CRT mode continues to use the single country selector used by that workflow.

The canonical `DEFAULT_IAT_FACTORS` object remains the only source of defaults; no second hardcoded U.S. factor set is introduced.

### 4. Comparison chart encoding

Use a stable country color function/map shared by the IAT comparison charts. Category positions are derived from the ordered country/scenario categories and their actual band centers, so the bar center and label center use the same coordinate.

For Local/Foreign charts:

- country color identifies the country;
- solid fill identifies Local;
- the same country color with a diagonal hatch identifies Foreign;
- one concise legend explains color and texture.

If the selected data has no meaningful foreign component and represents the U.S. reference case, render a short reference-case message instead of a chart of trivial duplicate values.

## Data-flow safeguards

Before changing formulas, verify with focused tests that:

1. IAT-only country overrides produce the expected country-specific configuration values.
2. Combined workflow uses the U.S. source OCC as IAT input and passes the adjusted IAT output CSV into CRT.
3. CRT-only does not construct an IAT result or country comparison object.
4. Removing synthetic display rows does not remove real scenario calculations or alter CSV outputs.

If any check fails, report the expected input, actual input, calculation path, result, and root cause before changing model code.

## Acceptance criteria

- IAT-only defaults to United States and never displays a duplicate Base case for the same U.S. reference result.
- IAT-only with United States, China, and Poland shows exactly those country names in cards/tables/charts and keeps each country’s factor edits isolated.
- IAT+CRT clearly shows `Original OCC (United States)` followed by `Adjusted OCC (Country)` and CRT Results.
- CRT-only shows the selected CRT baseline and CRT Results, with no IAT cards or country-comparison charts.
- OCC comparison bars are centered on their country labels at one, two, three, and responsive-width layouts.
- Country colors are stable across IAT comparison charts; Local/Foreign uses solid/hatch encoding.
- Existing CRT card terminology, ITC Gross/Net behavior, interactive charts, result tables, downloads, API payload keys, CSV formats, and numerical calculations are preserved.
- Relevant automated tests pass, the GUI is checked at wide and narrow browser widths, and affected dashboard images are inspected.

## Commit boundaries

1. `Fix workflow results` — rendering policies, combined OCC labels, and workflow tests.
2. `Fix IAT country comparison` — country assumption context/overrides and scenario identity tests.
3. `Improve IAT comparison charts` — categorical positioning, stable colors, hatch fills, and visual tests.

No push is planned. `ACCERT_DEVELOPMENT_HISTORY.md` and unrelated generated files are excluded.
