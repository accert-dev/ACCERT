# ACCERT v2.0.0

A major release that replaces the MySQL backend with a bundled SQLite database, adds two
new cost-analysis tools (IAT and CRT) with a GUI, introduces Mirror/AP1000/LPSR reactor
models, and expands the NEcost example set to 40 evaluation groups.

**This release contains breaking changes.** See [Breaking changes](#breaking-changes) before upgrading.

## Highlights

### SQLite database backend

ACCERT now ships `src/accertdb.sqlite` and reads it directly — no MySQL server to install,
configure, or keep running. The schema and seed data live in `accertdb_sqlite_schema_data.sql`
so the database can be rebuilt reproducibly, and database access is routed through
`sqlite_accert_connection.py` and `accert_sqlite_procedures.py`. Results are written to CSV
alongside the standard output file.

### Indigenization Adjustment Tool (IAT)

A new `iat` package estimates how costs shift when a reference design is built in a different
country, shipping localization factors for both large reactors and SMRs. Examples for AP1000
and generic LR overnight capital cost in China are under `tutorial/iat/`.

### Cost Reduction Tool (CRT) integration

`accert_bridge.py` feeds ACCERT output straight into the CRT workflow. End-to-end
ACCERT → IAT → CRT examples and a Jupyter notebook walkthrough are under `tutorial/combined/`.

### Graphical user interface

`tutorial/gui/crt_iat_gui.py` drives the IAT and CRT workflows interactively. Walkthrough
animations are included for IAT standalone and connected IAT → CRT use.

### New reactor models

- **Mirror** fusion reference model with dedicated algorithms in `MirrorFunc.py`; account,
  algorithm, variable, and default-input tables validated against TEAm.
- **AP1000** and **LPSR** direct cost models with reference tables, example inputs, and
  helper scripts that build the ACCERT tables from source data.

### Expanded NEcost examples

Forty evaluation group inputs (`EG01`–`EG40`) covering once-through, single-stage limited
recycle, multi-stage limited recycle, and continuous recycle scenarios, plus LCOE scenario,
two-island, and report-check example scripts.

### Standalone SON parser

`son_parser.py` provides a fallback parser, so command-line runs no longer require a
NEAMS Workbench installation.

### Continuous integration

A GitHub Actions workflow runs the test suite, builds the package, and validates package
metadata on every push and pull request.

## Breaking changes

| Change | What to do |
| --- | --- |
| **MySQL support removed** | Switch to the bundled SQLite database. The MySQL workflow and `test_mysql.py` are gone. |
| **`crf` package renamed to `crt`** | Update `import crf` / `from crf import ...` to use `crt`. |
| **Templates reorganized** | Templates are now namespaced under `etc/templates/accert/` and `etc/templates/necost/`. Update any paths pointing at the old flat locations. |
| **Large tokamak selector** | The tutorial now uses `ref_model = "large_tokamak"`. `fusion` still works as a backward-compatible alias, so existing inputs continue to run. |
| **Post-process column names** | OCC summaries use generic `value_escalated_*` columns tied to the configured target dollar year, replacing hard-coded year suffixes. Update downstream scripts that read those columns by name. |
| **`tutorial/` reorganized** | Examples now live in tool-specific subdirectories: `accert/`, `necost/`, `iat/`, `gui/`, `combined/`. |

## Fixed

- Corrected test import paths that failed on Windows.
- Resolved account cost scaling and rollup errors in the Mirror model.
- Refreshed gold output files to match corrected calculations.

## Removed

- Legacy MySQL workflow and `test_mysql.py`.
- The generated `inputsIndex` documentation tree and obsolete reference pages.
- Superseded template locations under `etc/templates`.

## Installation

Runtime dependencies are now declared in `pyproject.toml`, so they resolve automatically:

```bash
pip install -e .
```

## Documentation

New pages: AP1000 and Mirror examples, the IAT user guide, the combined GUI walkthrough, and
Mirror reference tables. The fusion example page is now `large-tokamak`, and the CRF user
guide is now `crt`.

**Full changelog:** https://github.com/accert-dev/ACCERT/compare/v1.0.0...v2.0.0
