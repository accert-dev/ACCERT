# ACCERT GUI development checklist

Use this checklist for changes to the local IAT/CRT GUI.

## Before implementation

- Review the affected GUI source and existing GUI tests.
- Review affected IAT + CRT and CRT-only workflow/integration tests.
- Check whether existing workflow GIFs, screenshots, or documentation are outdated.
- Keep calculation models, APIs, CSV formats, and research data unchanged unless the task explicitly requires otherwise.

## Verification before commit

- Run focused GUI tests first, then the relevant broader test suite.
- Run Python compilation checks and `git diff --check`.
- Perform a real browser or screenshot-based visual check for UI changes.
- Regenerate affected demonstration assets when necessary; preserve the original assets until the replacements are verified.
- Update GUI documentation when behavior, terminology, startup, or release instructions change.
- Inspect the staged diff and ensure `ACCERT_DEVELOPMENT_HISTORY.md` is not staged.

## Local GUI lifecycle

Start or reuse the local GUI with:

```bash
python tutorial/gui/launch_gui.py
```

Use `--port` or `ACCERT_GUI_PORT` when another process owns the default port. Stop a server recorded by the GUI with:

```bash
python tutorial/gui/stop_gui.py
```

The launcher reuses a healthy existing ACCERT GUI instance. It does not stop unrelated processes. A server started in the foreground can also be stopped with Ctrl-C.

## Future web distribution

The simplest future deployment is to keep the current Python HTTP handler and calculation modules, package them as one versioned server application, and place a reverse proxy or managed HTTPS service in front of it. A Docker image may be added later if the laboratory deployment environment benefits from containerized dependencies. Do not create a second calculation implementation or switch frameworks without an explicit architecture decision.

Suggested release flow:

```text
Update code → run tests → build one reproducible release → deploy → verify /health
```

The local `/health` endpoint reports the GUI version identifier and listening port. External publishing and deployment are intentionally outside the current task.

## Git handoff

- Commit cohesive changes with short descriptive messages using the user's Git identity.
- Keep lifecycle, visualization, tests, and demo assets in separate commits where practical.
- Do not push unless the user explicitly requests it.
