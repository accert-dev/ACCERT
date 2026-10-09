# Getting Started

The main function of ACCERT (The Algorithm for the Capital Cost Estimation of Reactor Technologies) is to provide an item-by-item estimate of the cost of a facility, at present a nuclear reactor complex, primarily nuclear power stations. The core of ACCERT is the large number of algorithms that have been developed and will continue to be developed. ACCERT is also a general methodology for identifying and organizing the individual items that are estimated using the ACCERT algorithms. ACCERT also summarize status and results; to save results and pull information from previous analyses; and to provide an interactive dynamic graphical user interface for a wide range of functions and visualizations. 


The software comprises three major components:
*	Relational Database
    *	Creation, editing, and linking of different element types
    *	Report generation (queries)
    *	Search
*	Equation solvers (extraction of information from elements and evaluation/updating of fields in the database)
    *	Algorithms
    *	Escalation
    *	Cost aggregation
*	Interactive Graphical User Interface
    *	Dynamic windows


ACCERT is designed for integration with the [NEAMS
Workbench](https://www.ornl.gov/project/neams-workbench) and relies on input
files using Workbench's SON format. ACCERT uses the bundled SQLite database at
`src/accertdb.sqlite`. Instructions for installing ACCERT both
with and without Workbench are provided in this README.

## Running the ACCERT GUI Locally

On macOS, double-click [Launch ACCERT GUI.command](tutorial/gui/Launch%20ACCERT%20GUI.command).
It uses the configured Anaconda Python 3.12 environment when available, starts the
local server, and opens the GUI in the default browser. The normal address is
`http://127.0.0.1:8765/`. If that port is occupied by an unrelated process,
the launcher selects the next available local port and opens that address
automatically; it never terminates unrelated processes.

If an ACCERT GUI is already running, the launcher offers three choices:

- reuse the existing session;
- stop the launcher-managed session and restart it; or
- start another session on a free port.

To stop the managed session, double-click [Stop ACCERT GUI.command](tutorial/gui/Stop%20ACCERT%20GUI.command).
This only stops the ACCERT process recorded by the launcher. It does not stop
an arbitrary process that happens to use port 8765. The same actions are
available from a terminal if needed:

```text
/opt/anaconda3/envs/py312/bin/python tutorial/gui/launch_gui.py
/opt/anaconda3/envs/py312/bin/python tutorial/gui/stop_gui.py
```

On Windows, run the equivalent commands from the repository root with
Python 3.12:

```text
py -3.12 tutorial/gui/launch_gui.py
py -3.12 tutorial/gui/stop_gui.py
```

On Linux, use the installed Python 3.12 executable:

```text
python3.12 tutorial/gui/launch_gui.py
python3.12 tutorial/gui/stop_gui.py
```

This is a local browser application. It listens only on `127.0.0.1`; it is
not a remotely deployed web service.

After changing GUI code, stop the current session, launch it again, and reload
the browser page. Confirm that the page opens and that `/health` reports the
local server as healthy. The launcher does not depend on closing a browser tab
to stop the server; use the Stop shortcut when finished.

## Troubleshooting

- **Port already in use:** use the double-click launcher. It automatically
  chooses a free port when 8765 is not available. An explicit `--port` is only
  needed for a fixed-port workflow.
- **Server already running:** choose reuse to open it, restart to stop and
  relaunch a launcher-managed session, or new to use another port.
- **Browser does not open:** open the address printed by the launcher, usually
  `http://127.0.0.1:8765/`.
- **Stale server after a code update:** double-click Stop ACCERT GUI.command,
  wait for it to finish, then double-click Launch ACCERT GUI.command.
- **Startup fails:** run `/opt/anaconda3/envs/py312/bin/python tutorial/gui/launch_gui.py` from the
  repository root and keep the terminal output. It includes the selected URL,
  output directory, and Python error details.
- **Confirm shutdown:** run `/opt/anaconda3/envs/py312/bin/python tutorial/gui/stop_gui.py` and verify that
  `curl http://127.0.0.1:8765/health` fails, or check the actual port printed
  by the launcher. The stop script never force-kills a process after its
  five-second graceful-shutdown window.

## Documentation

Documentation for ACCERT can be found
[__here__](https://accert.readthedocs.io/en/latest/index.html).
