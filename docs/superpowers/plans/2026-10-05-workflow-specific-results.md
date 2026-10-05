# ACCERT Workflow-Specific Results Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make IAT-only, IAT-then-CRT, and CRT-only results show only workflow-relevant information, with correct country-specific assumptions and consistent IAT comparison charts.

**Architecture:** Preserve the existing Python calculation and response contracts. Add a small display-policy/data-normalization layer in the existing GUI HTML and `run_workflow()` response construction, then make chart renderers consume normalized country/scenario rows. Keep CRT cards unchanged except for their workflow placement.

**Tech Stack:** Python 3, embedded HTML/JavaScript, pandas, pytest, local HTTP GUI server, CUA browser verification.

**Spec:** `docs/superpowers/specs/2026-10-05-workflow-specific-results-design.md`

## Global Constraints

- Do not rewrite IAT or CRT calculation models.
- Preserve public payload keys, CSV formats, interactive charts, result tables, downloads, and dashboard export contracts.
- Use the canonical `DEFAULT_IAT_FACTORS`; do not create a second hardcoded U.S. factor set.
- Do not stage or modify `ACCERT_DEVELOPMENT_HISTORY.md` or unrelated generated files.
- Do not push.
- Use the user's Git identity and short atomic commits.

## Review Focus

- CRT-only must not render generic IAT/adjusted-OCC cards: test the rendered HTML policy and the response shape.
- Combined IAT+CRT must use the actual U.S. source OCC and adjusted country OCC: test the response values and labels without recalculating OCC.
- Multi-country factor edits must remain isolated: test switching United States/China/Poland and preserving each override.
- Sparse and single-category chart rows must keep bars centered on labels: test one, two, and three country inputs.
- A U.S. reference case with no foreign component must produce an explanatory empty comparison state: test the renderer's semantic guard.

### Task 1: Fix workflow-specific result rendering

**Files:**
- Modify: `tutorial/gui/crt_iat_gui.py` — client `render()`, IAT summary helpers, CRT baseline/result placement, combined OCC labels.
- Test: `test/test_gui_workflow.py` — workflow-specific rendering and response assertions.

**Interfaces:**
- Consumes: existing response fields `workflow`, `iat`, `crt`, `base_case`, `country_results`, and `files`.
- Produces: workflow-specific HTML policy with no changed API keys.

- [ ] **Step 1: Write failing tests**

  Add tests that assert:

  - CRT-only rendering does not append `resultSummaryCards(data)` or an IAT comparison section.
  - IAT-only rendering does not append a synthetic generic Base Case alongside selected countries.
  - IAT+CRT contains `Original OCC (United States)` and `Adjusted OCC (${country})` before `CRT Results`.
  - CRT card markup remains present for CRT-only and combined responses.

- [ ] **Step 2: Run the focused tests and verify they fail**

  Run:

  ```bash
  python -m pytest test/test_gui_workflow.py -q -k 'workflow_specific or combined_original_occ or crt_only'
  ```

  Expected: FAIL on the current shared rendering behavior.

- [ ] **Step 3: Implement workflow display policy**

  In `tutorial/gui/crt_iat_gui.py`, separate the `render(data)` branches by workflow. Use the existing `data.iat` input totals for the combined original OCC card and the selected-country summary for adjusted OCC. Only call `baseCaseBlock()` where the workflow needs source identification; do not use CSS hiding as the policy mechanism.

- [ ] **Step 4: Run focused and existing GUI tests**

  ```bash
  python -m pytest test/test_gui_workflow.py -q -k 'workflow_specific or combined_original_occ or crt_only'
  python -m pytest test/test_gui_workflow.py -q -x
  ```

  Expected: all selected tests pass.

- [ ] **Step 5: Commit**

  ```bash
  git add tutorial/gui/crt_iat_gui.py test/test_gui_workflow.py
  git commit -m "Fix workflow results"
  ```

### Task 2: Add country-specific IAT assumption context and scenario identity

**Files:**
- Modify: `tutorial/gui/crt_iat_gui.py` — IAT advanced-assumption controls, override save/load flow, IAT-only response normalization.
- Test: `test/test_gui_workflow.py` — country context and data-flow tests.

**Interfaces:**
- Consumes: `DEFAULT_IAT_FACTORS`, existing `iatFactorOverrides`, `selectedCountries()`, `_iat_config()`, and `run_workflow()`.
- Produces: `iatFactorOverrides[country]` isolation and comparison rows whose country/scenario fields represent real cases only.

