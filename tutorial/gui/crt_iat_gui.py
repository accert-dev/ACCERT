"""Local GUI for IAT, CRT, and connected IAT-to-CRT workflows.

Run from the repository root with:

    python tutorial/gui/crt_iat_gui.py

Then open:

    http://127.0.0.1:8765
"""

from __future__ import annotations

import json
import argparse
import errno
import mimetypes
import os
import re
import signal
import sys
import tempfile
import threading
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote
from urllib.request import urlopen
from urllib.error import URLError

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from crt import (
    accert_output_to_crt_baseline,
    results_to_dataframe,
    run_one_scenario,
    save_dashboard,
    waterfall_to_dataframe,
)
from crt.io.excel_inputs import InputStore
from crt.reactor_config import (
    REACTOR_CONFIGS,
    compatible_crt_types,
    iat_api_type_from_label,
    reactor_power_mwe,
)
from iat import level_account_summary, occ_local_foreign_totals, run_adjustment, run_occ_scenarios
from iat.data_loader import load_assumptions
from cost_escalation import TARGET_DOLLAR_YEAR


HOST = "127.0.0.1"
PORT = 8765
APP_VERSION = os.environ.get("ACCERT_GUI_VERSION", "local")
RUNTIME_DIR = Path(tempfile.gettempdir()) / "accert-gui"
OUTPUT_DIR = REPO_ROOT / "tutorial" / "gui_outputs"
DEFAULT_IAT_YEAR_DOLLAR = TARGET_DOLLAR_YEAR
LAND_COST_PER_GUI_UNIT = 1_000.0
LABOR_HOURS_PER_MILLION = 1_000_000.0
DEFAULT_LAND_COST_PER_ACRE = 22_000.0
IAT_FACTOR_FIELDS = ["import_tariff", "equipment", "material", "labor", "labor_o_and_m", "land", "catchall"]
DEFAULT_IAT_FACTORS = load_assumptions()["adjustment_factors"]
DEFAULT_CONSTRUCTION_DURATIONS = {
    name: values["construction_duration_months"] for name, values in REACTOR_CONFIGS.items()
}
DEFAULT_20S_LABOR_HOURS = {
    name: values["labor_hours_20s"] for name, values in REACTOR_CONFIGS.items()
}
BASE_GROUP_TITLES = {
    "10": "Capitalized Pre-Construction Costs",
    "20": "Capitalized Direct Costs",
    "30": "Capitalized Indirect Services Costs",
    "50": "Capitalized Supplementary Costs",
    "60": "Capitalized Financial Costs",
}


def land_cost_from_gui(value: float | int | None) -> float | None:
    """Convert GUI $k/acre input to the CRT native $/acre unit."""
    return None if value is None else float(value) * LAND_COST_PER_GUI_UNIT


def labor_hours_from_gui(value: float | int | None) -> float | None:
    """Convert GUI million labor-hours input to native labor-hours."""
    return None if value is None else float(value) * LABOR_HOURS_PER_MILLION


HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ACCERT IAT and CRT GUI</title>
  <style>
    :root {
      --ink: #172331;
      --muted: #687587;
      --line: #d7dee8;
      --panel: #f7f9fc;
      --surface: #ffffff;
      --surface-soft: #f3f7fa;
      --highlight: #e7f3f4;
      --highlight-ink: #123b4a;
      --accent: #17647f;
      --accent-2: #2f7d57;
      --orange: #f28c34;
      --purple: #8062a7;
      --sidebar: #082f4a;
      --sidebar-2: #0e7284;
      --bg: #edf2f8;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
      font-size: 14px;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 14px 18px;
      border-bottom: 1px solid #0c3a50;
      background: #082f4a;
      color: white;
    }
    h1 {
      margin: 0;
      font-size: 20px;
      font-weight: 700;
      letter-spacing: 0;
    }
    main {
      display: grid;
      grid-template-columns: minmax(360px, 420px) minmax(0, 1fr);
      min-height: calc(100vh - 57px);
    }
    aside {
      border-right: 0;
      background: var(--sidebar);
      padding: 14px;
      overflow: auto;
    }
    section {
      padding: 16px 18px;
      overflow: auto;
    }
    fieldset {
      border: 1px solid rgba(207,239,248,0.28);
      border-radius: 8px;
      margin: 0 0 12px;
      padding: 12px;
      background: rgba(255,255,255,0.08);
      color: #eef7fb;
    }
    legend {
      padding: 0 6px;
      font-weight: 700;
      color: #c8f4ff;
      text-transform: uppercase;
      font-size: 12px;
      letter-spacing: 0.04em;
    }
    label {
      display: block;
      font-weight: 600;
      margin: 9px 0 4px;
      color: #edf8fc;
    }
    .label-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin: 9px 0 4px;
    }
    .label-row label { margin: 0; }
    .help {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      border: 1px solid rgba(255,255,255,0.45);
      color: #fff;
      font-size: 12px;
      font-weight: 800;
      cursor: help;
      flex: 0 0 auto;
    }
    input, select {
      width: 100%;
      min-width: 0;
      box-sizing: border-box;
      border: 1px solid #90b9cb;
      border-radius: 6px;
      padding: 9px 10px;
      font: inherit;
      background: #f7fbff;
      color: var(--ink);
    }
    .readonly-note {
      border: 1px solid rgba(144,185,203,0.45);
      border-radius: 5px;
      padding: 8px 9px;
      background: rgba(247,251,255,0.28);
      color: #eef7fb;
      font-weight: 700;
    }
    .field-note {
      margin-top: 5px;
      color: rgba(255,255,255,0.68);
      font-size: 11px;
      line-height: 1.35;
    }
    input[type="checkbox"] {
      width: auto;
      margin-right: 7px;
    }
    .row {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .row > div,
    .triple > div {
      min-width: 0;
      display: flex;
      flex-direction: column;
    }
    .row > div > label,
    .triple > div > label,
    .row > div > .label-row,
    .triple > div > .label-row {
      min-height: 2.8em;
      display: flex;
      align-items: flex-end;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }
    .triple {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }
    .crt-cost-row > div {
      display: flex;
      flex-direction: column;
    }
    .crt-cost-row .label-row {
      min-height: 44px;
      align-items: flex-start;
    }
    .baseline-control-row {
      display: flex;
      align-items: stretch;
      gap: 8px;
    }
    .baseline-control-row > select {
      flex: 1 1 auto;
      min-width: 0;
    }
    .baseline-control-row .file-input-row {
      flex: 0 0 235px;
      min-width: 0;
    }
    .baseline-control-row .file-input-row input {
      min-width: 0;
    }
    .lever-matrix {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 12px;
      padding: 12px;
      border: 1px solid rgba(207,239,248,0.28);
      background: rgba(8, 47, 74, 0.18);
      border-radius: 6px;
    }
    .lever-stack {
      display: grid;
      grid-template-rows: repeat(2, 74px);
      gap: 10px;
    }
    #leverPanel .triple > div,
    #leverPanel .row > div,
    #leverPanel .lever-stack > div {
      min-width: 0;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      min-height: 74px;
    }
    #leverPanel .label-row {
      min-height: 34px;
      margin: 0 0 5px;
      align-items: flex-end;
    }
    #leverPanel input,
    #leverPanel select {
      height: 38px;
    }
    .inline {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 10px;
      color: var(--muted);
      font-weight: 600;
      color: #dceef5;
    }
    button {
      border: 0;
      border-radius: 7px;
      padding: 10px 14px;
      font: inherit;
      font-weight: 700;
      color: white;
      background: var(--orange);
      cursor: pointer;
    }
    button.secondary { background: rgba(255,255,255,0.14); border: 1px solid rgba(199,239,250,0.45); }
    button:disabled { opacity: 0.55; cursor: not-allowed; }
    button:focus-visible, input:focus-visible, select:focus-visible, summary:focus-visible {
      outline: 3px solid rgba(242, 140, 52, 0.72);
      outline-offset: 2px;
    }
    .actions {
      display: flex;
      gap: 10px;
      padding: 4px 0 12px;
    }
    .hidden { display: none !important; }
    .status {
      min-height: 22px;
      color: rgba(255,255,255,0.82);
      font-weight: 600;
    }
    .status.error { color: #a13030; }
    header .status.error { color: #ffd0d0; }
    .panel-intro {
      padding: 4px 2px 12px;
      color: rgba(255,255,255,0.78);
      line-height: 1.45;
    }
    .panel-intro strong { color: #fff; }
    .workflow-steps {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 6px;
      margin-bottom: 14px;
    }
    .workflow-step {
      appearance: none;
      width: 100%;
      min-height: 64px;
      padding: 8px;
      border: 1px solid rgba(207,239,248,0.2);
      border-radius: 7px;
      background: rgba(255,255,255,0.06);
      color: rgba(255,255,255,0.66);
      font-size: 11px;
      line-height: 1.25;
      text-align: left;
      white-space: normal;
      overflow-wrap: anywhere;
    }
    .workflow-step .step-number {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 20px;
      height: 20px;
      margin-bottom: 5px;
      border-radius: 50%;
      background: rgba(255,255,255,0.16);
      color: #fff;
      font-weight: 800;
    }
    .workflow-step.active {
      border-color: rgba(242,140,52,0.9);
      background: rgba(242,140,52,0.14);
      color: #fff;
    }
    .workflow-step.done { border-color: rgba(93,196,146,0.7); color: #d9f5e7; }
    .workflow-step.done .step-number { background: var(--accent-2); }
    .workflow-step:hover { border-color: rgba(242,140,52,0.7); color: #fff; }
    .workflow-step[aria-current="step"] { box-shadow: inset 3px 0 0 var(--orange); }
    .advanced-section {
      margin: 10px 0 12px;
      border: 1px solid rgba(207,239,248,0.2);
      border-radius: 7px;
      background: rgba(8,47,74,0.24);
    }
    .advanced-section > summary {
      padding: 10px 11px;
      color: #d9f5e7;
      font-weight: 750;
      cursor: pointer;
    }
    .advanced-section > fieldset {
      margin: 0;
      border: 0;
      border-top: 1px solid rgba(207,239,248,0.18);
      border-radius: 0;
      background: transparent;
    }
    .run-summary {
      margin: 10px 0 12px;
      padding: 11px 12px;
      border: 1px solid rgba(207,239,248,0.26);
      border-radius: 7px;
      background: rgba(255,255,255,0.08);
      color: rgba(255,255,255,0.82);
      font-size: 12px;
      line-height: 1.5;
    }
    .run-summary strong { display: block; color: #fff; margin-bottom: 3px; }
    .processing-stage {
      display: none;
      margin-top: 8px;
      color: #d9f5e7;
      font-size: 12px;
      font-weight: 700;
    }
    .processing-stage.visible { display: block; }
    .processing-stage[data-stage="error"] { color: #ffd0d0; }
    .empty-state {
      display: grid;
      place-items: center;
      min-height: 360px;
      padding: 36px;
      text-align: center;
      border: 1px dashed #b8c8d6;
      border-radius: 10px;
      background: var(--surface-soft);
      color: var(--muted);
    }
    .empty-state h2 { margin: 0 0 8px; color: var(--ink); }
    .empty-state p { max-width: 520px; margin: 0; line-height: 1.5; }
    .term-guide {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 12px;
    }
    .term-guide span {
      padding: 4px 7px;
      border-radius: 5px;
      background: #e5eef3;
      border: 1px solid #c9dbe4;
      color: var(--ink);
      font-size: 11px;
      font-weight: 700;
    }
    .hero {
      border-radius: 8px;
      padding: 18px;
      color: #fff;
      background: linear-gradient(135deg, #0d3f58, #1b7c8e 60%, #2f7d57);
      box-shadow: 0 10px 24px rgba(22, 50, 74, 0.14);
      margin-bottom: 14px;
    }
    .hero h2 {
      margin: 0 0 4px;
      font-size: 24px;
      letter-spacing: 0;
    }
    .hero p { margin: 0; color: rgba(255,255,255,0.82); font-weight: 600; }
    .summary {
      display: grid;
      grid-template-columns: repeat(4, minmax(130px, 1fr));
      gap: 10px;
      margin-bottom: 14px;
    }
    .result-summary-cards {
      grid-template-columns: repeat(5, minmax(120px, 1fr));
      margin: 14px 0 18px;
    }
    .result-summary-cards .metric {
      min-height: 96px;
      border-top: 3px solid var(--accent);
    }
    .iat-results-section, .crt-results-section {
      margin: 18px 0 22px;
      padding-top: 4px;
    }
    .iat-results-section {
      border-top: 3px solid var(--accent);
    }
    .crt-results-section {
      border-top: 3px solid var(--accent-2);
    }
    .iat-results-section > h3, .crt-results-section > h3 {
      margin: 0 0 10px;
      font-size: 20px;
    }
    .iat-summary-cards {
      grid-template-columns: repeat(3, minmax(160px, 1fr));
      margin: 10px 0 16px;
    }
    .iat-summary-cards .metric { border-top: 3px solid var(--accent); }
    .iat-only-summary {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin: 10px 0 12px;
    }
    .iat-only-summary .metric { border-top: 3px solid var(--accent); min-height: 88px; }
    .iat-only-summary .metric-emphasis { border: 2px solid var(--accent); border-top-width: 4px; background: #f8fcfd; }
    .iat-only-summary .metric-emphasis .label { color: var(--accent); }
    .iat-scenario-note {
      border-left: 4px solid var(--accent);
      background: var(--surface-soft);
      color: var(--muted);
      padding: 9px 12px;
      margin: 8px 0 10px;
      font-size: 12px;
      font-weight: 700;
      line-height: 1.45;
    }
    .iat-scenario-table { margin-bottom: 14px; }
    .iat-scenario-table td.iat-adjusted-occ { background: var(--highlight); color: var(--highlight-ink); font-weight: 800; }
    .iat-country {
      margin: 2px 0 8px;
      color: var(--muted);
      font-size: 16px;
    }
    .iat-breakdown {
      margin: 2px 0 18px;
      color: var(--muted);
      font-size: 16px;
    }
    .breakdown-label { margin-bottom: 6px; }
    .breakdown-items {
      display: flex;
      flex-wrap: wrap;
      gap: 8px 24px;
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--surface-soft);
    }
    .breakdown-items span { color: var(--muted); }
    .breakdown-items strong { color: var(--ink); margin-left: 4px; }
    .crt-key-cards {
      grid-template-columns: repeat(2, minmax(220px, 1fr));
      margin: 8px 0 16px;
    }
    .crt-key-cards .metric { border-top: 3px solid var(--accent-2); }
    .crt-results-grid-wrap {
      overflow-x: auto;
      margin: 8px 0 16px;
    }
    .crt-results-grid {
      display: grid;
      grid-template-columns: minmax(170px, 1.35fr) repeat(4, minmax(120px, 1fr));
      min-width: 720px;
      border: 1px solid var(--line);
      border-radius: 7px;
      overflow: hidden;
      background: #fff;
    }
    .crt-results-grid > div {
      min-height: 58px;
      display: flex;
      align-items: center;
      padding: 10px 12px;
      border-right: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
    }
    .crt-results-grid > div:nth-child(5n) { border-right: 0; }
    .crt-results-grid > div:nth-last-child(-n + 5) { border-bottom: 0; }
    .crt-results-grid .grid-head {
      min-height: 42px;
      background: var(--surface-soft);
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
    }
    .crt-results-grid .grid-label { font-weight: 800; color: var(--ink); }
    .crt-results-grid .grid-value { justify-content: flex-end; color: var(--ink); font-weight: 750; font-variant-numeric: tabular-nums; }
    .crt-results-grid .grid-sub { display: block; margin-left: 5px; color: var(--muted); font-size: 10px; font-weight: 600; }
    .crt-metric-group { margin: 14px 0 18px; }
    .crt-metric-heading { display: flex; align-items: center; gap: 8px; margin: 0 0 8px; color: var(--ink); font-size: 18px; }
    .crt-metric-cards { display: grid; grid-template-columns: repeat(3, minmax(150px, 1fr)); gap: 10px; }
    .crt-metric-cards .metric { min-height: 82px; border-top: 3px solid var(--accent-2); }
    .crt-metric-reduction { margin: 7px 2px 0; color: var(--muted); font-size: 12px; }
    .crt-metric-reduction strong { color: var(--ink); }
    .info-tip { border-color: #8aa0b2; color: var(--accent); background: transparent; padding: 0; }
    .info-tip:hover, .info-tip:focus-visible { background: #e7f1f5; }
    .metric {
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      background: #fff;
      box-shadow: 0 2px 8px rgba(25, 47, 70, 0.06);
    }
    .metric .label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }
    .metric .value {
      font-size: 20px;
      font-weight: 750;
      margin-top: 4px;
    }
    .metric .subvalue,
    .cell-sub {
      margin-top: 3px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }
    .tabs {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin: 14px 0 10px;
    }
    .tabs button {
      background: #fff;
      color: var(--accent);
      border: 1px solid var(--line);
      padding: 8px 10px;
    }
    .tabs button.active {
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
    }
    .tab-panel { display: none; }
    .tab-panel.active { display: block; }
    .chart-grid {
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      gap: 16px;
      align-items: stretch;
    }
    .chart-panel {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 18px 22px;
      min-height: 570px;
      box-shadow: 0 2px 8px rgba(25, 47, 70, 0.06);
    }
    .chart-panel h3 {
      margin: 0 0 12px;
      font-size: 19px;
      color: var(--ink);
    }
    .chart-panel svg {
      width: 100%;
      height: 500px;
      display: block;
    }
    .axis text, .tick text { fill: #596775; font-size: 11px; }
    .axis line, .axis path, .grid line, line.grid { stroke: #ccd5df; }
    .grid line, line.grid { stroke-width: 1; }
    .hoverable { cursor: pointer; transition: opacity 120ms ease; }
    .hoverable:hover { opacity: 0.78; }
    #tooltip {
      display: none;
      position: fixed;
      z-index: 20;
      pointer-events: none;
      max-width: 260px;
      padding: 8px 10px;
      border-radius: 6px;
      background: rgba(15, 31, 45, 0.94);
      color: #fff;
      font-size: 12px;
      line-height: 1.35;
      box-shadow: 0 8px 20px rgba(0,0,0,0.22);
    }
    #tooltip .tip-label,
    #tooltip .tip-value {
      display: block;
      white-space: nowrap;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 10px 0 16px;
      background: #fff;
      font-size: 13px;
    }
    th, td {
      border: 1px solid var(--line);
      padding: 6px 7px;
      text-align: right;
      vertical-align: top;
    }
    th {
      background: #17647f;
      color: #fff;
      font-weight: 700;
    }
    td:first-child, td:nth-child(2), th:first-child, th:nth-child(2) {
      text-align: left;
    }
    .coa-parent {
      cursor: pointer;
      font-weight: 750;
      background: #f8fbff;
    }
    .coa-parent td:first-child::before {
      content: "+ ";
      color: var(--accent);
      font-weight: 900;
    }
    .coa-parent.expanded td:first-child::before { content: "- "; }
    .coa-child.hidden-row { display: none; }
    .coa-child td:first-child { padding-left: 24px; }
    .table-toolbar {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 8px;
      margin: 8px 0 4px;
      color: var(--muted);
      font-weight: 700;
    }
    .table-toolbar select {
      width: auto;
      min-width: 160px;
      background: #fff;
      color: var(--ink);
    }
    .links {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 10px 0 16px;
    }
    .links a {
      border: 1px solid var(--line);
      border-radius: 5px;
      padding: 7px 9px;
      color: var(--accent);
      text-decoration: none;
      font-weight: 700;
      background: #fff;
    }
    .download-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 10px 12px;
      margin-bottom: 12px;
      color: var(--muted);
      font-weight: 700;
    }
    .download-bar a {
      color: white;
      background: var(--accent);
      border-radius: 6px;
      padding: 8px 10px;
      text-decoration: none;
    }
    .file-input-row {
      display: flex;
      gap: 6px;
    }
    .file-input-row input[type="text"] {
      flex: 1;
      min-width: 0;
      background: #f7fbff;
      color: var(--ink);
      border: 1px solid #90b9cb;
      border-radius: 5px;
      padding: 7px 8px;
      font: inherit;
      cursor: default;
    }
    .file-input-row button {
      flex: 0 0 auto;
      padding: 7px 10px;
      font-size: 12px;
      background: rgba(255,255,255,0.18);
      border: 1px solid rgba(199,239,250,0.55);
    }
    select[multiple] {
      min-height: 68px;
      padding: 4px;
    }
    select[multiple] option {
      padding: 4px 6px;
    }
    .country-dropdown { position: relative; }
    .country-dropdown-btn {
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      text-align: left;
      padding: 7px 8px;
      background: #f7fbff;
      color: var(--ink);
      border: 1px solid #90b9cb;
      border-radius: 5px;
      font: inherit;
      font-weight: 400;
      cursor: pointer;
    }
    .country-dropdown-menu {
      position: absolute;
      z-index: 100;
      top: calc(100% + 2px);
      left: 0;
      right: 0;
      background: #f7fbff;
      border: 1px solid #90b9cb;
      border-radius: 5px;
      padding: 4px 0;
      box-shadow: 0 4px 12px rgba(0,0,0,0.22);
    }
    .country-option {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 7px 10px;
      cursor: pointer;
      color: var(--ink);
      font-weight: 400;
    }
    .country-option:hover { background: #e4f3fa; }
    .country-option input[type="checkbox"] { margin: 0; cursor: pointer; }
    .scenario-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.72);
      padding: 12px;
      margin: 12px 0 16px;
    }
    .base-case {
      border: 1px solid #bfd5df;
      border-radius: 8px;
      background: #fff;
      padding: 14px;
      margin: 0 0 16px;
      box-shadow: 0 2px 8px rgba(25, 47, 70, 0.06);
    }
    .scenario-card h4 {
      margin: 0 0 8px;
      font-size: 16px;
    }
    .result-note {
      border-left: 4px solid var(--accent);
      background: #fff;
      color: var(--muted);
      padding: 10px 12px;
      margin: 8px 0 12px;
      font-weight: 700;
      line-height: 1.42;
    }
    img.dashboard {
      max-width: 100%;
      border: 1px solid var(--line);
      background: #fff;
    }
    pre {
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      padding: 10px;
      max-height: 300px;
    }
    @media (max-width: 900px) {
      main { grid-template-columns: 1fr; }
      aside { border-right: 0; border-bottom: 1px solid var(--line); }
      .summary { grid-template-columns: 1fr 1fr; }
      .result-summary-cards { grid-template-columns: repeat(2, minmax(130px, 1fr)); }
      .chart-grid { grid-template-columns: 1fr; }
    }
    @media (max-width: 520px) {
      .workflow-steps { grid-template-columns: 1fr; }
      .row, .triple, .lever-matrix { grid-template-columns: 1fr; }
      .baseline-control-row { flex-direction: column; }
      .baseline-control-row .file-input-row { flex-basis: auto; }
      .result-summary-cards, .summary, .iat-summary-cards, .iat-only-summary, .crt-key-cards, .crt-metric-cards { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <h1>ACCERT IAT and CRT GUI</h1>
    <div class="status" id="status">Ready<div class="processing-stage" id="processingStage"></div></div>
  </header>
  <main>
    <aside>
      <div class="panel-intro"><strong>Build a clear cost scenario.</strong><br>Choose a source, review the key assumptions, then run the analysis.</div>
      <nav class="workflow-steps" aria-label="Workflow steps">
        <button class="workflow-step active" type="button" data-step="1" aria-controls="taskSourcePanel" aria-current="step"><span class="step-number">1</span><br>Select task and source</button>
        <button class="workflow-step" type="button" data-step="2" aria-controls="iatPanel" aria-current="false"><span class="step-number">2</span><br>Configure assumptions</button>
        <button class="workflow-step" type="button" data-step="3" aria-controls="runSummary" aria-current="false"><span class="step-number">3</span><br>Run and review</button>
      </nav>
      <div class="actions">
        <button id="runBtn">Run analysis</button>
        <button class="secondary" id="resetBtn" type="button">Reset</button>
      </div>

      <fieldset id="taskSourcePanel" tabindex="-1">
        <legend>Workflow</legend>
        <label for="workflow">Mode</label>
        <select id="workflow">
          <option value="iat_only">IAT only</option>
          <option value="crt_only">CRT only</option>
          <option value="iat_crt" selected>IAT then CRT</option>
        </select>
        <label for="outputName">Output name</label>
        <input id="outputName" value="AP1000 United States Baseline">
        <div class="field-note" id="outputNameHint">Auto-generated from reactor and country. Edit it to add a description.</div>
      </fieldset>

      <fieldset id="iatPanel" tabindex="-1">
        <legend>IAT Inputs</legend>
        <div class="row">
          <div>
            <label for="iatInputMode">IAT source</label>
            <select id="iatInputMode">
              <option value="occ" selected>Standard OCC</option>
              <option value="csv">Code of Account structure</option>
            </select>
          </div>
          <div>
            <label for="iatReactorType">Reactor type</label>
            <select id="iatReactorType">
              <option value="Large Reactor" selected>Large Reactor</option>
              <option value="SMR">SMR</option>
            </select>
          </div>
        </div>
        <div class="row">
          <div>
            <label>Country</label>
            <select id="countrySingle" class="hidden">
              <option value="United States" selected>United States / U.S. Baseline</option>
              <option value="China">China</option>
              <option value="Korea">South Korea</option>
              <option value="UAE">UAE</option>
              <option value="Poland">Poland</option>
              <option value="El Salvador">El Salvador</option>
              <option value="Thailand">Thailand</option>
              <option value="Vietnam">Vietnam</option>
              <option value="Indonesia">Indonesia</option>
            </select>
            <div id="countryMulti" class="country-dropdown">
              <button type="button" class="country-dropdown-btn" id="countryDropdownBtn">
              <span id="countryDropdownLabel">United States / U.S. Baseline</span><span>▾</span>
              </button>
              <div class="country-dropdown-menu hidden" id="countryDropdownMenu">
                <label class="country-option"><input type="checkbox" value="United States" checked> United States / U.S. Baseline</label>
                <label class="country-option"><input type="checkbox" value="Korea"> South Korea</label>
                <label class="country-option"><input type="checkbox" value="China"> China</label>
                <label class="country-option"><input type="checkbox" value="UAE"> UAE</label>
                <label class="country-option"><input type="checkbox" value="Poland"> Poland</label>
                <label class="country-option"><input type="checkbox" value="El Salvador"> El Salvador</label>
                <label class="country-option"><input type="checkbox" value="Thailand"> Thailand</label>
                <label class="country-option"><input type="checkbox" value="Vietnam"> Vietnam</label>
                <label class="country-option"><input type="checkbox" value="Indonesia"> Indonesia</label>
              </div>
            </div>
          </div>
          <div>
            <label>Year dollar</label>
            <div class="readonly-note">{{IAT_YEAR_DOLLAR}} CPI-U basis</div>
          </div>
        </div>
        <details class="advanced-section" id="iatAdvancedSection">
          <summary id="iatAssumptionsHeading" aria-controls="iatAdvancedFields">Advanced IAT Assumptions</summary>
        <div id="iatAdvancedFields">
        <div class="row">
          <div id="iatAssumptionCountryGroup">
            <label for="iatAssumptionCountry">Assumption country</label>
            <select id="iatAssumptionCountry"></select>
            <div class="field-note">Choose which selected country's factors you are editing.</div>
          </div>
          <div></div>
        </div>
        <div class="row">
          <div><label for="iatEquipmentFactor">Equipment factor</label><input id="iatEquipmentFactor" type="number" min="0" step="0.000001"></div>
          <div><label for="iatMaterialFactor">Material factor</label><input id="iatMaterialFactor" type="number" min="0" step="0.000001"></div>
        </div>
        <div class="row">
          <div><label for="iatLaborFactor">Labor factor</label><input id="iatLaborFactor" type="number" min="0" step="0.000001"></div>
          <div><label for="iatLandFactor">Land factor</label><input id="iatLandFactor" type="number" min="0" step="0.000001"></div>
        </div>
        <div class="row">
          <div><label for="iatLaborOandMFactor">Labor O&amp;M factor</label><input id="iatLaborOandMFactor" type="number" min="0" step="0.000001"></div>
          <div><label for="iatCatchallFactor">Catch-all factor</label><input id="iatCatchallFactor" type="number" min="0" step="0.000001"></div>
        </div>
        <div class="row">
          <div><label for="iatTariffFactor">Import tariff</label><input id="iatTariffFactor" type="number" min="0" step="0.000001"></div>
          <div></div>
        </div>
        <div class="status">Preset factors load with the selected country; edits apply only to this run.</div>
        </div>
        </details>
        <div id="iatCsvGroup" class="hidden">
          <label for="iatBaseline">IAT source file</label>
          <div class="baseline-control-row">
            <select id="iatBaseline">
              <option value="AP1000">Built-in ACCERT baseline · AP1000</option>
              <option value="SFR">Built-in ACCERT baseline · SFR</option>
              <option value="HTGR">Built-in ACCERT baseline · HTGR</option>
              <option value="custom">ACCERT account output / uploaded file</option>
            </select>
            <div id="iatUploadGroup" class="file-input-row hidden">
              <input type="text" id="iatCsvName" readonly placeholder="No file selected">
              <button type="button" id="iatBrowseBtn">Browse…</button>
              <input id="iatCsvFile" type="file" accept=".csv" class="hidden">
            </div>
          </div>
          <div class="status">Choose a built-in ACCERT baseline or select an ACCERT account output file generated by a previous run.</div>
        </div>
        <div id="electricOutputGroup" class="hidden">
          <label for="electricOutputMwe">Electric output (MWe)</label>
          <input id="electricOutputMwe" type="number" min="1" step="1" value="2234">
        </div>
        <div id="occScenarioGroup">
          <label for="scenarioCount">Scenario count ($/kWe inputs)</label>
          <input id="scenarioCount" type="number" min="1" max="3" step="1" value="3">
          <div id="occInputs" class="triple">
            <div><label for="occValue1">Scenario 1 ($/kWe)</label><input id="occValue1" type="number" value="5250"></div>
            <div><label for="occValue2">Scenario 2 ($/kWe)</label><input id="occValue2" type="number" value="5750"></div>
            <div><label for="occValue3">Scenario 3 ($/kWe)</label><input id="occValue3" type="number" value="6250"></div>
          </div>
        </div>
      </fieldset>

      <fieldset id="crtPanel" tabindex="-1">
        <legend>CRT Fixed Inputs</legend>
        <div id="crtReactorTypeGroup">
          <label for="crtReactorType">Reactor type</label>
          <select id="crtReactorType">
            <option selected>AP1000</option>
            <option>HTGR</option>
            <option>SFR</option>
          </select>
        </div>
        <div id="crtBaselineGroup">
          <label for="crtCsvName">Optional CRT baseline CSV</label>
          <div class="file-input-row">
            <input type="text" id="crtCsvName" readonly placeholder="Leave blank for built-in baseline">
            <button type="button" id="crtBrowseBtn">Browse…</button>
            <input id="crtCsvFile" type="file" accept=".csv" class="hidden">
          </div>
        </div>
        <div class="triple crt-cost-row">
          <div><div class="label-row"><label for="f22">Account 22 ($M)</label><span class="help" title="Factory allocation added to Account 22">?</span></div><input id="f22" type="text" inputmode="decimal" value="250"></div>
          <div><div class="label-row"><label for="f2321">Account 232.1 ($M)</label><span class="help" title="Factory allocation added to Account 232.1">?</span></div><input id="f2321" type="text" inputmode="decimal" value="150"></div>
          <div><label for="landCost">Land Cost ($k/acre)</label><input id="landCost" type="number" min="0" step="0.1" value="22"></div>
        </div>
        <div class="row">
          <div><label for="startup">Startup months</label><input id="startup" type="number" value="28"></div>
          <div><label for="staggering">Staggering ratio</label><input id="staggering" type="number" step="0.01" value="0.75"></div>
        </div>
        <div class="row">
          <div><label for="constructionDuration">Construction duration (months)</label><input id="constructionDuration" type="number" min="1" step="1" value="76"></div>
          <div><div class="label-row"><label for="total20sLaborHours">Total labor hours (million)</label><span class="help" title="Total labor hours for capitalized direct costs">?</span></div><input id="total20sLaborHours" type="number" min="0" step="0.01" value="51.11"></div>
        </div>
        <div class="inline"><input id="showLevers" type="checkbox"> Include lever table in dashboard image</div>
      </fieldset>

      <details class="advanced-section" id="advancedLevers">
        <summary aria-controls="leverPanel">Advanced CRT assumptions · CRT levers <span class="subvalue">Cost-reduction assumptions</span></summary>
      <fieldset id="leverPanel">
        <legend>CRT Levers</legend>
        <div class="triple">
          <div><label for="numOrders">Firm orders</label><input id="numOrders" type="number" min="2" step="1" value="10"></div>
          <div><label for="itcPercent">ITC %</label><input id="itcPercent" type="number" min="0" max="100" step="1" value="0"></div>
          <div><label for="designCompletion">Design compl. %</label><input id="designCompletion" type="number" value="70"></div>
        </div>
        <div class="triple">
          <div><label for="numNoak">NOAK unit</label><input id="numNoak" type="number" min="0" step="1" value="8"></div>
          <div><label for="nItc">ITC units</label><input id="nItc" type="number" min="0" step="1" value="0"></div>
          <div><label for="designMaturity">Design maturity</label><input id="designMaturity" type="number" min="0" max="2" step="0.1" value="1"></div>
        </div>
        <div class="row">
          <div><label for="interest">Interest %</label><input id="interest" type="number" value="6"></div>
          <div><label for="standardization">Standardization %</label><input id="standardization" type="number" value="80"></div>
        </div>
        <div class="lever-matrix">
          <div class="lever-stack">
            <div><label for="nProc">N supply chain</label><input id="nProc" type="number" min="0" max="10" step="1" value="3"></div>
            <div><label for="procExp">Supply chain prof.</label><input id="procExp" type="number" min="0" max="2" step="0.1" value="0.5"></div>
          </div>
          <div class="lever-stack">
            <div><label for="nAe">N A/E</label><input id="nAe" type="number" min="0" max="10" step="1" value="4"></div>
            <div><label for="aeExp">A/E prof.</label><input id="aeExp" type="number" min="0" max="2" step="0.1" value="0.5"></div>
          </div>
          <div class="lever-stack">
            <div><label for="nCons">N construction</label><input id="nCons" type="number" min="0" max="10" step="1" value="5"></div>
            <div><label for="ceExp">Construction prof.</label><input id="ceExp" type="number" min="0" max="2" step="0.1" value="0.5"></div>
          </div>
        </div>
        <div class="triple">
          <div><label for="bopGrade">Commercial BOP</label><select id="bopGrade"><option value="0">False</option><option value="1">True</option></select></div>
          <div><label for="rbGrade">Non-safety-related RB</label><select id="rbGrade"><option value="0">False</option><option value="1">True</option></select></div>
          <div><label for="modularity">Modular civil constr.</label><select id="modularity"><option value="0">False</option><option value="1">True</option></select></div>
        </div>
      </fieldset>
      </details>
      <div class="run-summary" id="runSummary" tabindex="-1" aria-live="polite"><strong>Ready to run</strong>Choose a workflow and review the selected source and assumptions here before starting.</div>
      <div class="status error hidden" id="inputValidation" role="alert"></div>
    </aside>
    <section>
      <div id="result">
        <div class="empty-state" id="emptyState" role="status" aria-live="polite">
          <div><h2 id="emptyTitle">Connected IAT → CRT results will appear here</h2><p id="emptyDescription">Run the connected workflow to see summary cards, interactive charts, tables, and downloadable output files.</p><div class="term-guide" id="termGuide"><span>IAT · International Adjustment Tool</span><span>CRT · Cost Reduction Tool</span><span>FOAK · First-of-a-Kind</span><span>NOAK · Nth-of-a-Kind</span><span>Levers · cost-reduction levers</span></div></div>
        </div>
      </div>
    </section>
  </main>
  <div id="tooltip"></div>

  <script>
    const $ = (id) => document.getElementById(id);
    let lastData = null;
    let coaUnit = "billion";

    let _csvFileContent = null;
    let _csvFilePath = null;
    let _crtFileContent = null;
    let _crtFilePath = null;
    let _lastCrtReactorType = null;
    let _lastGeneratedOutputName = "";
    let _outputNameCustomized = false;
    const defaultIatYearDollar = Number("{{IAT_YEAR_DOLLAR}}");
    const LAND_COST_GUI_TO_BACKEND = Number("{{LAND_COST_PER_GUI_UNIT}}");
    const LABOR_HOURS_GUI_TO_BACKEND = Number("{{LABOR_HOURS_PER_MILLION}}");
    const iatFactorDefaults = {{IAT_FACTOR_DEFAULTS}};
    const iatFactorIds = {import_tariff: "iatTariffFactor", equipment: "iatEquipmentFactor", material: "iatMaterialFactor", labor: "iatLaborFactor", labor_o_and_m: "iatLaborOandMFactor", land: "iatLandFactor", catchall: "iatCatchallFactor"};
    const iatFactorOverrides = {};
    const reactorConfigs = {{REACTOR_CONFIGS}};
    let loadedIatCountry = null;

    function numberValue(id) {
      const value = $(id).value.trim().replace(/,/g, "");
      return value === "" ? null : Number(value);
    }

    function landCostToBackend(value) {
      return value === null ? null : value * LAND_COST_GUI_TO_BACKEND;
    }

    function laborHoursToBackend(value) {
      return value === null ? null : value * LABOR_HOURS_GUI_TO_BACKEND;
    }

    function formatMillionLaborHours(nativeHours) {
      return (Number(nativeHours) / LABOR_HOURS_GUI_TO_BACKEND).toFixed(2).replace(/\.?(0+)$/, "");
    }

    function occScenarioValues() {
      const count = Math.max(1, Math.min(3, Number($("scenarioCount").value || 1)));
      const values = [];
      for (let i = 1; i <= count; i++) values.push(numberValue(`occValue${i}`));
      return values;
    }

    function selectedCountries() {
      if ($("workflow").value === "iat_crt") return [$("countrySingle").value];
      return Array.from(document.querySelectorAll("#countryDropdownMenu input[type='checkbox']:checked"))
        .map(cb => cb.value);
    }

    function activeIatCountry() {
      if ($("workflow").value === "iat_crt") return $("countrySingle").value;
      return $("iatAssumptionCountry").value || selectedCountries()[0] || "United States";
    }

    function saveIatFactorOverrides(country = activeIatCountry()) {
      if (!country) return;
      const values = {};
      Object.entries(iatFactorIds).forEach(([name, id]) => values[name] = numberValue(id));
      iatFactorOverrides[country] = values;
    }

    function loadIatFactorDefaults() {
      const country = activeIatCountry();
      if (loadedIatCountry && loadedIatCountry !== country) saveIatFactorOverrides(loadedIatCountry);
      const values = iatFactorOverrides[country] || iatFactorDefaults[country] || {};
      Object.entries(iatFactorIds).forEach(([name, id]) => {
        const value = values[name];
        $(id).value = value === undefined || value === null ? "" : Number(value).toFixed(4);
      });
      loadedIatCountry = country;
    }

    function displayCountryName(country) {
      return country === "Korea" ? "South Korea" : country;
    }

    function updateCountryDropdownLabel() {
      const selected = Array.from(
        document.querySelectorAll("#countryDropdownMenu input[type='checkbox']:checked")
      ).map(cb => displayCountryName(cb.value));
      $("countryDropdownLabel").textContent = selected.length ? selected.join(", ") : "Select countries";
      updateIatAssumptionCountryOptions();
    }

    function updateIatAssumptionCountryOptions() {
      const countries = $("workflow").value === "iat_crt"
        ? [$("countrySingle").value]
        : selectedCountries();
      const select = $("iatAssumptionCountry");
      const current = activeIatCountry();
      select.innerHTML = countries.map(country => `<option value="${esc(country)}">${esc(displayCountryName(country))}</option>`).join("");
      select.value = countries.includes(current) ? current : (countries[0] || "United States");
      updateIatAssumptionContext(countries);
    }

    function updateIatAssumptionContext(countries = selectedCountries()) {
      const isConnected = $("workflow").value === "iat_crt";
      const country = isConnected ? $("countrySingle").value : ($("iatAssumptionCountry").value || countries[0] || "United States");
      $("iatAssumptionsHeading").textContent = `Advanced IAT Assumptions — ${displayCountryName(country)}`;
      $("iatAssumptionCountryGroup").classList.toggle("hidden", isConnected || countries.length <= 1);
    }

    function baselineOptionsForIat() {
      return $("iatReactorType").value === "Large Reactor" ? ["AP1000"] : ["SFR", "HTGR"];
    }

    function selectedBaselineModel() {
      const selected = $("iatBaseline").value;
      return selected === "custom" ? $("crtReactorType").value : selected;
    }

    function syncBaselineSelection() {
      const shared = $("workflow").value === "iat_crt";
      const allowed = baselineOptionsForIat();
      const baseline = $("iatBaseline");
      const isCustom = baseline.value === "custom";
      $("iatUploadGroup").classList.toggle("hidden", !isCustom);
      Array.from(baseline.options).forEach(option => {
        option.disabled = option.value !== "custom" && !allowed.includes(option.value);
      });
      if (baseline.value !== "custom" && !allowed.includes(baseline.value)) baseline.value = allowed[0];
      const model = selectedBaselineModel();
      const config = reactorConfigs[model];
      if (baseline.value !== "custom" && config) {
        _csvFileContent = null;
        _csvFilePath = `src/crt/data/${config.baseline_csv}`;
        $("iatCsvName").value = `${config.baseline_csv} (${model})`;
        $("electricOutputMwe").value = String(config.power_mwe);
      }
      const crtSelect = $("crtReactorType");
      Array.from(crtSelect.options).forEach(option => {
        option.disabled = shared ? !allowed.includes(option.value) : false;
      });
      if (shared && allowed.includes(model)) {
        crtSelect.value = model;
        updateCrtDefaults(true);
      } else if (shared && !allowed.includes(crtSelect.value)) {
        crtSelect.value = allowed[0];
        updateCrtDefaults(true);
      }
      crtSelect.disabled = shared && baseline.value !== "custom";
    }

    function updateDefaultCsvPath() {
      syncBaselineSelection();
    }

    function updateElectricOutputDefault() {
      const model = selectedBaselineModel();
      if (reactorConfigs[model]) $("electricOutputMwe").value = String(reactorConfigs[model].power_mwe);
    }

    function updateCrtDefaults(force = false) {
      const rt = $("crtReactorType").value;
      if (!force && _lastCrtReactorType === rt) return;
      _lastCrtReactorType = rt;
      if (rt === "AP1000") {
        $("startup").value = "25";
        $("bopGrade").value = "0";
        $("modularity").value = "0";
      } else {
        $("startup").value = "16";
        $("bopGrade").value = "1";
        $("modularity").value = "1";
      }
      $("constructionDuration").value = String(reactorConfigs[rt].construction_duration_months);
      $("total20sLaborHours").value = formatMillionLaborHours(reactorConfigs[rt].labor_hours_20s);
    }

    function syncCrtOptionsToIat() { syncBaselineSelection(); }

    function apiReactorType() {
      if ($("workflow").value === "iat_crt") {
        return iatApiTypeForIat($('iatReactorType').value);
      }
      const rt = $("iatReactorType").value;
      const mode = $("iatInputMode").value;
      if (mode === "csv") return rt === "Large Reactor" ? "ACCERT output-LR" : "ACCERT output-SMR";
      return rt === "Large Reactor" ? "large reactor" : "SMR";
    }

    function iatApiTypeForIat(iatType) {
      const family = iatType === "Large Reactor" ? "LR" : "SMR";
      const prefix = $("iatInputMode").value === "csv" ? "ACCERT output-" : "";
      return prefix + family;
    }

    function payload() {
      return {
        workflow: $("workflow").value,
        output_name: $("outputName").value,
        iat: {
          input_mode: $("iatInputMode").value,
          reactor_type: apiReactorType(),
          countries: selectedCountries(),
          adjustment_factor_overrides: (() => { saveIatFactorOverrides(); return iatFactorOverrides; })(),
          baseline_reactor_type: selectedBaselineModel(),
          year_dollar: defaultIatYearDollar,
          input_csv: _csvFilePath,
          csv_content: _csvFileContent,
          csv_filename: _csvFileContent ? $("iatCsvName").value : null,
          electric_output_mwe: numberValue("electricOutputMwe"),
          scenario_count: numberValue("scenarioCount"),
          occ_values: occScenarioValues()
        },
        crt: {
          reactor_type: $("crtReactorType").value,
          baseline_csv: _crtFilePath,
          baseline_csv_content: _crtFileContent,
          baseline_csv_filename: _crtFileContent ? $("crtCsvName").value : null,
          f_22: numberValue("f22") === null ? null : numberValue("f22") * 1000000,
          f_2321: numberValue("f2321") === null ? null : numberValue("f2321") * 1000000,
          land_cost_per_acre_0: landCostToBackend(numberValue("landCost")),
          startup_0: numberValue("startup"),
          construction_duration_0: numberValue("constructionDuration"),
          total_20s_labor_hours: laborHoursToBackend(numberValue("total20sLaborHours")),
          staggering_ratio: numberValue("staggering"),
          show_levers: $("showLevers").checked
        },
        levers: {
          num_orders: numberValue("numOrders"),
          num_NOAK: numberValue("numNoak"),
          itc_percent: numberValue("itcPercent"),
          n_itc: numberValue("nItc"),
          interest_percent: numberValue("interest"),
          design_completion_percent: numberValue("designCompletion"),
          design_maturity: numberValue("designMaturity"),
          proc_exp: numberValue("procExp"),
          N_proc: numberValue("nProc"),
          ce_exp: numberValue("ceExp"),
          N_cons: numberValue("nCons"),
          ae_exp: numberValue("aeExp"),
          N_AE: numberValue("nAe"),
          standardization_percent: numberValue("standardization"),
          modularity_code: Number($("modularity").value),
          bop_grade_code: Number($("bopGrade").value),
          rb_grade_code: Number($("rbGrade").value)
        }
      };
    }

    function updatePanels() {
      const workflow = $("workflow").value;
      const isConnected = workflow === "iat_crt";
      $("iatInputMode").disabled = workflow === "iat_crt";
      $("iatPanel").classList.toggle("hidden", workflow === "crt_only");
      $("crtPanel").classList.toggle("hidden", workflow === "iat_only");
      $("advancedLevers").classList.toggle("hidden", workflow === "iat_only");
      $("crtBaselineGroup").classList.toggle("hidden", workflow !== "crt_only");
      $("crtReactorTypeGroup").classList.toggle("hidden", workflow !== "crt_only");
      if (workflow === "iat_crt") {
        $("iatInputMode").value = "csv";
        $("iatCsvGroup").classList.remove("hidden");
        $("occScenarioGroup").classList.add("hidden");
      }
      syncCrtOptionsToIat();
      const inputMode = $("iatInputMode").value;
      const isCsvMode = inputMode === "csv";
      if (workflow !== "iat_crt") {
        const isCsv = inputMode === "csv";
        $("iatCsvGroup").classList.toggle("hidden", !isCsv);
        $("occScenarioGroup").classList.toggle("hidden", isCsv);
      }
      $("countrySingle").classList.toggle("hidden", !isConnected);
      $("countryMulti").classList.toggle("hidden", isConnected);
      updateIatAssumptionCountryOptions();
      $("electricOutputGroup").classList.toggle("hidden", !isCsvMode);
      if (isCsvMode) {
        updateDefaultCsvPath();
        updateElectricOutputDefault();
      }
      updateScenarioInputs();
      updateCrtDefaults();
      const maxOrders = Math.max(0, Number($("numOrders").value || 0));
      ["nProc", "nCons", "nAe", "nItc", "numNoak"].forEach(id => {
        $(id).max = maxOrders;
        if (Number($(id).value) > maxOrders) $(id).value = maxOrders;
      });
      updateRunSummary();
      updateOutputName();
      updateEmptyState();
      if (!$('runBtn').disabled) setWorkflowStep(workflow === "iat_only" ? 2 : 1);
    }

    function validateAdvancedInputs() {
      const errors = [];
      const orders = numberValue("numOrders");
      const noak = numberValue("numNoak");
      const itcPercent = numberValue("itcPercent");
      const itcUnits = numberValue("nItc");
      if (!Number.isInteger(orders) || orders < 2) errors.push("Firm orders must be an integer of at least 2.");
      if (!Number.isInteger(noak) || noak < 0 || noak > orders) errors.push("NOAK unit must be between 0 and firm orders.");
      if (!Number.isInteger(itcUnits) || itcUnits < 0 || itcUnits > orders) errors.push("ITC units cannot exceed firm orders.");
      if (itcPercent === null || itcPercent < 0 || itcPercent > 100) errors.push("ITC must be between 0 and 100%.");
      const validation = $("inputValidation");
      validation.textContent = errors.join(" ");
      validation.classList.toggle("hidden", errors.length === 0);
      return errors.length === 0;
    }

    function updateScenarioInputs() {
      const count = Math.max(1, Math.min(3, Number($("scenarioCount").value || 1)));
      $("scenarioCount").value = count;
      for (let i = 1; i <= 3; i++) {
        const wrapper = $(`occValue${i}`).closest("div");
        wrapper.classList.toggle("hidden", i > count);
        $(`occValue${i}`).disabled = i > count;
      }
    }

    function setWorkflowStep(step) {
      const targetId = workflowStepTarget(step)?.id || "";
      document.querySelectorAll(".workflow-step").forEach(item => {
        const itemStep = Number(item.dataset.step);
        item.classList.toggle("active", itemStep === step);
        item.classList.toggle("done", itemStep < step);
        item.setAttribute("aria-current", itemStep === step ? "step" : "false");
        if (itemStep === 2 && targetId) item.setAttribute("aria-controls", targetId);
      });
    }

    function workflowStepTarget(step) {
      if (step === 1) return $("taskSourcePanel");
      if (step === 2) return $("crtPanel").classList.contains("hidden") ? $("iatPanel") : $("crtPanel");
      return $("runSummary");
    }

    function navigateToWorkflowStep(step) {
      const target = workflowStepTarget(step);
      if (!target) return;
      setWorkflowStep(step);
      target.scrollIntoView({behavior: "smooth", block: "start"});
      window.setTimeout(() => target.focus({preventScroll: true}), 250);
    }

    function setProcessingStage(stage, message) {
      const stageEl = $("processingStage");
      stageEl.dataset.stage = stage;
      stageEl.textContent = message || "";
      stageEl.classList.toggle("hidden", !message);
      stageEl.setAttribute("aria-live", stage === "complete" || stage === "error" ? "polite" : "assertive");
    }

    function updateEmptyState() {
      const states = {
        iat_only: {
          title: "IAT results will appear here",
          description: "Run IAT to see localization adjustments, OCC comparisons, interactive charts, tables, and downloadable output files.",
          terms: ["IAT · International Adjustment Tool", "FOAK · First-of-a-Kind", "NOAK · Nth-of-a-Kind"]
        },
        crt_only: {
          title: "CRT results will appear here",
          description: "Run CRT to see capital cost summaries, reduction levers, construction charts, results tables, and downloadable output files.",
          terms: ["CRT · Cost Reduction Tool", "FOAK · First-of-a-Kind", "NOAK · Nth-of-a-Kind", "Levers · cost-reduction levers"]
        },
        iat_crt: {
          title: "Connected IAT → CRT results will appear here",
          description: "Run the connected workflow to see IAT-adjusted inputs flowing into CRT, followed by summary cards, charts, tables, and downloads.",
          terms: ["IAT · International Adjustment Tool", "CRT · Cost Reduction Tool", "FOAK · First-of-a-Kind", "NOAK · Nth-of-a-Kind", "Levers · cost-reduction levers"]
        }
      }[$("workflow").value];
      if (!states || !$("emptyTitle")) return;
      $("emptyTitle").textContent = states.title;
      $("emptyDescription").textContent = states.description;
      $("termGuide").innerHTML = states.terms.map(term => `<span>${esc(term)}</span>`).join("");
    }

    function updateRunSummary() {
      const workflow = $("workflow").value;
      const workflowLabel = $("workflow").selectedOptions[0]?.textContent || workflow;
      const inputMode = $("iatInputMode").value;
      const source = inputMode === "csv" ? ($("iatCsvName").value || "ACCERT output CSV") : "Standalone OCC scenarios";
      const reactor = workflow === "crt_only" ? $("crtReactorType").value : $("iatReactorType").value;
      const country = inputMode === "csv" || workflow === "iat_crt"
        ? ($("countrySingle").value || "selected country")
        : "selected countries";
      const assumptions = workflow === "iat_only"
        ? `IAT reactor: ${reactor}; country: ${country}`
        : `CRT reactor: ${$("crtReactorType").value}; construction: ${$("constructionDuration").value || "—"} months`;
      $("runSummary").innerHTML = `<strong>Ready to run · ${esc(workflowLabel)}</strong><span>Source: ${esc(source)} · ${esc(assumptions)}</span>`;
    }

    function outputNameParts() {
      const workflow = $("workflow").value;
      const reactor = workflow === "iat_only" ? $("iatReactorType").value : $("crtReactorType").value;
      const country = workflow === "crt_only"
        ? "United States"
        : workflow === "iat_crt"
          ? ($("countrySingle").value || "United States")
          : (selectedCountries()[0] || "United States");
      return {reactor: reactor || "ACCERT", country};
    }

    function updateOutputName() {
      const parts = outputNameParts();
      const generated = `${parts.reactor} ${parts.country} Baseline`;
      const current = $("outputName").value.trim();
      if (!_outputNameCustomized || current === _lastGeneratedOutputName || !current) {
        $("outputName").value = generated;
        _outputNameCustomized = false;
      }
      _lastGeneratedOutputName = generated;
    }

    function enhanceLabels() {
      const helpText = {
        workflow: "Choose whether to run IAT only, CRT only, or pass IAT-adjusted costs into CRT.",
        outputName: "Base filename for CSV and dashboard outputs saved in tutorial/gui_outputs.",
        iatInputMode: "ACCERT CSV uses a COA cost file. Standalone OCC builds a cost structure from the localization shares.",
        iatReactorType: "Large reactor or SMR localization basis. ACCERT output options use the input COA file.",
        country: "Country where localization and adjustment factors are applied.",
        iatCsv: "Input ACCERT/COA CSV. Relative paths are resolved from the ACCERT repository root.",
        iatBaseline: "Built-in ACCERT reference CSV. It selects the associated model and electric output; choose uploaded CSV for a user-generated ACCERT result.",
        scenarioCount: "Standalone IAT scenario count. Choose 1 to 3 OCC scenarios.",
        occValue1: "Scenario 1 U.S.-based OCC input. IAT allocates this OCC to COA accounts using packaged COA breakdown percentages, then applies localization and adjustment factors.",
        occValue2: "Scenario 2 U.S.-based OCC input. IAT allocates this OCC to COA accounts using packaged COA breakdown percentages, then applies localization and adjustment factors.",
        occValue3: "Scenario 3 U.S.-based OCC input. IAT allocates this OCC to COA accounts using packaged COA breakdown percentages, then applies localization and adjustment factors.",
        crtReactorType: "CRT reactor case to run.",
        f22: "Internal CRT parameter f_22. Adds a non-learning factory-equipment allocation to account 22, divided by the number of firm orders. The current reference workbook does not identify a source cell for the default.",
        f2321: "Internal CRT parameter f_2321. Adds a non-learning factory-equipment allocation to account 232.1, divided by the number of firm orders. The current reference workbook does not identify a source cell for the default.",
        crtCsvName: "Optional CSV baseline for CRT. Connected IAT-to-CRT runs fill this automatically.",
        f22: "Factory equipment cost input used by the CRT baseline calculations.",
        f2321: "Turbine-generator equipment cost input used by the CRT baseline calculations.",
        landCost: "Land cost in thousand dollars per acre. The CRT backend receives the value in dollars per acre.",
        startup: "FOAK startup duration in months.",
        constructionDuration: "Reference FOAK construction duration in months. Defaults are AP1000 76, SFR 80, and HTGR 125.",
        total20sLaborHours: "Total labor hours in millions, assigned across 20s direct accounts. The CRT backend receives the full labor-hour value.",
        staggering: "Fractional overlap used for the sequential construction timeline.",
        numOrders: "Number of firm orders: This determines the size of the order book for a given reactor concept. It directly impacts equipment costs for all plants within the order (including the first).",
        numNoak: "NOAK unit: plant number used for the FOAK-to-NOAK comparison. Range: 1 to firm orders.",
        itcPercent: "Investment tax credits (ITC): federal tax credits claimed by the generation owner after project completion. Only ITC is considered because this framework focuses on capital expenses. Range: 0 to 100%.",
        nItc: "Number of plants ITC is applied to: the first few plants in the order book that receive ITC, as chosen by the user. Range: 0 to firm orders.",
        interest: "Interest rate: cost of borrowing money used to finance a project using debt. This percentage may include subsidized low-interest financing. Range: percent value.",
        designCompletion: "Design completion before construction start: percentage of design completed when plant construction begins. Lower completion can cause licensing amendments, rework, delays, and cost increases. Range: 0 to 100%.",
        designMaturity: "Design maturity: 0 means most components are new, 1 means most components are deployed in non-nuclear industry but not nuclear, and 2 means most components have already been deployed in nuclear. Range: 0 to 2.",
        nProc: "Number of plants to achieve best supply-chain proficiency: maximum proficiency is assumed to be reached after this many deployed plants. Report default is 3. Range: 0 to firm orders.",
        procExp: "Supply-chain service proficiency: combines contractor past experience, performance, and methods or technologies used to accomplish tasks. Range: 0 lowest to 2 highest.",
        nCons: "Number of plants to achieve best construction proficiency: maximum proficiency is assumed to be reached after this many deployed plants. Report default is 5. Range: 0 to firm orders.",
        ceExp: "Construction proficiency: proficiency of the construction contractor. Range: 0 lowest to 2 highest, including decimal increments.",
        nAe: "Number of plants to achieve best A/E proficiency: maximum proficiency is assumed to be reached after this many deployed plants. Report default is 4. Range: 0 to firm orders.",
        aeExp: "A/E proficiency: proficiency of the architect/engineering contractor. Range: 0 lowest to 2 highest, including decimal increments.",
        standardization: "Cross-site standardization: percentage of design standardized between sites. Civil works can change due to topography and local natural hazards; higher standardization reduces those changes.",
        modularity: "Modular civil construction: TRUE/FALSE toggle for whether construction uses modular methods such as steel composite walls.",
        bopGrade: "Commercial BOP: TRUE if balance-of-plant can be commercially sourced from non-nuclear vendors; FALSE if safety-related and subject to nuclear qualifications.",
        rbGrade: "Non-safety-related reactor building (RB): TRUE if passive safety features can support classifying the RB as non-safety-related or special treatment instead of safety-related."
      };
      document.querySelectorAll("label[for]").forEach(label => {
        const id = label.getAttribute("for");
        if (!helpText[id] || label.parentElement.classList.contains("label-row")) return;
        const row = document.createElement("div");
        row.className = "label-row";
        label.parentNode.insertBefore(row, label);
        row.appendChild(label);
        const help = document.createElement("span");
        help.className = "help";
        help.textContent = "?";
        help.setAttribute("role", "img");
        help.setAttribute("tabindex", "0");
        help.setAttribute("aria-label", `Help for ${label.textContent.trim()}`);
        help.dataset.tip = esc(helpText[id]);
        help.addEventListener("mousemove", event => showTip(event, help.dataset.tip));
        help.addEventListener("mouseleave", hideTip);
        help.addEventListener("focus", () => {
          const rect = help.getBoundingClientRect();
          showTip({clientX: rect.right, clientY: rect.top}, help.dataset.tip);
        });
        help.addEventListener("blur", hideTip);
        row.appendChild(help);
      });
    }

    function fmt(value) {
      if (value === null || value === undefined || Number.isNaN(Number(value))) return "";
      return Number(value).toLocaleString(undefined, {maximumFractionDigits: 2});
    }

    function fmtInt(value) {
      if (value === null || value === undefined || Number.isNaN(Number(value))) return "";
      return Math.round(Number(value)).toLocaleString();
    }

    function fmtMoneyScale(value) {
      const number = Number(value || 0);
      const abs = Math.abs(number);
      if (abs >= 1e9) return `$${(number / 1e9).toLocaleString(undefined, {maximumFractionDigits: 2})}B`;
      if (abs >= 1e6) return `$${(number / 1e6).toLocaleString(undefined, {maximumFractionDigits: 2})}M`;
      return `$${fmt(number)}`;
    }

    function fmtPerKw(value) {
      return `$${fmt(value)}/kW`;
    }

    function pairValue(gross, net) {
      const grossText = fmtInt(gross);
      const netText = fmtInt(net ?? gross);
      return grossText === netText ? grossText : `${grossText} / ${netText}`;
    }

    function metrics(items, className = "summary") {
      return `<div class="${className}">${items.map(item => `
        <div class="metric"><div class="label">${item.label}</div><div class="value">${item.value}</div>${item.sub ? `<div class="subvalue">${item.sub}</div>` : ""}</div>
      `).join("")}</div>`;
    }

    function table(rows, columns) {
      if (!rows || !rows.length) return "";
      return `<table><thead><tr>${columns.map(c => `<th>${c.label}</th>`).join("")}</tr></thead><tbody>
        ${rows.map(row => `<tr>${columns.map(c => `<td>${c.format ? c.format(row[c.key]) : (row[c.key] ?? "")}</td>`).join("")}</tr>`).join("")}
      </tbody></table>`;
    }

    function coaTable(rows, columns, powerKwe, showToolbar = true) {
      if (!rows || !rows.length) return "";
      const kept = rows.filter(row => !String(row.COA || "").startsWith("6"));
      const ordered = orderCoaRows(kept);
      const toolbar = showToolbar ? `<div class="table-toolbar"><span>Show cost as</span><select class="coaUnit">
        <option value="billion"${coaUnit === "billion" ? " selected" : ""}>Billion USD</option>
        <option value="million"${coaUnit === "million" ? " selected" : ""}>Million USD</option>
        <option value="perkw"${coaUnit === "perkw" ? " selected" : ""}>$/kWe</option>
      </select></div>` : "";
      return `${toolbar}<table class="coa-table"><thead><tr>${columns.map(c => `<th>${c.label}</th>`).join("")}</tr></thead><tbody>
        ${ordered.map(row => {
          const coa = String(row.COA || "");
          const isParent = coa.length === 2 && coa.endsWith("0");
          const parent = `${coa[0]}0`;
          const cls = isParent ? "coa-parent" : `coa-child hidden-row child-of-${parent}`;
          const attrs = isParent ? `data-group="${coa}"` : "";
          return `<tr class="${cls}" ${attrs}>${columns.map(c => `<td>${c.format ? c.format(row[c.key], row, powerKwe) : (row[c.key] ?? "")}</td>`).join("")}</tr>`;
        }).join("")}
      </tbody></table>`;
    }

    function coaSortKey(row) {
      const coa = String(row.COA || "");
      const numeric = Number(coa);
      return Number.isFinite(numeric) ? numeric : Number.MAX_SAFE_INTEGER;
    }

    function orderCoaRows(rows) {
      const parents = rows.filter(row => {
        const coa = String(row.COA || "");
        return coa.length === 2 && coa.endsWith("0");
      }).sort((a, b) => coaSortKey(a) - coaSortKey(b));
      const parentIds = new Set(parents.map(row => String(row.COA || "")));
      const childrenByParent = new Map();
      const standalone = [];
      rows.forEach(row => {
        const coa = String(row.COA || "");
        const parent = `${coa[0]}0`;
        if (parentIds.has(parent) && coa !== parent) {
          if (!childrenByParent.has(parent)) childrenByParent.set(parent, []);
          childrenByParent.get(parent).push(row);
        } else if (!parentIds.has(coa)) {
          standalone.push(row);
        }
      });
      const ordered = [];
      parents.forEach(parent => {
        const coa = String(parent.COA || "");
        ordered.push(parent);
        ordered.push(...(childrenByParent.get(coa) || []).sort((a, b) => coaSortKey(a) - coaSortKey(b)));
      });
      return ordered.concat(standalone.sort((a, b) => coaSortKey(a) - coaSortKey(b)));
    }

    function moneyCell(value, row, powerKwe) {
      const number = Number(value || 0);
      if (coaUnit === "perkw") {
        return powerKwe ? fmtKwe(number / Number(powerKwe)) : "";
      }
      if (coaUnit === "million") {
        return `$${(number / 1e6).toLocaleString(undefined, {maximumFractionDigits: 2})}M`;
      }
      return `$${(number / 1e9).toLocaleString(undefined, {maximumFractionDigits: 3})}B`;
    }

    function iatResultColumns(formatter) {
      return [
        {key: "COA", label: "COA"},
        {key: "Title", label: "Title"},
        {key: "Adjustment Ratio", label: "Ratio", format: fmt},
        {key: "Adjusted Equipment Cost", label: "Adj factory", format: formatter},
        {key: "Adjusted Material Cost", label: "Adj material", format: formatter},
        {key: "Adjusted Labor Cost", label: "Adj labor", format: formatter},
        {key: "Adjusted Total Cost", label: "Adj total", format: formatter}
      ];
    }

    function baseCostColumns(formatter) {
      return [
        {key: "COA", label: "COA"},
        {key: "Title", label: "Title"},
        {key: "Equipment Cost", label: "Factory", format: formatter},
        {key: "Material Cost", label: "Material", format: formatter},
        {key: "Labor Cost", label: "Labor", format: formatter},
        {key: "Total Cost", label: "Total", format: formatter}
      ];
    }

    function baseCaseBlock(baseCase) {
      if (!baseCase || !baseCase.comparison || !baseCase.comparison.length) return "";
      const isStandalone = !baseCase.power_kwe || baseCase.power_kwe === 1.0;
      if (isStandalone) {
        return `<div class="base-case">
          <h3>U.S. Base Case · WE_FOAK (No Levers)</h3>
          <div class="cell-sub">United States baseline (${esc(baseCase.source || "Baseline")}); WE_FOAK with no cost-reduction levers applied. Shown as $/kWe with factory, material, and labor categories included.</div>
          ${coaTable(baseCase.comparison, baseCostColumns(v => fmtKwe(v)), 1.0, false)}
        </div>`;
      }
      const unitLabel = coaUnit === "perkw" ? "$/kWe" : coaUnit === "million" ? "M USD" : "B USD";
      return `<div class="base-case">
        <h3>U.S. Base Case · WE_FOAK (No Levers)</h3>
        <div class="cell-sub">United States baseline (${esc(baseCase.source || "Baseline")}); WE_FOAK with no cost-reduction levers applied. Shown as ${unitLabel} with factory, material, and labor categories included.</div>
        ${coaTable(baseCase.comparison, baseCostColumns((v, row, kwe) => moneyCell(v, row, kwe)), baseCase.power_kwe, true)}
      </div>`;
    }

    function crtResultsColumns() {
      return [
        {key: "Plant number", label: "Plant"},
        {key: "OCC", label: "OCC ($/kW)", format: fmt},
        {key: "TCI", label: "TCI ($/kW)", format: fmt},
        {key: "Construction duration", label: "Construction mo.", format: fmt},
        {key: "Startup duration", label: "Startup mo.", format: fmt},
        {key: "Preconstruction costs", label: "10s", format: fmt},
        {key: "Direct costs", label: "20s", format: fmt},
        {key: "Direct costs: equipment", label: "20s factory", format: fmt},
        {key: "Direct costs: material", label: "20s material", format: fmt},
        {key: "Direct costs: labor", label: "20s labor", format: fmt},
        {key: "Indirect costs", label: "30s", format: fmt},
        {key: "Supplementary costs", label: "50s", format: fmt},
        {key: "Financing costs", label: "60s", format: fmt}
      ];
    }

    function links(files) {
      if (!files) return "";
      return `<div class="links">${Object.entries(files).map(([name, info]) => `<a href="${info.url}" target="_blank">${name}</a>`).join("")}</div>`;
    }

    function fileLink(label, info) {
      return info ? `<div class="links"><a href="${info.url}" target="_blank">${esc(label)}</a></div>` : "";
    }

    function tabSafe(value) {
      return String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "tab";
    }

    function esc(value) {
      return String(value ?? "").replace(/[&<>"']/g, ch => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\"": "&quot;",
        "'": "&#39;"
      }[ch]));
    }

    function showTip(event, html) {
      const tip = $("tooltip");
      tip.innerHTML = html;
      tip.style.display = "block";
      tip.style.left = `${event.clientX + 14}px`;
      tip.style.top = `${event.clientY + 14}px`;
    }

    function hideTip() {
      $("tooltip").style.display = "none";
      $("tooltip").dataset.owner = "";
    }

    function bindTips(root) {
      root.querySelectorAll("[data-tip]").forEach(node => {
        node.addEventListener("mousemove", event => showTip(event, node.dataset.tip));
        node.addEventListener("mouseleave", hideTip);
        if (node.matches("button, [tabindex]")) {
          const showFromFocus = () => {
            const rect = node.getBoundingClientRect();
            showTip({clientX: rect.right, clientY: rect.top}, node.dataset.tip);
            $("tooltip").dataset.owner = node.dataset.tip;
          };
          node.addEventListener("focus", showFromFocus);
          node.addEventListener("blur", hideTip);
          node.addEventListener("click", event => {
            event.stopPropagation();
            if ($("tooltip").dataset.owner === node.dataset.tip && $("tooltip").style.display === "block") hideTip();
            else showFromFocus();
          });
        }
      });
    }

    function niceMax(value) {
      if (!value || value <= 0) return 1;
      const pow = Math.pow(10, Math.floor(Math.log10(value)));
      return Math.ceil(value / pow) * pow;
    }

    function capitalChart(rows) {
      if (!rows || !rows.length) return "";
      const w = 1120, h = 430;
      const m = {left: 108, right: 28, top: 58, bottom: 66};
      const innerW = w - m.left - m.right;
      const innerH = h - m.top - m.bottom;
      const tciValue = row => Number(row.TCI || 0);
      const nciValue = row => Number(row.NCI ?? row.TCI ?? 0);
      const occValue = row => Number(row.OCC || 0);
      const netOccValue = row => Number(row["Net OCC"] ?? row.OCC ?? 0);
      const max = niceMax(Math.max(...rows.flatMap(r => [tciValue(r), occValue(r)])) * 1.08);
      const y = v => m.top + innerH - (Number(v || 0) / max) * innerH;
      const groupW = innerW / rows.length;
      const barW = Math.max(14, Math.min(34, groupW * 0.28));
      let svg = `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="TCI by plant with NCI and ITC reduction"><defs><pattern id="itcHatch" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(35)"><line x1="0" y1="0" x2="0" y2="8" stroke="#2ca02c" stroke-width="3" opacity="0.7"></line></pattern></defs>`;
      for (let i = 0; i <= 4; i++) {
        const value = max * i / 4;
        const yy = y(value);
        svg += `<line class="grid" x1="${m.left}" y1="${yy}" x2="${w - m.right}" y2="${yy}"></line>`;
        svg += `<text x="${m.left - 10}" y="${yy + 5}" text-anchor="end" fill="#596775" font-size="15" font-weight="700">${fmt(value)}</text>`;
      }
      svg += `<line x1="${m.left}" y1="${m.top}" x2="${m.left}" y2="${m.top + innerH}" stroke="#8896a7"></line>`;
      svg += `<line x1="${m.left}" y1="${m.top + innerH}" x2="${w - m.right}" y2="${m.top + innerH}" stroke="#8896a7"></line>`;
      svg += `<text transform="translate(18,${m.top + innerH / 2}) rotate(-90)" text-anchor="middle" fill="#596775" font-size="15" font-weight="700">Cost ($/kW)</text>`;
      rows.forEach((r, idx) => {
        const cx = m.left + groupW * idx + groupW / 2;
        const tci = tciValue(r);
        const netTci = nciValue(r);
        const tciReduction = Math.max(0, Number(r["TCI ITC reduction"] ?? (tci - netTci)));
        const nci = Math.min(tci, netTci);
        const itc = Math.min(tci - nci, tciReduction);
        const occ = occValue(r);
        const netOccValueActual = netOccValue(r);
        const occReduction = Math.max(0, Number(r["OCC ITC reduction"] ?? (occ - netOccValueActual)));
        const netOcc = Math.min(occ, netOccValueActual);
        const occItc = Math.min(occ - netOcc, occReduction);
        const solidH = m.top + innerH - y(nci);
        const itcH = y(nci) - y(tci);
        const occSolidH = m.top + innerH - y(netOcc);
        const occItcH = y(netOcc) - y(occ);
        const tciTip = tciReduction > 0
          ? `<b>Plant ${esc(r["Plant number"])}</b><br><span class='tip-label'>TCI / Net TCI ($/kW)</span><span class='tip-value'>${fmt(tci)} / ${fmt(netTci)}</span><span class='tip-label'>ITC Reduction ($/kW)</span><span class='tip-value'>${fmt(tciReduction)}</span>`
          : `<b>Plant ${esc(r["Plant number"])}</b><br><span class='tip-label'>TCI ($/kW)</span><span class='tip-value'>${fmt(tci)}</span>`;
        const occTip = occReduction > 0
          ? `<b>Plant ${esc(r["Plant number"])}</b><br><span class='tip-label'>OCC / Net OCC ($/kW)</span><span class='tip-value'>${fmt(occ)} / ${fmt(netOccValueActual)}</span><span class='tip-label'>ITC Reduction ($/kW)</span><span class='tip-value'>${fmt(occReduction)}</span>`
          : `<b>Plant ${esc(r["Plant number"])}</b><br><span class='tip-label'>OCC ($/kW)</span><span class='tip-value'>${fmt(occ)}</span>`;
        svg += `<rect class="hoverable" data-tip="${tciTip}" x="${cx - barW - 2}" y="${y(nci)}" width="${barW}" height="${solidH}" fill="#2ca02c" stroke="#2ca02c" stroke-width="1.5"></rect>`;
        if (itc > 0) svg += `<rect class="hoverable" data-tip="${tciTip}" x="${cx - barW - 2}" y="${y(tci)}" width="${barW}" height="${itcH}" fill="url(#itcHatch)" stroke="#2ca02c" stroke-width="1.5"></rect>`;
        svg += `<rect class="hoverable" data-tip="${occTip}" x="${cx + 2}" y="${y(netOcc)}" width="${barW}" height="${occSolidH}" fill="#1f77b4" stroke="#1f77b4" stroke-width="1.5"></rect>`;
        if (occItc > 0) svg += `<rect class="hoverable" data-tip="${occTip}" x="${cx + 2}" y="${y(occ)}" width="${barW}" height="${occItcH}" fill="url(#itcHatch)" stroke="#1f77b4" stroke-width="1.5"></rect>`;
        if (idx % Math.ceil(rows.length / 8) === 0 || rows.length <= 8) {
          svg += `<text x="${cx}" y="${h - 28}" text-anchor="middle" fill="#596775" font-size="15" font-weight="700">${esc(r["Plant number"])}</text>`;
        }
      });
      svg += `<text x="${m.left + innerW / 2}" y="${h - 6}" text-anchor="middle" fill="#596775" font-size="15" font-weight="700">Plant number</text>`;
      svg += `<rect x="${m.left}" y="20" width="14" height="14" fill="#2ca02c" stroke="#2ca02c" stroke-width="1.5"></rect><text x="${m.left + 22}" y="32" fill="#596775" font-size="15" font-weight="700">TCI / Net TCI</text>`;
      svg += `<rect x="${m.left + 160}" y="20" width="14" height="14" fill="#1f77b4" stroke="#1f77b4" stroke-width="1.5"></rect><text x="${m.left + 182}" y="32" fill="#596775" font-size="15" font-weight="700">OCC / Net OCC</text>`;
      if (rows.some(r => Number(r["TCI ITC reduction"] || 0) > 0 || Number(r["OCC ITC reduction"] || 0) > 0)) {
        svg += `<rect x="${m.left + 360}" y="20" width="14" height="14" fill="url(#itcHatch)" stroke="#2ca02c" stroke-width="1.5"></rect><text x="${m.left + 382}" y="32" fill="#596775" font-size="15" font-weight="700">ITC reduction</text>`;
      }
      svg += `</svg>`;
      return svg;
    }

    function waterfallChart(rows) {
      if (!rows || !rows.length) return "";
      const w = 1120, h = 460;
      const m = {left: 108, right: 28, top: 34, bottom: 112};
      const innerW = w - m.left - m.right;
      const innerH = h - m.top - m.bottom;
      const max = niceMax(Math.max(...rows.map(r => Number(r.cumulative_tci || 0))) * 1.08);
      const y = v => m.top + innerH - (Number(v || 0) / max) * innerH;
      const step = innerW / rows.length;
      const bw = Math.max(24, Math.min(58, step * 0.62));
      let previous = 0;
      let svg = `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="TCI waterfall savings by lever">`;
      for (let i = 0; i <= 4; i++) {
        const value = max * i / 4;
        const yy = y(value);
        svg += `<line class="grid" x1="${m.left}" y1="${yy}" x2="${w - m.right}" y2="${yy}"></line>`;
        svg += `<text x="${m.left - 10}" y="${yy + 5}" text-anchor="end" fill="#596775" font-size="15" font-weight="700">${fmt(value)}</text>`;
      }
      svg += `<line x1="${m.left}" y1="${m.top + innerH}" x2="${w - m.right}" y2="${m.top + innerH}" stroke="#8896a7"></line>`;
      svg += `<text transform="translate(18,${m.top + innerH / 2}) rotate(-90)" text-anchor="middle" fill="#596775" font-size="15" font-weight="700">TCI ($/kW)</text>`;
      rows.forEach((r, idx) => {
        const cumulative = Number(r.cumulative_tci || 0);
        const change = Number(r.absolute_change || 0);
        const isTotal = r.kind === "total";
        const start = isTotal ? 0 : previous;
        const top = Math.min(start, cumulative);
        const bottom = Math.max(start, cumulative);
        const x = m.left + step * idx + (step - bw) / 2;
        const barY = y(bottom);
        const barH = Math.max(1, y(top) - y(bottom));
        const color = isTotal ? "#1f77b4" : (change <= 0 ? "#2ca02c" : "#ff7f0e");
        const pct = rows[0]?.cumulative_tci ? (change / Number(rows[0].cumulative_tci) * 100) : 0;
        svg += `<rect class="hoverable" data-tip="<b>${esc(r.label)}</b><br>Change: ${fmt(change)} (${fmt(pct)}%)<br>Cumulative TCI: ${fmt(cumulative)}" x="${x}" y="${barY}" width="${bw}" height="${barH}" fill="${color}"></rect>`;
        if (!isTotal) {
          svg += `<line x1="${x - step * 0.18}" y1="${y(start)}" x2="${x}" y2="${y(start)}" stroke="#aeb8c4" stroke-dasharray="3 3"></line>`;
        }
        const label = String(r.label || "").replace(/\n/g, " ");
        svg += `<text transform="translate(${x + bw / 2},${h - 96}) rotate(52)" text-anchor="start" fill="#596775" font-size="13" font-weight="700">${esc(label.slice(0, 28))}</text>`;
        if (!isTotal && Math.abs(pct) > 0.05) {
          svg += `<text x="${x + bw / 2}" y="${barY - 8}" text-anchor="middle" fill="#596775" font-size="13" font-weight="800">${fmt(pct)}%</text>`;
        }
        previous = cumulative;
      });
      svg += `</svg>`;
      return svg;
    }

    function breakdownChart(rows, mode = "tci") {
      if (!rows || !rows.length) return "";
      const keys = mode === "occ"
        ? [
            ["Preconstruction costs", "10 - Preconstruction", "#4e79a7"],
            ["Direct costs: equipment", "20 - Direct: Equipment", "#76b7b2"],
            ["Direct costs: material", "20 - Direct: Material", "#f28e2b"],
            ["Direct costs: labor", "20 - Direct: Labor", "#e15759"],
            ["Indirect costs", "30 - Indirect", "#59a14f"],
            ["Supplementary costs", "50 - Supplementary", "#b07aa1"]
          ]
        : [
            ["Preconstruction costs", "10 - Preconstruction", "#4e79a7"],
            ["Direct costs", "20 - Direct", "#59a14f"],
            ["Indirect costs", "30 - Indirect", "#f28e2b"],
            ["Supplementary costs", "50 - Supplementary", "#b07aa1"],
            ["Financing costs", "60 - Financing", "#e15759"]
          ];
      const w = 1120, h = 430;
      const m = {left: 108, right: 28, top: 30, bottom: 78};
      const innerW = w - m.left - m.right;
      const innerH = h - m.top - m.bottom;
      const max = niceMax(Math.max(...rows.map(r => keys.reduce((sum, [k]) => sum + Number(r[k] || 0), 0))) * 1.08);
      const y = v => m.top + innerH - (Number(v || 0) / max) * innerH;
      const step = innerW / rows.length;
      const bw = Math.max(18, Math.min(50, step * 0.62));
      let svg = `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${mode.toUpperCase()} cost breakdown by plant">`;
      for (let i = 0; i <= 4; i++) {
        const value = max * i / 4;
        const yy = y(value);
        svg += `<line class="grid" x1="${m.left}" y1="${yy}" x2="${w - m.right}" y2="${yy}"></line>`;
        svg += `<text x="${m.left - 10}" y="${yy + 5}" text-anchor="end" fill="#596775" font-size="15" font-weight="700">${fmt(value)}</text>`;
      }
      svg += `<line x1="${m.left}" y1="${m.top + innerH}" x2="${w - m.right}" y2="${m.top + innerH}" stroke="#8896a7"></line>`;
      svg += `<text transform="translate(18,${m.top + innerH / 2}) rotate(-90)" text-anchor="middle" fill="#596775" font-size="15" font-weight="700">${mode.toUpperCase()} ($/kW)</text>`;
      rows.forEach((r, idx) => {
        const x = m.left + step * idx + (step - bw) / 2;
        let total = 0;
        keys.forEach(([key, label, color]) => {
          const value = Number(r[key] || 0);
          const y0 = y(total);
          total += value;
          const y1 = y(total);
          svg += `<rect class="hoverable" data-tip="<b>Plant ${esc(r["Plant number"])}</b><br>${esc(label)}: ${fmt(value)}<br>Total: ${fmt(total)}" x="${x}" y="${y1}" width="${bw}" height="${Math.max(0.5, y0 - y1)}" fill="${color}"></rect>`;
        });
        if (idx % Math.ceil(rows.length / 8) === 0 || rows.length <= 8) {
          svg += `<text x="${x + bw / 2}" y="${h - 44}" text-anchor="middle" fill="#596775" font-size="15" font-weight="700">${esc(r["Plant number"])}</text>`;
        }
      });
      keys.slice(0, 5).forEach(([key, label, color], idx) => {
        const x = m.left + idx * 190;
        svg += `<rect x="${x}" y="${h - 22}" width="13" height="13" fill="${color}"></rect><text x="${x + 20}" y="${h - 11}" fill="#596775" font-size="13" font-weight="700">${esc(label.replace("20 - Direct: ", ""))}</text>`;
      });
      svg += `</svg>`;
      return svg;
    }

    function durationChart(rows) {
      if (!rows || !rows.length) return "";
      const w = 1120, h = 430;
      const m = {left: 108, right: 28, top: 34, bottom: 66};
      const innerW = w - m.left - m.right;
      const innerH = h - m.top - m.bottom;
      const max = niceMax(Math.max(...rows.map(r => Number(r["Construction duration"] || 0) + Number(r["Startup duration"] || 0))) * 1.08);
      const y = v => m.top + innerH - (Number(v || 0) / max) * innerH;
      const step = innerW / rows.length;
      const bw = Math.max(18, Math.min(52, step * 0.62));
      let svg = `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="Construction and startup durations">`;
      for (let i = 0; i <= 4; i++) {
        const value = max * i / 4;
        const yy = y(value);
        svg += `<line class="grid" stroke="#c7d4e2" x1="${m.left}" y1="${yy}" x2="${w - m.right}" y2="${yy}"></line>`;
        svg += `<text x="${m.left - 10}" y="${yy + 5}" text-anchor="end" fill="#596775" font-size="15" font-weight="700">${fmt(value)}</text>`;
      }
      rows.forEach((r, idx) => {
        const xx = m.left + step * idx + step / 2;
        svg += `<line stroke="#edf2f7" x1="${xx}" y1="${m.top}" x2="${xx}" y2="${m.top + innerH}"></line>`;
      });
      svg += `<line x1="${m.left}" y1="${m.top + innerH}" x2="${w - m.right}" y2="${m.top + innerH}" stroke="#8896a7"></line>`;
      svg += `<text transform="translate(18,${m.top + innerH / 2}) rotate(-90)" text-anchor="middle" fill="#596775" font-size="15" font-weight="700">Duration (months)</text>`;
      rows.forEach((r, idx) => {
        const x = m.left + step * idx + (step - bw) / 2;
        const construction = Number(r["Construction duration"] || 0);
        const startup = Number(r["Startup duration"] || 0);
        const y0 = y(construction);
        svg += `<rect class="hoverable" data-tip="<b>Plant ${esc(r["Plant number"])}</b><br>Construction: ${fmt(construction)} months" x="${x}" y="${y0}" width="${bw}" height="${m.top + innerH - y0}" fill="#ff7f0e"></rect>`;
        svg += `<rect class="hoverable" data-tip="<b>Plant ${esc(r["Plant number"])}</b><br>Startup: ${fmt(startup)} months<br>Total: ${fmt(construction + startup)} months" x="${x}" y="${y(construction + startup)}" width="${bw}" height="${y0 - y(construction + startup)}" fill="#9467bd"></rect>`;
        if (idx % Math.ceil(rows.length / 8) === 0 || rows.length <= 8) {
          svg += `<text x="${x + bw / 2}" y="${h - 28}" text-anchor="middle" fill="#596775" font-size="15" font-weight="700">${esc(r["Plant number"])}</text>`;
        }
      });
      svg += `<rect x="${w - 202}" y="14" width="14" height="14" fill="#ff7f0e"></rect><text x="${w - 180}" y="26" fill="#596775" font-size="15" font-weight="700">Construction</text>`;
      svg += `<rect x="${w - 86}" y="14" width="14" height="14" fill="#9467bd"></rect><text x="${w - 64}" y="26" fill="#596775" font-size="15" font-weight="700">Startup</text>`;
      svg += `</svg>`;
      return svg;
    }

    function timelineChart(rows) {
      if (!rows || !rows.length) return "";
      const w = 1120, h = 430;
      const m = {left: 108, right: 28, top: 34, bottom: 66};
      const innerW = w - m.left - m.right;
      const innerH = h - m.top - m.bottom;
      const max = Math.max(1, Math.ceil(Math.max(...rows.map(r => Number(r.startup_end_year || 0))) * 1.05));
      const x = v => m.left + (Number(v || 0) / max) * innerW;
      const rowH = innerH / rows.length;
      let svg = `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="Sequential construction timeline">`;
      const tickStep = Math.max(1, Math.ceil(max / 6));
      for (let value = 0; value <= max; value += tickStep) {
        const xx = x(value);
        svg += `<line class="grid" stroke="#c7d4e2" x1="${xx}" y1="${m.top}" x2="${xx}" y2="${m.top + innerH}"></line>`;
        svg += `<text x="${xx}" y="${h - 28}" text-anchor="middle" fill="#596775" font-size="15" font-weight="700">${value}</text>`;
      }
      rows.forEach((r, idx) => {
        const y = m.top + idx * rowH + rowH * 0.2;
        const bh = Math.max(6, rowH * 0.6);
        const rowMid = m.top + idx * rowH + rowH / 2;
        svg += `<line stroke="#edf2f7" x1="${m.left}" y1="${rowMid}" x2="${w - m.right}" y2="${rowMid}"></line>`;
        const cs = x(r.construction_start_year);
        const ce = x(r.construction_end_year);
        const se = x(r.startup_end_year);
        svg += `<text x="${m.left - 14}" y="${y + bh * 0.7}" text-anchor="end" fill="#596775" font-size="15" font-weight="700">${esc(r.plant)}</text>`;
        svg += `<rect class="hoverable" data-tip="<b>Plant ${esc(r.plant)}</b><br>Construction: ${fmt(r.construction_start_year)}-${fmt(r.construction_end_year)} years" x="${cs}" y="${y}" width="${Math.max(1, ce - cs)}" height="${bh}" fill="#ff7f0e" stroke="#333"></rect>`;
        svg += `<rect class="hoverable" data-tip="<b>Plant ${esc(r.plant)}</b><br>Startup end: ${fmt(r.startup_end_year)} years" x="${ce}" y="${y}" width="${Math.max(1, se - ce)}" height="${bh}" fill="#9467bd" stroke="#333"></rect>`;
      });
      svg += `<text transform="translate(18,${m.top + innerH / 2}) rotate(-90)" text-anchor="middle" fill="#596775" font-size="15" font-weight="700">Reactor number</text>`;
      svg += `<text x="${m.left + innerW / 2}" y="${h - 6}" text-anchor="middle" fill="#596775" font-size="15" font-weight="700">Time (years)</text>`;
      svg += `</svg>`;
      return svg;
    }

    function setupTabs() {
      document.querySelectorAll(".tabs button").forEach(button => {
        button.addEventListener("click", () => {
          const tab = button.dataset.tab;
          document.querySelectorAll(".tabs button").forEach(b => b.classList.toggle("active", b === button));
          document.querySelectorAll(".tab-panel").forEach(panel => panel.classList.toggle("active", panel.id === `tab-${tab}`));
        });
      });
    }

    function setupCoaTables() {
      document.querySelectorAll(".coa-parent").forEach(row => {
        row.addEventListener("click", () => {
          const group = row.dataset.group;
          row.classList.toggle("expanded");
          document.querySelectorAll(`.child-of-${group}`).forEach(child => child.classList.toggle("hidden-row"));
        });
      });
    }

    function fmtKwe(value) {
      return value != null ? `$${fmtInt(value)}/kWe` : "";
    }

    function iatSummaryCards(iat) {
      return `<div class="iat-country">Selected country: <strong>${esc(displayCountryName(iat.country || "Selected country"))}</strong></div><div class="summary iat-summary-cards">
        <div class="metric"><div class="label">Original OCC</div><div class="value">${fmtKwe(iat.input_occ_per_kw)}</div><div class="subvalue">Original ACCERT cost</div></div>
        <div class="metric"><div class="label">IAT-adjusted OCC</div><div class="value">${fmtKwe(iat.adjusted_occ_per_kw)}</div><div class="subvalue">${esc(displayCountryName(iat.country || "Selected country"))}</div></div>
        <div class="metric"><div class="label">OCC Change</div><div class="value">${fmt((Number(iat.adjustment_ratio || 1) - 1) * 100)}%</div><div class="subvalue">Change from original</div></div>
      </div>`;
    }

    function iatBreakdown(iat) {
      const breakdown = iat.breakdown || {};
      const value = name => fmtKwe(breakdown[`${name}_per_kw`]);
      return `<div class="iat-breakdown"><div class="breakdown-label">Adjusted OCC cost breakdown</div><div class="breakdown-items"><span>Material <strong>${value("material")}</strong></span><span>Factory <strong>${value("factory")}</strong></span><span>Labor <strong>${value("labor")}</strong></span><span>Other OCC (land + catch-all) <strong>${value("other")}</strong></span></div><div class="cell-sub">Categories are additive and reconcile to Adjusted OCC.</div></div>`;
    }

    function iatOnlyCountrySummary(iat) {
      const country = displayCountryName(iat.country || "Selected country");
      const change = (Number(iat.adjustment_ratio || 1) - 1) * 100;
      return `<div class="iat-only-summary">
        <div class="metric"><div class="label">Original OCC</div><div class="value">${fmtKwe(iat.input_occ_per_kw)}</div><div class="subvalue">Base Case entering IAT</div></div>
        <div class="metric metric-emphasis"><div class="label">Adjusted OCC</div><div class="value">${fmtKwe(iat.adjusted_occ_per_kw)}</div><div class="subvalue">${esc(country)} result after IAT</div></div>
        <div class="metric"><div class="label">OCC adjustment</div><div class="value">${fmt(change)}%</div><div class="subvalue">Change from Original OCC</div></div>
        <div class="metric"><div class="label">Country</div><div class="value">${esc(country)}</div><div class="subvalue">Selected IAT location</div></div>
      </div>
      ${iatBreakdown(iat)}`;
    }

    function iatScenarioTable(rows) {
      if (!rows || !rows.length) return "";
      return `<div class="iat-scenario-note"><strong>Scenario input and adjusted result</strong><br>Base Case is the original OCC entering IAT. Adjusted OCC is the country-adjusted result used for this scenario.</div><table class="iat-scenario-table"><thead><tr><th>Scenario</th><th>Input OCC ($/kWe)</th><th>Adjusted OCC ($/kWe)</th><th>OCC Ratio</th></tr></thead><tbody>${rows.map(row => `<tr><td>${esc(row.Scenario || "")}</td><td>${fmt(row["Input OCC"])}</td><td class="iat-adjusted-occ">${fmt(row["Adjusted OCC"])}</td><td>${fmt(row["Adjustment Ratio of OCC"])}</td></tr>`).join("")}</tbody></table>`;
    }

    function crtKeySummaryCards(crt) {
      return `<div class="summary crt-key-cards">
        <div class="metric"><div class="label">FOAK OCC / Net OCC ($/kW)</div><div class="value">${fmtPerKw(crt.occ_1)} / ${fmtPerKw(crt.net_occ_1 ?? crt.occ_1)}</div><div class="subvalue">Gross / Net</div></div>
        <div class="metric"><div class="label">FOAK TCI / Net TCI ($/kW)</div><div class="value">${fmtPerKw(crt.tci_1)} / ${fmtPerKw(crt.net_tci_1 ?? crt.tci_1)}</div><div class="subvalue">Gross / Net</div></div>
      </div>`;
    }

    function crtGridValue(gross, net, reduction) {
      const grossValue = Number(gross);
      const netValue = Number(net ?? gross);
      return reduction > 0 && Math.abs(grossValue - netValue) > 0.005
        ? `${fmtInt(grossValue)} / ${fmtInt(netValue)}`
        : fmtInt(grossValue);
    }

    function infoIcon(label, explanation) {
      return `<button type="button" class="help info-tip" aria-label="Explain ${esc(label)}" data-tip="${esc(explanation)}">?</button>`;
    }

    function crtMetricGroup(title, explanation, cards, reductionLabel = "", reductionValue = "") {
      return `<div class="crt-metric-group"><h4 class="crt-metric-heading">${title} ${infoIcon(title, explanation)}</h4><div class="crt-metric-cards">${cards.map(card => `<div class="metric"><div class="label">${card.label}</div><div class="value">${card.value}</div>${card.sub ? `<div class="subvalue">${card.sub}</div>` : ""}</div>`).join("")}</div>${reductionLabel ? `<div class="crt-metric-reduction">${reductionLabel}: <strong>${reductionValue || "—"}</strong></div>` : ""}</div>`;
    }

    function crtResultsGrid(crt) {
      const plants = crt.plants || [];
      const plant = number => plants.find(row => Number(row["Plant number"]) === number) || {};
      const foak = plant(1);
      const noak = plant(Number(crt.num_noak));
      const reduction = (row, key) => Number(row[key] || 0);
      const foakOccNet = crt.net_occ_1 ?? foak["Net OCC"];
      const noakOccNet = crt.net_occ_noak ?? noak["Net OCC"];
      const foakTciNet = crt.net_tci_1 ?? foak.NCI;
      const noakTciNet = crt.net_tci_noak ?? noak.NCI;
      const foakOccReduction = Math.max(0, Number(foak.OCC) - Number(foakOccNet));
      const noakOccReduction = Math.max(0, Number(noak.OCC) - Number(noakOccNet));
      const foakTciReduction = Math.max(0, Number(foak.TCI) - Number(foakTciNet));
      const noakTciReduction = Math.max(0, Number(noak.TCI) - Number(noakTciNet));
      const averageNet = (netKey, grossKey, fallback) => {
        const values = plants.map(row => Number(row[netKey] ?? row[grossKey])).filter(Number.isFinite);
        return values.length ? values.reduce((sum, item) => sum + item, 0) / values.length : Number(fallback);
      };
      const avgOccNet = averageNet("Net OCC", "OCC", crt.avg_occ);
      const avgTciNet = averageNet("NCI", "TCI", crt.avg_tci);
      const avgOccReduction = Math.max(0, Number(crt.avg_occ) - avgOccNet);
      const avgTciReduction = Math.max(0, Number(crt.avg_tci) - avgTciNet);
      const value = (gross, net, reductionValue) => crtGridValue(gross, net, reductionValue);
      return `<div class="crt-results-summary">
        ${crtMetricGroup("Overnight Capital Cost (OCC)", "Overnight Capital Cost (OCC) represents the estimated capital cost of constructing the plant as if it were built overnight, excluding financing costs incurred during construction.", [
          {label: foakOccReduction > 0 ? "FOAK OCC / Net OCC" : "FOAK OCC", value: `${value(foak.OCC, foakOccNet, foakOccReduction)} $/kWe`, sub: foakOccReduction > 0 ? "Gross / Net" : ""},
          {label: noakOccReduction > 0 ? "NOAK OCC / Net OCC" : "NOAK OCC", value: `${value(noak.OCC, noakOccNet, noakOccReduction)} $/kWe`, sub: noakOccReduction > 0 ? "Gross / Net" : ""},
          {label: avgOccReduction > 0 ? "Average OCC / Net OCC" : "Average OCC", value: `${value(crt.avg_occ, avgOccNet, avgOccReduction)} $/kWe`, sub: avgOccReduction > 0 ? "Gross / Net" : ""}
        ], "Learning reduction", `${fmt(crt.occ_reduction_percent)}%`)}
        ${crtMetricGroup("Total Capital Investment (TCI)", "Total Capital Investment (TCI) includes the model's Overnight Capital Cost plus 60-series financing costs, including interest during construction, as defined in the CRT model.", [
          {label: foakTciReduction > 0 ? "FOAK TCI / NCI" : "FOAK TCI", value: `${value(foak.TCI, foakTciNet, foakTciReduction)} $/kWe`, sub: foakTciReduction > 0 ? "Gross / Net" : ""},
          {label: noakTciReduction > 0 ? "NOAK TCI / NCI" : "NOAK TCI", value: `${value(noak.TCI, noakTciNet, noakTciReduction)} $/kWe`, sub: noakTciReduction > 0 ? "Gross / Net" : ""},
          {label: avgTciReduction > 0 ? "Average TCI / NCI" : "Average TCI", value: `${value(crt.avg_tci, avgTciNet, avgTciReduction)} $/kWe`, sub: avgTciReduction > 0 ? "Gross / Net" : ""}
        ], "Learning reduction", `${fmt(crt.tci_reduction_percent)}%`)}
        ${crtMetricGroup("Construction Duration", "Construction duration is the modeled time to build each unit; startup duration is reported separately in the detailed results.", [
          {label: "FOAK", value: `${fmtInt(foak["Construction duration"])} months`},
          {label: "NOAK", value: `${fmtInt(noak["Construction duration"])} months`},
          {label: "Average", value: `${fmtInt(crt.avg_duration)} months`}
        ])}
      </div>`;
    }

    function iatBlock(iat, title = "", includeMetrics = true) {
      let html = title ? `<div class="scenario-card"><h4>${title}</h4>` : "";
      if (includeMetrics) {
        html += iatOnlyCountrySummary(iat);
      }
      const isStandalone = !iat.power_kwe || iat.power_kwe === 1.0;
      if (isStandalone) {
        html += coaTable(iat.comparison, iatResultColumns(v => fmtKwe(v)), 1.0, false);
      } else {
        const unitLabel = coaUnit === "perkw" ? "$/kWe" : coaUnit === "million" ? "M USD" : "B USD";
        html += `<div class="cell-sub">Adjusted COA cost columns shown as ${unitLabel}; original values are shown in the Base Case section.</div>`;
        html += coaTable(iat.comparison, iatResultColumns((v, row, kwe) => moneyCell(v, row, kwe)), iat.power_kwe, true);
      }
      return title ? `${html}</div>` : html;
    }

    const IAT_COUNTRY_COLORS = [
      "#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd", "#d62728", "#17becf",
      "#8c564b", "#e377c2", "#bcbd22", "#4e79a7", "#59a14f", "#f28e2b"
    ];

    function iatCountryColor(country, index) {
      const known = {
        "United States": "#1f77b4", "China": "#ff7f0e", "South Korea": "#2ca02c", "Korea": "#2ca02c",
        "UAE": "#9467bd", "Poland": "#d62728", "El Salvador": "#17becf",
        "Thailand": "#8c564b", "Vietnam": "#e377c2", "Indonesia": "#bcbd22"
      };
      if (known[country]) return known[country];
      let hash = 0;
      for (const char of String(country || "")) hash = ((hash << 5) - hash + char.charCodeAt(0)) | 0;
      return IAT_COUNTRY_COLORS[Math.abs(hash) % IAT_COUNTRY_COLORS.length];
    }

    function finalCountryComparisonRows(rows) {
      return (rows || []).map(row => {
        const adjusted = Number(row.adjusted_occ_per_kw || 0);
        const isUnitedStates = String(row.country || "").trim() === "United States";
        return {
          ...row,
          reference_case: isUnitedStates,
          display_local_per_kw: isUnitedStates ? adjusted : Number(row.local_per_kw || 0),
          display_foreign_per_kw: isUnitedStates ? 0 : Number(row.foreign_per_kw || 0)
        };
      });
    }

    function countryComparisonChart(rows) {
      if (!rows || !rows.length) return "";
      const finalRows = finalCountryComparisonRows(rows);
      // The backend emits rows in selected-country then scenario input order.
      // Keep that order: scenario identifiers, never cost values, determine x-position.
      const countries = [...new Set(finalRows.map(r => r.country))];
      const groups = countries.map(country => ({
        country,
        rows: finalRows.filter(row => row.country === country)
      }));
      const w = 1120, h = 520;
      const m = {left: 108, right: 28, top: 76, bottom: 106};
      const innerW = w - m.left - m.right;
      const innerH = h - m.top - m.bottom;
      const maxVal = Math.max(1, ...finalRows.map(r => Number(r.adjusted_occ_per_kw || 0))) * 1.12;
      const yScale = v => m.top + innerH - (Number(v || 0) / maxVal) * innerH;
      const step = innerW / countries.length;
      const tolerance = 0.01;
      let svg = `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="Adjusted OCC by country and scenario"><defs>`;
      groups.forEach(group => {
        const color = iatCountryColor(group.country, countries.indexOf(group.country));
        const patternId = `iatForeignHatch-${tabSafe(group.country)}`;
        svg += `<pattern id="${patternId}" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(35)"><line x1="0" y1="0" x2="0" y2="8" stroke="${color}" stroke-width="3" opacity="0.75"></line></pattern>`;
      });
      svg += `<pattern id="iatForeignLegendHatch" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(35)"><line x1="0" y1="0" x2="0" y2="8" stroke="#64748b" stroke-width="3" opacity="0.75"></line></pattern></defs>`;
      svg += `<text x="${m.left}" y="24" fill="#596775" font-size="13" font-weight="800">Color: Country</text>`;
      const colorLegendColumns = Math.min(3, countries.length);
      const colorLegendWidth = innerW / Math.max(1, colorLegendColumns);
      countries.forEach((country, idx) => {
        const col = idx % colorLegendColumns;
        const row = Math.floor(idx / colorLegendColumns);
        const lx = m.left + 112 + col * colorLegendWidth;
        const ly = 24 + row * 20;
        const color = iatCountryColor(country, idx);
        svg += `<rect x="${lx}" y="${ly - 11}" width="12" height="12" fill="${color}" rx="2"></rect><text x="${lx + 19}" y="${ly}" fill="#596775" font-size="13" font-weight="700">${esc(displayCountryName(country))}</text>`;
      });
      for (let i = 0; i <= 4; i++) {
        const v = maxVal * i / 4;
        const yy = yScale(v);
        svg += `<line stroke="#d5e0ea" x1="${m.left}" y1="${yy}" x2="${w - m.right}" y2="${yy}"></line>`;
        svg += `<text x="${m.left - 10}" y="${yy + 5}" text-anchor="end" fill="#41566d" font-size="15" font-weight="700">${fmt(Math.round(v))}</text>`;
      }
      svg += `<line x1="${m.left}" y1="${m.top + innerH}" x2="${w - m.right}" y2="${m.top + innerH}" stroke="#8093a7"></line>`;
      svg += `<text transform="translate(18,${m.top + innerH / 2}) rotate(-90)" text-anchor="middle" fill="#41566d" font-size="15" font-weight="700">Adjusted OCC ($/kWe)</text>`;
      groups.forEach((group, groupIndex) => {
        const country = group.country;
        const countryLabel = displayCountryName(country);
        const color = iatCountryColor(country, groupIndex);
        const groupStep = step / (group.rows.length + 1);
        const barW = Math.max(24, Math.min(54, groupStep * 0.62));
        const patternId = `iatForeignHatch-${tabSafe(country)}`;
        group.rows.forEach((row, scenarioIndex) => {
          const adjusted = Number(row.adjusted_occ_per_kw || 0);
          const local = Math.max(0, Number(row.display_local_per_kw || 0));
          const foreign = Math.max(0, Number(row.display_foreign_per_kw || 0));
          const mismatch = adjusted - (local + foreign);
          const x = m.left + step * groupIndex + groupStep * (scenarioIndex + 1) - barW / 2;
          const localY = yScale(local);
          const stackY = yScale(local + foreign);
          const localH = Math.max(0, yScale(0) - localY);
          const foreignH = Math.max(0, localY - stackY);
          const scenarioLabel = row.scenario || `Scenario ${scenarioIndex + 1}`;
          const scenarioShortLabel = /^Scenario\s+(\d+)$/i.test(scenarioLabel)
            ? `S${scenarioLabel.match(/\d+/)[0]}`
            : `S${scenarioIndex + 1}`;
          const tip = `<b>${esc(countryLabel)} · ${esc(scenarioLabel)}</b><br>Original OCC ($/kW): ${fmt(Math.round(Number(row.input_occ_per_kw || 0)))}<br>Adjusted OCC ($/kW): ${fmt(Math.round(adjusted))}<br>Local OCC ($/kW): ${fmt(Math.round(local))}<br>Foreign / Imported OCC ($/kW): ${fmt(Math.round(foreign))}${Math.abs(mismatch) > tolerance ? `<br>Model check difference: ${fmt(Math.round(mismatch))} $/kW` : ""}`;
          if (localH > 0) svg += `<rect class="hoverable" data-tip="${tip}" x="${x}" y="${localY}" width="${barW}" height="${localH}" fill="${color}" stroke="${color}" rx="2"></rect>`;
          if (foreignH > 0) {
            svg += `<rect class="hoverable" data-tip="${tip}" x="${x}" y="${stackY}" width="${barW}" height="${foreignH}" fill="none" stroke="${color}" rx="2"></rect>`;
            svg += `<rect pointer-events="none" x="${x}" y="${stackY}" width="${barW}" height="${foreignH}" fill="url(#${patternId})" stroke="none"></rect>`;
          }
          svg += `<text x="${x + barW / 2}" y="${h - 54}" text-anchor="middle" fill="#41566d" font-size="14" font-weight="700">${esc(scenarioShortLabel)}</text>`;
        });
        const groupCenter = m.left + step * groupIndex + step / 2;
        svg += `<text x="${groupCenter}" y="${h - 78}" text-anchor="middle" fill="#41566d" font-size="14" font-weight="800">${esc(countryLabel)}</text>`;
      });
      svg += `<text x="${m.left}" y="${h - 30}" fill="#596775" font-size="13" font-weight="800">Cost origin</text>`;
      svg += `<rect x="${m.left + 106}" y="${h - 43}" width="14" height="14" fill="#64748b" stroke="#64748b" rx="2"></rect><text x="${m.left + 128}" y="${h - 31}" fill="#596775" font-size="13" font-weight="700">Solid — Local</text>`;
      svg += `<rect x="${m.left + 262}" y="${h - 43}" width="14" height="14" fill="none" stroke="#64748b" rx="2"></rect><rect x="${m.left + 262}" y="${h - 43}" width="14" height="14" fill="url(#iatForeignLegendHatch)" stroke="none" rx="2"></rect><text x="${m.left + 284}" y="${h - 31}" fill="#596775" font-size="13" font-weight="700">Transparent hatch — Foreign / Imported</text>`;
      svg += `</svg>`;
      return svg;
    }

    function workflowHero(data) {
      return `<div class="hero"><h2>${data.workflow_label}</h2><p>ACCERT workflow results with saved outputs and interactive cost plots.</p></div>${links(data.files)}`;
    }

    function iatTransformationCards(iat) {
      const country = displayCountryName(iat.country || "Selected country");
      const basis = iat.baseline_basis || "WE-FOAK";
      const originalTip = basis === "WE-FOAK"
        ? "U.S. overnight capital cost based on the well-executed first-of-a-kind (WE-FOAK) baseline, before international cost adjustment."
        : "U.S. overnight capital cost from the selected user-provided baseline, before international cost adjustment.";
      const adjustedTip = basis === "WE-FOAK"
        ? "WE-FOAK overnight capital cost after applying the selected country's IAT cost factors."
        : "Overnight capital cost after applying the selected country's IAT cost factors to the user-provided baseline.";
      return `<div class="summary iat-summary-cards">
        <div class="metric"><div class="label">Original OCC (${esc("United States")}, ${esc(basis)}) <span class="help" title="${esc(originalTip)}">?</span></div><div class="value">${fmtKwe(iat.input_occ_per_kw)}</div><div class="subvalue">U.S. baseline entering IAT</div></div>
        <div class="metric"><div class="label">Adjusted OCC (${esc(country)}, ${esc(basis)}) <span class="help" title="${esc(adjustedTip)}">?</span></div><div class="value">${fmtKwe(iat.adjusted_occ_per_kw)}</div><div class="subvalue">After IAT country adjustment</div></div>
        <div class="metric"><div class="label">IAT adjustment</div><div class="value">${fmt((Number(iat.adjustment_ratio || 1) - 1) * 100)}%</div><div class="subvalue">Passed to CRT</div></div>
      </div>`;
    }

    function renderIatOnlyResults(data) {
      const countries = data.iat.country_results || [];
      let html = workflowHero(data) + `<section class="iat-results-section"><h3>IAT Results</h3>`;
      if (!countries.length) return html + iatTransformationCards(data.iat) + `</section>`;
      html += `<div class="tabs">`;
      countries.forEach((cr, idx) => {
        html += `<button class="${idx === 0 ? "active" : ""}" data-tab="iat-country-${tabSafe(cr.country)}">${esc(displayCountryName(cr.country))}</button>`;
      });
      html += `<button data-tab="iat-comparison">Country Comparison</button></div>`;
      countries.forEach((cr, idx) => {
        const d = cr.data;
        html += `<div id="tab-iat-country-${tabSafe(cr.country)}" class="tab-panel ${idx === 0 ? "active" : ""}">`;
        html += `<h3>${esc(displayCountryName(cr.country))}</h3>`;
        html += fileLink(`IAT CSV (${cr.country})`, data.files && data.files[`IAT CSV (${cr.country})`]);
        if (d.scenarios && d.scenarios.length) {
          html += iatScenarioTable(d.summary);
          d.scenarios.forEach((s, i) => { html += iatBlock(s, `${s.scenario || `Scenario ${i + 1}`} result`); });
        } else {
          html += iatBlock(d);
        }
        html += `</div>`;
      });
      html += `<div id="tab-iat-comparison" class="tab-panel"><div class="chart-panel">
        <h3>Adjusted OCC by Country</h3><div id="iatCountryCompChart"></div>
      </div></div></section>`;
      return html;
    }

    function renderCrtResults(data, combined = false) {
      const crt = data.crt;
      let html = `<section class="crt-results-section"><h3>CRT Results</h3>${crtResultsGrid(crt)}`;
      if (combined) html += `<div class="result-note"><strong>Why IAT and CRT OCC can differ</strong><br>IAT-adjusted OCC represents the country-adjusted WE-FOAK cost baseline. CRT then applies its deployment and project-execution assumptions to estimate FOAK and subsequent-unit costs, so CRT FOAK OCC may differ substantially from the IAT-adjusted baseline.</div>`;
      html += metrics([
        {label: `Years to build ${fmtInt(crt.num_noak)} plants`, value: `${fmtInt(crt.years_to_noak)} years`},
        {label: `Years to build ${fmtInt(crt.num_orders)} plants`, value: `${fmtInt(crt.years_to_orderbook)} years`}
      ], "crt-key-cards");
      html += `<div class="tabs">
        <button class="active" data-tab="capital">Capital Cost</button><button data-tab="levers">Reduction Levers</button>
        <button data-tab="durations">Construction Durations</button><button data-tab="breakdown">Cost Breakdown</button>
        <button data-tab="dashboard">Dashboard Image</button><button data-tab="results">Results Table</button>
      </div>`;
      html += `<div id="tab-capital" class="tab-panel active"><div class="chart-grid">
        <div class="chart-panel"><h3>Capital Cost: TCI/NCI and OCC</h3><div id="capitalChart"></div></div>
        <div class="chart-panel"><h3>10-60 - TCI Breakdown</h3><div id="breakdownPreview"></div></div>
      </div></div>`;
      html += `<div id="tab-levers" class="tab-panel"><div class="chart-panel"><h3>TCI Savings by Reduction Lever</h3><div id="waterfallChart"></div></div></div>`;
      html += `<div id="tab-durations" class="tab-panel"><div class="chart-grid">
        <div class="chart-panel"><h3>Total Construction Duration</h3><div id="durationChart"></div></div>
        <div class="chart-panel"><h3>Sequential Construction Timeline</h3><div id="timelineChart"></div></div>
      </div></div>`;
      html += `<div id="tab-breakdown" class="tab-panel"><div class="chart-grid">
        <div class="chart-panel"><h3>10-60 - TCI Breakdown</h3><div id="breakdownTciChart"></div></div>
        <div class="chart-panel"><h3>10-50 - OCC Components</h3><div id="breakdownOccChart"></div></div>
      </div></div>`;
      html += `<div id="tab-dashboard" class="tab-panel">`;
      if (crt.dashboard_url) {
        const dashUrl = `${crt.dashboard_url}?t=${Date.now()}`;
        html += `<div class="download-bar"><span>Dashboard image${crt.show_levers ? " with lever table" : " without lever table"}</span><a href="${dashUrl}" target="_blank">Download PNG</a></div><img class="dashboard" src="${dashUrl}" alt="CRT dashboard">`;
      }
      html += `</div><div id="tab-results" class="tab-panel">${fileLink("Download CRT results CSV", data.files && data.files["CRT results CSV"])}${table(crt.plants, crtResultsColumns())}</div></section>`;
      return html;
    }

    function renderCombinedResults(data) {
      const iat = data.iat;
      let html = workflowHero(data) + `<section class="iat-results-section"><h3>IAT Results</h3>`;
      html += iatTransformationCards(iat) + iatBreakdown(iat);
      if (iat.comparison_chart && iat.comparison_chart.length) {
        html += `<div class="chart-panel iat-combined-comparison"><h3>Original vs. Adjusted OCC</h3><div id="iatCombinedComparisonChart"></div></div>`;
      }
      html += fileLink("IAT adjusted CSV", data.files && data.files["IAT adjusted CSV"]);
      html += `</section>${renderCrtResults(data, true)}`;
      return html;
    }

    function renderCrtOnlyResults(data) {
      const source = data.base_case?.source || "Selected CRT baseline";
      return workflowHero(data) + `<section class="crt-only-baseline"><h3>CRT-only baseline</h3><p>${esc(source)}</p></section>${renderCrtResults(data)}`;
    }

    function render(data) {
      lastData = data;
      const result = $("result");
      let html;
      if (data.workflow === "iat_only") html = renderIatOnlyResults(data);
      else if (data.workflow === "iat_crt") html = renderCombinedResults(data);
      else if (data.workflow === "crt_only") html = renderCrtOnlyResults(data);
      else html = workflowHero(data);
      if (data.notes && data.notes.length) html += `<h3>Notes</h3><ul>${data.notes.map(n => `<li>${n}</li>`).join("")}</ul>`;
      result.innerHTML = html;
      document.querySelectorAll(".coaUnit").forEach(select => {
        select.addEventListener("change", event => {
          coaUnit = event.target.value;
          render(lastData);
        });
      });
      if (data.crt) {
        if (data.iat && data.iat.comparison_chart && data.iat.comparison_chart.length && $("iatCombinedComparisonChart")) {
          $("iatCombinedComparisonChart").innerHTML = countryComparisonChart(data.iat.comparison_chart);
        }
        $("capitalChart").innerHTML = capitalChart(data.crt.capital_cost || data.crt.plants);
        $("breakdownPreview").innerHTML = breakdownChart(data.crt.plants, "tci");
        $("waterfallChart").innerHTML = waterfallChart(data.crt.waterfall);
        $("durationChart").innerHTML = durationChart(data.crt.plants);
        $("timelineChart").innerHTML = timelineChart(data.crt.timeline);
        $("breakdownTciChart").innerHTML = breakdownChart(data.crt.plants, "tci");
        $("breakdownOccChart").innerHTML = breakdownChart(data.crt.plants, "occ");
        setupTabs();
        setupCoaTables();
        bindTips(result);
      } else {
        if (data.iat && data.iat.country_results) {
          setupTabs();
          $("iatCountryCompChart").innerHTML = countryComparisonChart(data.iat.comparison_chart || []);
          bindTips(result);
        }
        setupCoaTables();
      }
    }

    async function runWorkflow() {
      if (!validateAdvancedInputs()) return;
      $("runBtn").disabled = true;
      $("status").className = "status";
      const workflow = $("workflow").value;
      setWorkflowStep(3);
      const stage = workflow === "iat_only" ? "iat" : workflow === "crt_only" ? "crt" : "prepare";
      const message = workflow === "iat_crt" ? "Running IAT, then CRT…" : stage === "iat" ? "Running IAT…" : "Running CRT…";
      $("status").firstChild.textContent = "Running";
      setProcessingStage(stage, message);
      try {
        const response = await fetch("/run", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(payload())
        });
        const data = await response.json();
        if (!response.ok || data.error) throw new Error(data.error || "Run failed");
        setProcessingStage("render", "Rendering results…");
        render(data);
        $("status").firstChild.textContent = "Complete";
        setProcessingStage("complete", "Complete");
        setWorkflowStep(3);
      } catch (error) {
        $("status").className = "status error";
        $("status").firstChild.textContent = "Run failed";
        setProcessingStage("error", "Run failed");
        $("result").innerHTML = `<div class="empty-state error-state"><div><h2>Run failed</h2><p>${esc(error.message)}</p><p>Review the inputs and try again.</p></div></div>`;
      } finally {
        $("runBtn").disabled = false;
      }
    }

    $("workflow").addEventListener("change", updatePanels);
    $("iatInputMode").addEventListener("change", () => { updatePanels(); updateIatAssumptionCountryOptions(); loadIatFactorDefaults(); });
    $("countrySingle").addEventListener("change", () => { updateIatAssumptionCountryOptions(); loadIatFactorDefaults(); updateOutputName(); });
    $("iatReactorType").addEventListener("change", () => {
      syncCrtOptionsToIat();
      updateOutputName();
      const isCsvMode = $("iatInputMode").value === "csv" || $("workflow").value === "iat_crt";
      if (isCsvMode) {
        if (!_csvFileContent) updateDefaultCsvPath();
        updateElectricOutputDefault();
      }
    });
    $("iatBaseline").addEventListener("change", () => {
      if ($("iatBaseline").value === "custom") {
        _csvFilePath = null;
        $("iatCsvName").value = "";
      }
      syncBaselineSelection();
    });
    $("scenarioCount").addEventListener("input", updatePanels);
    $("numOrders").addEventListener("input", updatePanels);
    $("countryDropdownBtn").addEventListener("click", e => {
      e.stopPropagation();
      $("countryDropdownMenu").classList.toggle("hidden");
    });
    document.addEventListener("click", e => {
      if (!$("countryMulti").contains(e.target)) {
        $("countryDropdownMenu").classList.add("hidden");
      }
    });
    document.querySelectorAll("#countryDropdownMenu input[type='checkbox']").forEach(cb => {
      cb.addEventListener("change", () => { saveIatFactorOverrides(); updateCountryDropdownLabel(); loadIatFactorDefaults(); updateOutputName(); });
    });
    $("iatAssumptionCountry").addEventListener("change", () => { loadIatFactorDefaults(); updateIatAssumptionContext(); });
    document.querySelectorAll(".workflow-step").forEach(step => {
      step.addEventListener("click", () => navigateToWorkflowStep(Number(step.dataset.step)));
    });
    $("iatBrowseBtn").addEventListener("click", () => $("iatCsvFile").click());
    $("iatCsvFile").addEventListener("change", () => {
      const file = $("iatCsvFile").files[0];
      if (!file) return;
      $("iatBaseline").value = "custom";
      _csvFilePath = null;
      $("iatCsvName").value = file.name;
      const reader = new FileReader();
      reader.onload = e => { _csvFileContent = e.target.result; };
      reader.readAsText(file);
    });
    $("crtBrowseBtn").addEventListener("click", () => $("crtCsvFile").click());
    $("crtCsvFile").addEventListener("change", () => {
      const file = $("crtCsvFile").files[0];
      if (!file) return;
      _crtFilePath = null;
      $("crtCsvName").value = file.name;
      const reader = new FileReader();
      reader.onload = e => { _crtFileContent = e.target.result; };
      reader.readAsText(file);
      updateOutputName();
    });
    $("crtReactorType").addEventListener("change", () => { updateCrtDefaults(true); updateOutputName(); });
    $("crtReactorType").addEventListener("change", () => { syncCrtOptionsToIat(); updateElectricOutputDefault(); updateOutputName(); });
    $("runBtn").addEventListener("click", runWorkflow);
    $("resetBtn").addEventListener("click", () => location.reload());
    enhanceLabels();
    updatePanels();
    syncCrtOptionsToIat();
    updateIatAssumptionCountryOptions();
    loadIatFactorDefaults();
    document.querySelectorAll("input, select").forEach(control => {
      if (control.type === "file") return;
      control.addEventListener("input", updateRunSummary);
      control.addEventListener("change", updateRunSummary);
    });
    $("outputName").addEventListener("input", () => {
      _outputNameCustomized = $("outputName").value.trim() !== _lastGeneratedOutputName;
    });
    updateRunSummary();
  </script>
</body>
</html>
"""


def _safe_name(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value).strip()).strip("._")
    return name or "accert_gui_run"


def _dashboard_title(display_name: str, workflow: str, reactor_type: str, country: str = "") -> str:
    """Return the user-facing dashboard title without changing filename rules."""
    custom = re.sub(r"\s+", " ", str(display_name or "").replace("_", " ").strip())
    if custom:
        return custom
    if workflow == "iat_crt" and country:
        return f"{country} {reactor_type} CRT Dashboard"
    if workflow == "crt_only":
        return f"{reactor_type} CRT Dashboard"
    return f"{reactor_type} IAT Dashboard"


def _resolve_path(value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(str(value)).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _write_uploaded_csv(prefix: str, filename: str | None, content: str) -> Path:
    csv_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", filename or "upload.csv")
    tmp_path = OUTPUT_DIR / f"{prefix}{csv_name}"
    tmp_path.write_text(content)
    return tmp_path


def _is_accert_account_output(path: Path) -> bool:
    columns = set(pd.read_csv(path, nrows=0).columns)
    return {"code_of_account", "account_description", "total_cost"}.issubset(columns)


def _prepare_iat_input_csv(payload: dict) -> Path:
    iat = payload["iat"]
    prepared = iat.get("_prepared_input_csv")
    if prepared:
        return Path(prepared)

    csv_content = iat.get("csv_content")
    if csv_content:
        input_csv = _write_uploaded_csv("_upload_", iat.get("csv_filename"), csv_content)
    else:
        input_csv = _resolve_path(iat.get("input_csv"))
        if input_csv is None:
            raise ValueError("IAT CSV input path or uploaded file is required")

    if _is_accert_account_output(input_csv):
        name = _safe_name(payload.get("output_name", "accert_gui_run"))
        converted_csv = OUTPUT_DIR / f"{name}_accert_baseline_for_iat_crt.csv"
        crt = payload.get("crt", {})
        accert_output_to_crt_baseline(
            input_csv,
            converted_csv,
            reactor_type=crt.get("reactor_type", "AP1000"),
            total_20s_labor_hours=_num(
                crt.get("total_20s_labor_hours"),
                DEFAULT_20S_LABOR_HOURS.get(crt.get("reactor_type", "AP1000"), DEFAULT_20S_LABOR_HOURS["AP1000"]),
            ),
        )
        iat["_prepared_from_accert_csv"] = str(input_csv)
        iat["_prepared_input_csv"] = str(converted_csv)
        return converted_csv

    iat["_prepared_input_csv"] = str(input_csv)
    return input_csv


def _prepare_crt_baseline_csv(payload: dict) -> Path | None:
    crt = payload["crt"]
    prepared = crt.get("_prepared_baseline_csv")
    if prepared:
        return Path(prepared)

    csv_content = crt.get("baseline_csv_content")
    if csv_content:
        input_csv = _write_uploaded_csv("_crt_upload_", crt.get("baseline_csv_filename"), csv_content)
    else:
        input_csv = _resolve_path(crt.get("baseline_csv"))
        if input_csv is None:
            return None

    if _is_accert_account_output(input_csv):
        name = _safe_name(payload.get("output_name", "accert_gui_run"))
        converted_csv = OUTPUT_DIR / f"{name}_accert_baseline_for_crt.csv"
        accert_output_to_crt_baseline(
            input_csv,
            converted_csv,
            reactor_type=crt.get("reactor_type", "AP1000"),
            total_20s_labor_hours=_num(
                crt.get("total_20s_labor_hours"),
                DEFAULT_20S_LABOR_HOURS.get(crt.get("reactor_type", "AP1000"), DEFAULT_20S_LABOR_HOURS["AP1000"]),
            ),
        )
        crt["_prepared_from_accert_csv"] = str(input_csv)
        crt["_prepared_baseline_csv"] = str(converted_csv)
        return converted_csv

    crt["_prepared_baseline_csv"] = str(input_csv)
    return input_csv


def _num(value, default=None):
    if value in (None, ""):
        return default
    return float(value)


def _int(value, default=None):
    if value in (None, ""):
        return default
    return int(float(value))


def _parse_occ_values(value) -> list[float]:
    if isinstance(value, list):
        values = [item for item in value if item not in (None, "")]
    else:
        values = [item.strip() for item in str(value).split(",") if item.strip()]
    if not values:
        raise ValueError("At least one OCC value is required for standalone IAT mode")
    if len(values) > 3:
        raise ValueError("Standalone IAT supports 1 to 3 OCC scenarios")
    return [float(item) for item in values]


def _records(df: pd.DataFrame | None) -> list[dict]:
    if df is None or df.empty:
        return []
    clean = df.copy()
    return json.loads(clean.to_json(orient="records"))


def _coa_sorted_summary(adjusted_costs: pd.DataFrame) -> pd.DataFrame:
    summary = level_account_summary(adjusted_costs, max_level=2).copy()
    if "COA" not in summary.columns:
        return summary
    summary["_coa_order"] = pd.to_numeric(summary["COA"], errors="coerce")
    summary = summary.sort_values(["_coa_order", "COA"], kind="stable").drop(columns=["_coa_order"])
    return summary.reset_index(drop=True)


def _occ_rows(summary: pd.DataFrame) -> pd.DataFrame:
    coa = summary["COA"].astype(str)
    return summary[coa.str.match(r"^[1235]0$")].copy()


def _reactor_power_kwe(payload: dict) -> float:
    if payload.get("workflow") == "iat_crt":
        return reactor_power_mwe(payload["crt"]["reactor_type"]) * 1000.0
    iat = payload.get("iat", {})
    if iat.get("input_mode") == "occ":
        return 1.0
    mwe = _num(iat.get("electric_output_mwe"), 0.0)
    if mwe and mwe > 0:
        return mwe * 1000.0
    reactor = str(iat.get("reactor_type") or "")
    return 310.8 * 1000.0 if "SMR" in reactor else 2234.0 * 1000.0


def _comparison_chart_row(
    country: str,
    summary: dict,
    reference_case: bool,
    scenario: str = "Adjusted OCC",
) -> dict:
    """Build chart-only local/foreign values without changing raw IAT metrics.

    The standard U.S. case is a visual reference convention: its full adjusted
    OCC is shown as local and its displayed foreign portion is zero. The raw
    model decomposition remains available in the ``model_*`` fields. The
    caller applies this convention to every U.S. chart row, including custom
    scenarios, because the chart's U.S. bar is always the visual reference.
    """
    adjusted = summary.get("adjusted_occ_per_kw")
    model_local = summary.get("local_occ_per_kw")
    model_foreign = summary.get("foreign_occ_per_kw")
    return {
        "country": country,
        "scenario": scenario,
        "input_occ_per_kw": summary.get("input_occ_per_kw"),
        "adjusted_occ_per_kw": adjusted,
        "local_per_kw": adjusted if reference_case else model_local,
        "foreign_per_kw": 0.0 if reference_case else model_foreign,
        "model_local_per_kw": model_local,
        "model_foreign_per_kw": model_foreign,
        "reference_case": reference_case,
        "label": country,
    }


def _iat_metrics(adjusted_costs: pd.DataFrame, power_kwe: float) -> dict:
    summary = _coa_sorted_summary(adjusted_costs)
    occ = _occ_rows(summary)
    input_occ = float(occ["Original Total Cost"].sum())
    adjusted_occ = float(occ["Adjusted Total Cost"].sum())
    factor = adjusted_occ / input_occ if input_occ else 0.0
    lf = occ_local_foreign_totals(adjusted_costs)
    data = adjusted_costs.copy()
    accounts = _normalize_accounts(data["Account"])
    if "Is Leaf Account" in data.columns:
        leaf_mask = data["Is Leaf Account"].astype(bool)
    else:
        leaf_mask = _leaf_mask(accounts)
    occ_mask = accounts.str.startswith(("1", "2", "3", "5"))
    leaf_occ = data.loc[leaf_mask & occ_mask]
    category_totals = {
        "factory": float(leaf_occ["Adjusted Factory Equipment Cost"].sum()),
        "material": float(leaf_occ["Adjusted Site Material Cost"].sum()),
        "labor": float(leaf_occ["Adjusted Site Labor Cost"].sum()),
        "other": float(
            leaf_occ["Adjusted Land Cost"].sum()
            + leaf_occ["Adjusted Catch-All Cost"].sum()
        ),
    }
    return {
        "input_occ_total": input_occ,
        "adjusted_occ_total": adjusted_occ,
        "occ_adjustment_factor": factor,
        "power_kwe": power_kwe,
        "input_occ_per_kw": input_occ / power_kwe if power_kwe else None,
        "adjusted_occ_per_kw": adjusted_occ / power_kwe if power_kwe else None,
        "local_occ_per_kw": lf["local"] / power_kwe if power_kwe else None,
        "foreign_occ_per_kw": lf["foreign"] / power_kwe if power_kwe else None,
        "breakdown": {
            **category_totals,
            **{
                f"{name}_per_kw": value / power_kwe if power_kwe else None
                for name, value in category_totals.items()
            },
        },
        "comparison": _records(summary),
    }


def _timeline_records(plants: pd.DataFrame, staggering_ratio: float) -> list[dict]:
    rows: list[dict] = []
    previous_start = 0.0
    previous_construction_end = 0.0
    previous_startup_end = 0.0
    for _, row in plants.iterrows():
        construction_months = float(row.get("Construction duration", 0.0) or 0.0)
        startup_months = float(row.get("Startup duration", 0.0) or 0.0)
        plant = int(row.get("Plant number", len(rows) + 1))
        if not rows:
            construction_start = 0.0
        else:
            construction_start = previous_start + (construction_months * max(0.0, 1.0 - staggering_ratio) / 12.0)
        construction_end = construction_start + construction_months / 12.0
        if construction_end < previous_construction_end:
            construction_end = previous_construction_end
            construction_start = max(0.0, construction_end - construction_months / 12.0)
        startup_end = construction_end + startup_months / 12.0
        if startup_end < previous_startup_end:
            startup_end = previous_startup_end
        rows.append(
            {
                "plant": plant,
                "construction_start_year": construction_start,
                "construction_end_year": construction_end,
                "startup_end_year": startup_end,
            }
        )
        previous_start = construction_start
        previous_construction_end = construction_end
        previous_startup_end = startup_end
    return rows


def _file_info(path: Path) -> dict:
    return {
        "path": str(path),
        "url": f"/outputs/{path.name}",
    }


def _iat_config(payload: dict, output_csv: Path | None = None, country: str | None = None) -> dict:
    iat = payload["iat"]
    if country is None:
        countries = iat.get("countries") or []
        country = countries[0] if countries else iat.get("country", "United States")
    config = {
        "reactor_type": iat["reactor_type"],
        "country": country,
        "year_dollar": _int(iat["year_dollar"], DEFAULT_IAT_YEAR_DOLLAR),
    }
    overrides = iat.get("adjustment_factor_overrides", {})
    if isinstance(overrides, dict):
        config["adjustment_factor_overrides"] = overrides.get(country, {})
    if output_csv is not None:
        config["output_csv"] = output_csv
    if iat["input_mode"] == "occ":
        config["occ_values"] = _parse_occ_values(iat["occ_values"])
        return config

    config["input_csv"] = _prepare_iat_input_csv(payload)
    return config


def _crt_config(payload: dict, baseline_csv: Path | None = None) -> dict:
    crt = payload["crt"]
    config = {
        "reactor_type": crt["reactor_type"],
        "f_22": _num(crt["f_22"], 0.0),
        "f_2321": _num(crt["f_2321"], 0.0),
        "land_cost_per_acre_0": _num(crt["land_cost_per_acre_0"], DEFAULT_LAND_COST_PER_ACRE),
        "startup_0": _num(crt["startup_0"], 28.0),
        "construction_duration_0": _num(
            crt.get("construction_duration_0"),
            DEFAULT_CONSTRUCTION_DURATIONS.get(crt.get("reactor_type", "AP1000"), 76.0),
        ),
        "staggering_ratio": _num(crt["staggering_ratio"], 0.75),
    }
    if baseline_csv is not None:
        config["baseline_csv"] = baseline_csv
        return config
    path = _prepare_crt_baseline_csv(payload)
    if path is not None:
        config["baseline_csv"] = path
    return config


def _levers(payload: dict) -> dict:
    levers = payload["levers"]
    return {
        "num_orders": _int(levers["num_orders"], 1),
        "num_NOAK": _int(levers["num_NOAK"], levers["num_orders"]),
        "itc_percent": _num(levers["itc_percent"], 0.0),
        "n_itc": _int(levers["n_itc"], 0),
        "interest_percent": _num(levers["interest_percent"], 6.0),
        "design_completion_percent": _num(levers["design_completion_percent"], 70.0),
        "design_maturity": _num(levers["design_maturity"], 1.0),
        "proc_exp": _num(levers["proc_exp"], 0.5),
        "N_proc": _num(levers["N_proc"], 3.0),
        "ce_exp": _num(levers["ce_exp"], 0.5),
        "N_cons": _num(levers["N_cons"], 5.0),
        "ae_exp": _num(levers["ae_exp"], 0.5),
        "N_AE": _num(levers["N_AE"], 4.0),
        "standardization_percent": _num(levers["standardization_percent"], 80.0),
        "modularity_code": _int(levers["modularity_code"], 0),
        "bop_grade_code": _int(levers["bop_grade_code"], 0),
        "rb_grade_code": _int(levers["rb_grade_code"], 0),
    }


def _summarize_iat_result(result: dict, power_kwe: float) -> dict:
    metrics = _iat_metrics(result["adjusted_costs"], power_kwe)
    return {
        "country": result["country"],
        "input_total": result["input_total"],
        "adjusted_total": result["adjusted_total"],
        "adjustment_ratio": result["occ_adjustment_ratio"],
        **metrics,
    }


def _base_case_from_iat_result(result: dict, power_kwe: float) -> dict:
    metrics = _iat_metrics(result["adjusted_costs"], power_kwe)
    comparison = []
    for row in metrics["comparison"]:
        comparison.append(
            {
                "COA": row.get("COA"),
                "Title": row.get("Title"),
                "Equipment Cost": row.get("Original Equipment Cost", 0.0),
                "Material Cost": row.get("Original Material Cost", 0.0),
                "Labor Cost": row.get("Original Labor Cost", 0.0),
                "Land Cost": row.get("Original Land Cost", 0.0),
                "Catch-All Cost": row.get("Original Catch-All Cost", 0.0),
                "Total Cost": row.get("Original Total Cost", 0.0),
            }
        )
    return {
        "source": result.get("input_source", "IAT input baseline"),
        "power_kwe": power_kwe,
        "comparison": comparison,
    }


def _summarize_occ_result(result: dict, power_kwe: float) -> dict:
    first = result["scenario_results"][0]
    metrics = _iat_metrics(first["adjusted_costs"], power_kwe)
    scenarios = []
    for scenario in result["scenario_results"]:
        scenario_metrics = _iat_metrics(scenario["adjusted_costs"], power_kwe)
        scenario_metrics.update(
            {
                "scenario": scenario.get("scenario", ""),
                "country": scenario["country"],
                "input_total": scenario["input_total"],
                "adjusted_total": scenario["adjusted_total"],
                "adjustment_ratio": scenario["occ_adjustment_ratio"],
            }
        )
        scenarios.append(scenario_metrics)
    return {
        "country": result["country"],
        "input_total": first["input_total"],
        "adjusted_total": first["adjusted_total"],
        "adjustment_ratio": first["occ_adjustment_ratio"],
        "summary": _records(result["summary"]),
        "scenarios": scenarios,
        **metrics,
    }


def _normalize_accounts(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)


def _leaf_mask(accounts: pd.Series) -> pd.Series:
    values = accounts.astype(str).tolist()
    return pd.Series(
        [
            not any(other != account and other.startswith(account) for other in values)
            for account in values
        ],
        index=accounts.index,
    )


def _base_case_summary_from_dataframe(df: pd.DataFrame, power_kwe: float, source: str) -> dict:
    data = df.copy()
    data["Account"] = _normalize_accounts(data["Account"])
    for column in [
        "Total Cost (USD)",
        "Factory Equipment Cost",
        "Site Material Cost",
        "Site Labor Cost",
        "Land Cost",
        "Catch-All Cost",
    ]:
        if column not in data.columns:
            data[column] = 0.0
        data[column] = pd.to_numeric(
            data[column].astype(str).str.replace(",", "", regex=False),
            errors="coerce",
        ).fillna(0.0)
    accounts = data["Account"].astype(str)
    leaf = data.loc[_leaf_mask(accounts)].copy()
    leaf_accounts = leaf["Account"].astype(str)
    rows = []

    def add_row(code: str, title: str, subset: pd.DataFrame) -> None:
        if subset.empty:
            return
        rows.append(
            {
                "COA": code,
                "Title": title,
                "Equipment Cost": float(subset["Factory Equipment Cost"].sum()),
                "Material Cost": float(subset["Site Material Cost"].sum()),
                "Labor Cost": float(subset["Site Labor Cost"].sum()),
                "Land Cost": float(subset["Land Cost"].sum()),
                "Catch-All Cost": float(subset["Catch-All Cost"].sum()),
                "Total Cost": float(subset["Total Cost (USD)"].sum()),
            }
        )

    level_2_codes = sorted({account[:2] for account in accounts if len(account) >= 2 and account[:2].isdigit()})
    for group in sorted({account[0] for account in leaf_accounts if account and account[0].isdigit()}):
        add_row(f"{group}0", BASE_GROUP_TITLES.get(f"{group}0", ""), leaf.loc[leaf_accounts.str.startswith(group)])
        for code in [code for code in level_2_codes if code.startswith(group) and code != f"{group}0"]:
            subset = leaf.loc[leaf_accounts.str.startswith(code)]
            if subset.empty:
                continue
            title_rows = data.loc[data["Account"].eq(code), "Title"]
            add_row(code, str(title_rows.iloc[0]) if not title_rows.empty else "", subset)
    return {
        "source": source,
        "power_kwe": power_kwe,
        "comparison": rows,
    }


def _base_case_from_crt_config(config: dict) -> dict:
    df, power = InputStore(
        data_dir=config.get("data_dir"),
        baseline_csv=config.get("baseline_csv"),
    ).get_baseline(config["reactor_type"])
    source = str(config.get("baseline_csv") or f"{config['reactor_type']} built-in baseline")
    return _base_case_summary_from_dataframe(df, power, source)


def _capital_cost_records(plants: pd.DataFrame) -> list[dict]:
    columns = ["Plant number", "TCI", "NCI", "OCC", "Net OCC", "ITC reduction"]
    available = [column for column in columns if column in plants.columns]
    records = _records(plants[available])
    for row in records:
        tci = float(row.get("TCI") or 0.0)
        nci_value = row.get("NCI")
        nci = tci if nci_value in (None, "") else float(nci_value)
        row["NCI"] = nci
        occ = float(row.get("OCC") or 0.0)
        net_occ_value = row.get("Net OCC")
        row["Net OCC"] = occ if net_occ_value in (None, "") else float(net_occ_value)
        row["TCI ITC reduction"] = max(0.0, tci - nci)
        row["OCC ITC reduction"] = max(0.0, occ - row["Net OCC"])
        row["ITC reduction"] = row["TCI ITC reduction"]
    return records


def _summarize_crt_result(result: dict) -> dict:
    noak = int(result.get("num_NOAK", result.get("Num_orders", 1)))
    num_orders = int(result.get("Num_orders", result.get("num_orders", noak)))
    plant_columns = [
        "Plant number",
        "OCC",
        "Net OCC",
        "TCI",
        "NCI",
        "Construction duration",
        "Startup duration",
        "Preconstruction costs",
        "Direct costs",
        "Direct costs: equipment",
        "Direct costs: material",
        "Direct costs: labor",
        "Indirect costs",
        "Supplementary costs",
        "Financing costs",
    ]
    plants = results_to_dataframe(result)
    available = [column for column in plant_columns if column in plants.columns]
    capital_cost = _capital_cost_records(plants)
    timeline = _timeline_records(
        plants,
        float(result.get("effective_staggering_ratio", result.get("staggering_ratio", 0.75))),
    )
    years_by_plant = {int(row["plant"]): float(row["startup_end_year"]) for row in timeline}
    return {
        "num_noak": noak,
        "num_orders": num_orders,
        "occ_1": result.get("OCC_1"),
        "occ_noak": result.get(f"OCC_{noak}"),
        "net_occ_1": result.get("NETOCC_1", result.get("OCC_1")),
        "net_occ_noak": result.get(f"NETOCC_{noak}", result.get(f"OCC_{noak}")),
        "tci_1": result.get("TCI_1"),
        "tci_noak": result.get(f"TCI_{noak}"),
        "net_tci_1": result.get("NCI_1", result.get("TCI_1")),
        "net_tci_noak": result.get(f"NCI_{noak}", result.get(f"TCI_{noak}")),
        "avg_occ": result.get("avg_OCC"),
        "avg_tci": result.get("avg_TCI"),
        "avg_duration": result.get("avg_duration"),
        "occ_reduction_percent": result.get("occ_reduction_from_FOAK_to_NOAK_percent"),
        "tci_reduction_percent": (
            (float(result.get("TCI_1")) - float(result.get(f"TCI_{noak}")))
            / float(result.get("TCI_1")) * 100.0
            if result.get("TCI_1") and result.get(f"TCI_{noak}") is not None
            else None
        ),
        "years_to_noak": years_by_plant.get(noak),
        "years_to_orderbook": years_by_plant.get(num_orders),
        "show_levers": False,
        "plants": _records(plants[available]),
        "capital_cost": capital_cost,
        "timeline": timeline,
        "waterfall": _records(waterfall_to_dataframe(result)),
    }


def _write_crt_results_csv(result: dict, path: Path) -> pd.DataFrame:
    plants = results_to_dataframe(result)
    path.parent.mkdir(parents=True, exist_ok=True)
    plants.to_csv(path, index=False)
    return plants


def run_workflow(payload: dict) -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    name = _safe_name(payload.get("output_name", "accert_gui_run"))
    workflow = payload["workflow"]
    files: dict[str, dict] = {}
    notes: list[str] = []
    response: dict = {
        "workflow": workflow,
        "workflow_label": {
            "iat_only": "IAT Only",
            "crt_only": "CRT Only",
            "iat_crt": "IAT then CRT",
        }.get(workflow, workflow),
        "files": files,
        "notes": notes,
    }

    if workflow == "iat_crt":
        csv_mode = payload["iat"].get("input_mode") == "csv"
        iat_reactor_type = payload["iat"].get("reactor_type")
        iat_label = next(
            (
                label for label in ("Large Reactor", "SMR")
                if iat_api_type_from_label(label, csv_mode=csv_mode) == iat_reactor_type
            ),
            None,
        )
        if iat_label is None:
            raise ValueError(
                f"Unknown IAT reactor type {iat_reactor_type!r} for the selected input mode."
            )
        crt_reactor_type = payload["crt"].get("reactor_type")
        if crt_reactor_type not in compatible_crt_types(iat_label):
            raise ValueError(
                f"CRT reactor type {crt_reactor_type!r} is not compatible with IAT reactor type {iat_label!r}."
            )
        baseline_reactor_type = payload["iat"].get("baseline_reactor_type")
        if baseline_reactor_type and baseline_reactor_type != "custom" and baseline_reactor_type != crt_reactor_type:
            raise ValueError(
                f"ACCERT baseline reactor type {baseline_reactor_type!r} does not match CRT reactor type {crt_reactor_type!r}."
            )

    if workflow == "iat_only":
        iat = payload["iat"]
        countries = iat.get("countries") or [iat.get("country", "China")]
        if not countries:
            raise ValueError("At least one country must be selected")
        power_kwe = _reactor_power_kwe(payload)
        country_results: list[dict] = []
        comparison_chart: list[dict] = []
        for country in countries:
            country_slug = re.sub(r"[^A-Za-z0-9]+", "_", country.lower())
            iat_csv = OUTPUT_DIR / f"{name}_iat_{country_slug}_adjusted.csv"
            config = _iat_config(payload, iat_csv, country=country)
            if iat["input_mode"] == "occ":
                result = run_occ_scenarios(config)
                summary = _summarize_occ_result(result, power_kwe)
                if "base_case" not in response and result["scenario_results"]:
                    response["base_case"] = _base_case_from_iat_result(result["scenario_results"][0], power_kwe)
                reference_case = country == "United States"
                for scenario in summary["scenarios"]:
                    comparison_chart.append(
                        _comparison_chart_row(
                            country,
                            scenario,
                            reference_case,
                            scenario=scenario.get("scenario") or "Scenario 1",
                        )
                    )
            else:
                result = run_adjustment(config)
                if iat.get("_prepared_from_accert_csv") and "Converted ACCERT baseline" not in files:
                    files["Converted ACCERT baseline"] = _file_info(Path(iat["_prepared_input_csv"]))
                    notes.append("The raw ACCERT account CSV was converted to CRT/IAT baseline format before IAT was run.")
                summary = _summarize_iat_result(result, power_kwe)
                if "base_case" not in response:
                    response["base_case"] = _base_case_from_iat_result(result, power_kwe)
                reference_case = country == "United States"
                comparison_chart.append(_comparison_chart_row(country, summary, reference_case))
            country_results.append({"country": country, "data": summary})
            files[f"IAT CSV ({country})"] = _file_info(iat_csv)
        response["iat"] = {
            "country_results": country_results,
            "comparison_chart": comparison_chart,
        }
        return response

    if workflow == "crt_only":
        dashboard = OUTPUT_DIR / f"{name}_crt_dashboard.png"
        results_csv = OUTPUT_DIR / f"{name}_crt_results.csv"
        config = _crt_config(payload)
        if payload["crt"].get("_prepared_from_accert_csv"):
            files["Converted ACCERT baseline"] = _file_info(Path(payload["crt"]["_prepared_baseline_csv"]))
            notes.append("The raw ACCERT account CSV was converted to CRT baseline format before CRT was run.")
        response["base_case"] = _base_case_from_crt_config(config)
        result = run_one_scenario(config, _levers(payload))
        _write_crt_results_csv(result, results_csv)
        save_dashboard(
            result,
            dashboard,
            title=_dashboard_title(
                payload.get("output_name", ""),
                workflow,
                payload["crt"]["reactor_type"],
            ),
            show_levers=bool(payload["crt"].get("show_levers", True)),
        )
        response["crt"] = _summarize_crt_result(result)
        response["crt"]["show_levers"] = bool(payload["crt"].get("show_levers", True))
        response["crt"]["dashboard_url"] = _file_info(dashboard)["url"]
        files["CRT results CSV"] = _file_info(results_csv)
        files["CRT dashboard"] = _file_info(dashboard)
        return response

    if workflow == "iat_crt":
        iat_csv = OUTPUT_DIR / f"{name}_iat_adjusted_for_crt.csv"
        dashboard = OUTPUT_DIR / f"{name}_crt_dashboard.png"
        results_csv = OUTPUT_DIR / f"{name}_crt_results.csv"
        iat_payload = json.loads(json.dumps(payload))
        iat_payload["iat"]["input_mode"] = "csv"
        iat_result = run_adjustment(_iat_config(iat_payload, iat_csv))
        response["base_case"] = _base_case_from_iat_result(iat_result, _reactor_power_kwe(payload))
        if iat_payload["iat"].get("_prepared_from_accert_csv"):
            files["Converted ACCERT baseline"] = _file_info(Path(iat_payload["iat"]["_prepared_input_csv"]))
            notes.append("The raw ACCERT account CSV was converted to CRT/IAT baseline format before IAT and CRT were run.")
        crt_result = run_one_scenario(_crt_config(payload, baseline_csv=iat_csv), _levers(payload))
        _write_crt_results_csv(crt_result, results_csv)
        _crt_countries = payload["iat"].get("countries") or [payload["iat"].get("country", "")]
        selected_country = _crt_countries[0] if _crt_countries else "United States"
        save_dashboard(
            crt_result,
            dashboard,
            title=_dashboard_title(
                payload.get("output_name", ""),
                workflow,
                payload["crt"]["reactor_type"],
                selected_country,
            ),
            show_levers=bool(payload["crt"].get("show_levers", True)),
        )
        iat_summary = _summarize_iat_result(iat_result, _reactor_power_kwe(payload))
        comparison_chart = []
        if selected_country != "United States":
            comparison_chart = [
                _comparison_chart_row(
                    "United States",
                    {
                        "adjusted_occ_per_kw": iat_summary["input_occ_per_kw"],
                        "local_occ_per_kw": iat_summary["input_occ_per_kw"],
                        "foreign_occ_per_kw": 0.0,
                    },
                    True,
                ),
                _comparison_chart_row(selected_country, iat_summary, False),
            ]
        iat_summary["comparison_chart"] = comparison_chart
        response["iat"] = iat_summary
        response["iat"]["baseline_basis"] = (
            "WE-FOAK"
            if not iat_payload["iat"].get("csv_content") and not iat_payload["iat"].get("_prepared_from_accert_csv")
            else "user-provided baseline"
        )
        response["crt"] = _summarize_crt_result(crt_result)
        response["crt"]["show_levers"] = bool(payload["crt"].get("show_levers", True))
        response["crt"]["dashboard_url"] = _file_info(dashboard)["url"]
        files["IAT adjusted CSV"] = _file_info(iat_csv)
        files["CRT results CSV"] = _file_info(results_csv)
        files["CRT dashboard"] = _file_info(dashboard)
        notes.append("The original CRT baseline CSV was not modified; CRT used the IAT output through baseline_csv.")
        return response

    raise ValueError(f"Unknown workflow: {workflow}")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send(
                200,
                json.dumps({"status": "ok", "version": APP_VERSION, "port": self.server.server_port}).encode("utf-8"),
                "application/json",
            )
            return
        if self.path in {"/", "/index.html"}:
            html = HTML.replace("{{IAT_YEAR_DOLLAR}}", str(DEFAULT_IAT_YEAR_DOLLAR))
            html = html.replace("{{LAND_COST_PER_GUI_UNIT}}", str(LAND_COST_PER_GUI_UNIT))
            html = html.replace("{{LABOR_HOURS_PER_MILLION}}", str(LABOR_HOURS_PER_MILLION))
            html = html.replace("{{IAT_FACTOR_DEFAULTS}}", json.dumps(DEFAULT_IAT_FACTORS))
            html = html.replace("{{REACTOR_CONFIGS}}", json.dumps(REACTOR_CONFIGS))
            self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
            return
        if self.path.startswith("/outputs/"):
            raw = self.path.split("/outputs/", 1)[1].split("?", 1)[0]
            name = Path(unquote(raw)).name
            path = OUTPUT_DIR / name
            if not path.exists() or not path.is_file():
                self._send(404, b"Not found", "text/plain; charset=utf-8")
                return
            content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            self._send(200, path.read_bytes(), content_type)
            return
        self._send(404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:
        if self.path != "/run":
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            result = run_workflow(payload)
            self._send(200, json.dumps(result).encode("utf-8"), "application/json")
        except BrokenPipeError:
            # The browser may navigate away while a long CRT run is finishing.
            # Do not replace that client disconnect with a second server error.
            return
        except Exception as exc:
            traceback.print_exc()
            body = {
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
            try:
                self._send(500, json.dumps(body).encode("utf-8"), "application/json")
            except BrokenPipeError:
                return


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def resolve_gui_port(port: int | str | None = None) -> int:
    raw_port = os.environ.get("ACCERT_GUI_PORT", str(PORT)) if port is None else port
    resolved = int(raw_port)
    if resolved < 0 or resolved > 65535:
        raise ValueError("GUI port must be between 0 and 65535.")
    return resolved


def create_server(host: str = HOST, port: int | str | None = None) -> ReusableThreadingHTTPServer:
    return ReusableThreadingHTTPServer((host, resolve_gui_port(port)), Handler)


def gui_url(host: str = HOST, port: int | str | None = None) -> str:
    return f"http://{host}:{resolve_gui_port(port)}"


def pid_file(port: int | str) -> Path:
    return RUNTIME_DIR / f"gui-{resolve_gui_port(port)}.pid"


def find_available_port(host: str = HOST, preferred: int = PORT) -> int:
    """Return the preferred port when free, otherwise the next free local port."""
    for candidate in range(preferred, 65536):
        try:
            probe = ReusableThreadingHTTPServer((host, candidate), Handler)
        except OSError as exc:
            if exc.errno in {errno.EADDRINUSE, errno.EADDRNOTAVAIL}:
                continue
            raise
        probe.server_close()
        return candidate
    raise OSError("No available local port was found for the ACCERT GUI.")


def is_gui_running(host: str = HOST, port: int | str | None = None, timeout: float = 0.5) -> bool:
    try:
        with urlopen(f"{gui_url(host, port)}/health", timeout=timeout) as response:
            return response.status == 200 and json.load(response).get("status") == "ok"
    except (OSError, URLError, ValueError):
        return False


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local ACCERT IAT/CRT GUI.")
    parser.add_argument("--port", type=int, default=None, help=f"Listening port (default: {PORT} or ACCERT_GUI_PORT).")
    parser.add_argument("--host", default=HOST, help=f"Listening host (default: {HOST}).")
    parser.add_argument("--no-browser", action="store_true", help="Start the server without opening a browser.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    port = resolve_gui_port(args.port)
    if is_gui_running(args.host, port):
        url = gui_url(args.host, port)
        print(f"ACCERT GUI is already running at {url}; reusing that instance.")
        if not args.no_browser:
            webbrowser.open(url)
        return
    try:
        server = create_server(args.host, port)
    except OSError as exc:
        if exc.errno == errno.EADDRINUSE:
            raise SystemExit(
                f"ACCERT GUI could not start: port {port} is already in use. "
                f"Use --port or ACCERT_GUI_PORT to choose another port; unrelated processes are not stopped automatically."
            ) from exc
        raise
    url = gui_url(args.host, server.server_port)
    print(f"ACCERT IAT and CRT GUI running at {url}")
    print(f"Outputs will be written to {OUTPUT_DIR}")
    runtime_pid = pid_file(server.server_port)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    runtime_pid.write_text(str(os.getpid()), encoding="utf-8")

    def request_shutdown(_signum: int, _frame: object) -> None:
        # HTTPServer.shutdown() must run outside serve_forever()'s thread.
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, request_shutdown)
    signal.signal(signal.SIGINT, request_shutdown)
    try:
        if not args.no_browser:
            webbrowser.open(url)
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping ACCERT GUI.")
    finally:
        server.server_close()
        if runtime_pid.exists() and runtime_pid.read_text(encoding="utf-8").strip() == str(os.getpid()):
            runtime_pid.unlink()


if __name__ == "__main__":
    main()
