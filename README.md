# ACCERT

ACCERT (the Algorithm for the Capital Cost Estimation of Reactor
Technologies) estimates reactor-facility costs item by item. It includes
capital-cost algorithms, a SQLite database, International Adjustment Tool
(IAT) and Cost Reduction Tool (CRT) workflows, and an interactive GUI for
reviewing results and visualizations.

ACCERT can integrate with the [NEAMS
Workbench](https://www.ornl.gov/project/neams-workbench) and can use
Workbench SON input files. The repository includes the SQLite database at
`src/accertdb.sqlite`.

## Requirements

The project metadata supports Python 3.10 and newer. The application and test
suite have been tested with Python 3.12. If you encounter compatibility
issues, check your Python version.

Install the Python dependencies from the repository root:

```bash
python -m pip install -r requirements.txt
```

Conda is not required by the project.

## Start the GUI on macOS

The macOS launcher is the supported, tested GUI startup path:

1. Install Python and the project dependencies.
2. Double-click [Launch ACCERT GUI.command](tutorial/gui/Launch%20ACCERT%20GUI.command).
3. The launcher starts the local GUI server and opens the GUI in the default browser.

To stop a launcher-managed session, double-click
[Stop ACCERT GUI.command](tutorial/gui/Stop%20ACCERT%20GUI.command).

The macOS launcher has been tested successfully. Windows and Linux launchers
have not been confirmed as tested. The underlying Python modules may be useful
on other platforms, but this README does not claim that the GUI launcher works
there.

## Basic GUI use

Choose an IAT-only, CRT-only, or connected IAT-then-CRT workflow. Select the
source and country, review the visible assumptions, expand advanced sections
when needed, and select **Run analysis**. Results include summary cards,
interactive charts, tables, and downloadable output files.

## Running tests

These commands use the pytest configuration in `pyproject.toml`:

```bash
# Quick default suite
python -m pytest

# GUI-related tests
python -m pytest -m gui

# Complete collected suite, including GUI and slow regression tests
python -m pytest -o addopts=""
```

## Documentation

More detailed ACCERT documentation is available at
[Read the Docs](https://accert.readthedocs.io/en/latest/index.html).