- [ ] **Step 1: Write failing tests**

  Add tests that assert:

  - the initial IAT-only selector/checkbox state includes United States;
  - an explicit `iatAssumptionCountry` control is populated from selected countries;
  - save/load functions use that control rather than always using the first selected country;
  - IAT-only response comparison rows for United States + China + Poland contain no synthetic `Base case` country;
  - combined workflow preserves the U.S. input total as the original OCC and sends the adjusted IAT CSV to CRT.

- [ ] **Step 2: Run focused tests and verify failure**

  ```bash
  python -m pytest test/test_gui_workflow.py -q -k 'country_assumptions or scenario_identity or iat_data_flow'
  ```

  Expected: FAIL because the editor has no country context and `run_workflow()` adds synthetic Base case rows.

- [ ] **Step 3: Implement isolated country context**

  Add a select control whose options are derived from the currently selected IAT-only countries. Update `activeIatCountry()`, `saveIatFactorOverrides()`, `loadIatFactorDefaults()`, and country-selection listeners so switching the control saves the current values and loads only the chosen country’s override/defaults. Keep connected IAT+CRT bound to its single country selection.

- [ ] **Step 4: Normalize IAT-only scenario rows**

  Remove synthetic display-only Base case rows from ordinary country comparison. Preserve real OCC scenario rows when the input mode genuinely has multiple independent scenarios, and use the country name as the display identity when there is no independent scenario dimension.

- [ ] **Step 5: Run focused and API tests**

  ```bash
  python -m pytest test/test_gui_workflow.py -q -k 'country_assumptions or scenario_identity or iat_data_flow'
  python -m pytest test/test_gui_workflow.py test/test_crt_api.py -q -x
  ```

  Expected: all selected tests pass and CRT/IAT data-flow assertions show unchanged calculation inputs/outputs.

- [ ] **Step 6: Commit**

  ```bash
  git add tutorial/gui/crt_iat_gui.py test/test_gui_workflow.py
  git commit -m "Fix IAT country comparison"
  ```

### Task 3: Improve IAT comparison charts

**Files:**
- Modify: `tutorial/gui/crt_iat_gui.py` — `occComparisonChart()`, `localForeignChart()`, shared color/hatch helpers and semantic empty state.
- Test: `test/test_gui_workflow.py` — chart markup and category-position tests.

**Interfaces:**
- Consumes: normalized rows from Task 2 with `country`, optional `scenario`, `label`, `adjusted_occ_per_kw`, `local_per_kw`, and `foreign_per_kw`.
- Produces: SVG charts with shared country color mapping, centered category bands, and Local/Foreign texture encoding.

- [ ] **Step 1: Write failing tests**

  Add tests that assert:

  - the OCC chart derives bar and label positions from the same category center;
  - color is selected by country rather than scenario index;
  - the Local/Foreign chart defines hatch patterns and uses the country color for both solid and hatched segments;
  - the U.S.-reference empty state is returned when all foreign components are zero or trivial;
  - no country-specific x-offset constants are present.

- [ ] **Step 2: Run focused tests and verify failure**

  ```bash
  python -m pytest test/test_gui_workflow.py -q -k 'comparison_chart or local_foreign or chart_colors'
  ```

  Expected: FAIL on scenario-based colors, fixed component colors, or the current category calculations.

- [ ] **Step 3: Implement shared chart helpers**

  Add small JavaScript helpers for ordered categories, stable country colors, categorical band centers, and SVG hatch definitions. Keep the current application palette and tooltip behavior.

- [ ] **Step 4: Update OCC comparison chart**

  Render each category using the same computed center for its bars and country label. Support one, two, three, and more countries without hardcoded offsets; preserve responsive viewBox behavior.

- [ ] **Step 5: Update Local/Foreign chart**

  Use solid country-color Local segments and diagonal-hatched segments using the same country color for Foreign. Add a concise legend for `Color = country` and `Fill = Local / Foreign`. Return the U.S. reference message when no meaningful foreign component exists.

- [ ] **Step 6: Run tests and visual verification**

  ```bash
  python -m pytest test/test_gui_workflow.py test/test_crt_api.py -q -x
  python -m py_compile tutorial/gui/crt_iat_gui.py src/crt/visualization.py
  git diff --check
  ```

  Start the local GUI server, inspect IAT-only at wide and narrow browser widths, inspect combined and CRT-only result hierarchy, and inspect affected generated dashboard PNGs. Confirm browser console logs have no errors.

- [ ] **Step 7: Commit**

  ```bash
  git add tutorial/gui/crt_iat_gui.py test/test_gui_workflow.py
  git commit -m "Improve IAT comparison charts"
  ```

### Final checkpoint

- [ ] Verify all three commits contain only intended files and no history/generated files.
- [ ] Run the complete relevant test command and record the exact pass count.
- [ ] Review the final diff against the spec acceptance criteria.
- [ ] Do not push.
