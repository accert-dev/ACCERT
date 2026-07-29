"""Local GUI for IAT, CRT, and connected IAT-to-CRT workflows.

Run from the repository root with:

    python tutorial/gui/crt_iat_gui.py

Then open:

    http://127.0.0.1:8765
"""

from __future__ import annotations

import json
import mimetypes
import re
import sys
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

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
from iat import level_account_summary, occ_local_foreign_totals, run_adjustment, run_occ_scenarios


HOST = "127.0.0.1"
PORT = 8765
OUTPUT_DIR = REPO_ROOT / "tutorial" / "gui_outputs"
DEFAULT_CONSTRUCTION_DURATIONS = {
    "AP1000": 76.0,
    "SFR": 80.0,
    "HTGR": 125.0,
}
DEFAULT_20S_LABOR_HOURS = {
    "AP1000": 51_112_635.470753975,
    "SFR": 10_402_590.638988608,
    "HTGR": 37_288_941.04573331,
}
BASE_GROUP_TITLES = {
    "10": "Capitalized Pre-Construction Costs",
    "20": "Capitalized Direct Costs",
    "30": "Capitalized Indirect Services Costs",
    "50": "Capitalized Supplementary Costs",
    "60": "Capitalized Financial Costs",
}


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
      background: linear-gradient(90deg, #082f4a, #0b6f86 58%, #15937f);
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
      grid-template-columns: minmax(500px, 560px) minmax(0, 1fr);
      min-height: calc(100vh - 57px);
    }
    aside {
      border-right: 0;
      background:
        radial-gradient(circle at 12% 0%, rgba(78, 188, 214, 0.22), transparent 28%),
        linear-gradient(180deg, var(--sidebar), #07556f 48%, var(--sidebar-2));
      padding: 14px;
      overflow: auto;
    }
    section {
      padding: 16px 18px;
      overflow: auto;
    }
    fieldset {
      border: 1px solid rgba(207,239,248,0.28);
      border-radius: 6px;
      margin: 0 0 12px;
      padding: 12px;
      background: rgba(255,255,255,0.1);
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
      border: 1px solid #90b9cb;
      border-radius: 5px;
      padding: 7px 8px;
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
    input[type="checkbox"] {
      width: auto;
      margin-right: 7px;
    }
    .row {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .triple {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
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
      border-radius: 6px;
      padding: 9px 13px;
      font: inherit;
      font-weight: 700;
      color: white;
      background: var(--orange);
      cursor: pointer;
    }
    button.secondary { background: rgba(255,255,255,0.14); border: 1px solid rgba(199,239,250,0.45); }
    button:disabled { opacity: 0.55; cursor: not-allowed; }
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
      .chart-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <h1>ACCERT IAT and CRT GUI</h1>
    <div class="status" id="status">Ready</div>
  </header>
  <main>
    <aside>
      <div class="actions">
        <button id="runBtn">Run workflow</button>
        <button class="secondary" id="resetBtn" type="button">Reset</button>
      </div>

      <fieldset>
        <legend>Workflow</legend>
        <label for="workflow">Mode</label>
        <select id="workflow">
          <option value="iat_only">IAT only</option>
          <option value="crt_only">CRT only</option>
          <option value="iat_crt" selected>IAT then CRT</option>
        </select>
        <label for="outputName">Output name</label>
        <input id="outputName" value="ap1000_china_gui">
      </fieldset>

      <fieldset id="iatPanel">
        <legend>IAT Inputs</legend>
        <div class="row">
          <div>
            <label for="iatInputMode">Input type</label>
            <select id="iatInputMode">
              <option value="occ" selected>Standalone OCC</option>
              <option value="csv">ACCERT output</option>
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
              <option value="China">China</option>
              <option value="Korea">Korea</option>
              <option value="UAE">UAE</option>
              <option value="Poland">Poland</option>
              <option value="El Salvador">El Salvador</option>
            </select>
            <div id="countryMulti" class="country-dropdown">
              <button type="button" class="country-dropdown-btn" id="countryDropdownBtn">
                <span id="countryDropdownLabel">Korea, China, UAE, Poland, El Salvador</span><span>▾</span>
              </button>
              <div class="country-dropdown-menu hidden" id="countryDropdownMenu">
                <label class="country-option"><input type="checkbox" value="Korea" checked> Korea</label>
                <label class="country-option"><input type="checkbox" value="China" checked> China</label>
                <label class="country-option"><input type="checkbox" value="UAE" checked> UAE</label>
                <label class="country-option"><input type="checkbox" value="Poland" checked> Poland</label>
                <label class="country-option"><input type="checkbox" value="El Salvador" checked> El Salvador</label>
              </div>
            </div>
          </div>
          <div>
            <label>Year dollar</label>
            <div class="readonly-note">2024 CPI-U basis</div>
          </div>
        </div>
        <div id="iatCsvGroup" class="hidden">
          <label>ACCERT CSV file</label>
          <div class="file-input-row">
            <input type="text" id="iatCsvName" readonly placeholder="No file selected">
            <button type="button" id="iatBrowseBtn">Browse…</button>
            <input id="iatCsvFile" type="file" accept=".csv" class="hidden">
          </div>
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

      <fieldset id="crtPanel">
        <legend>CRT Fixed Inputs</legend>
        <label for="crtReactorType">Reactor type</label>
        <select id="crtReactorType">
          <option selected>AP1000</option>
          <option>HTGR</option>
          <option>SFR</option>
        </select>
        <label for="crtCsvName">Optional CRT baseline CSV</label>
        <div class="file-input-row">
          <input type="text" id="crtCsvName" readonly placeholder="Leave blank for built-in baseline">
          <button type="button" id="crtBrowseBtn">Browse…</button>
          <input id="crtCsvFile" type="file" accept=".csv" class="hidden">
        </div>
        <div class="triple">
          <div><label for="f22">f_22</label><input id="f22" type="number" value="250000000"></div>
          <div><label for="f2321">f_2321</label><input id="f2321" type="number" value="150000000"></div>
          <div><label for="landCost">Land $/acre</label><input id="landCost" type="number" value="22000"></div>
        </div>
        <div class="row">
          <div><label for="startup">Startup months</label><input id="startup" type="number" value="28"></div>
          <div><label for="staggering">Staggering ratio</label><input id="staggering" type="number" step="0.01" value="0.75"></div>
        </div>
        <div class="row">
          <div><label for="constructionDuration">Construction duration months</label><input id="constructionDuration" type="number" min="1" step="1" value="76"></div>
          <div><label for="total20sLaborHours">20s labor hours</label><input id="total20sLaborHours" type="number" min="0" step="1" value="51112635"></div>
        </div>
        <div class="inline"><input id="showLevers" type="checkbox"> Include lever table in dashboard image</div>
      </fieldset>

      <fieldset id="leverPanel">
        <legend>CRT Levers</legend>
        <div class="triple">
          <div><label for="numOrders">Firm orders</label><input id="numOrders" type="number" value="10"></div>
          <div><label for="itcPercent">ITC %</label><input id="itcPercent" type="number" value="0"></div>
          <div><label for="designCompletion">Design compl. %</label><input id="designCompletion" type="number" value="70"></div>
        </div>
        <div class="triple">
          <div><label for="numNoak">NOAK unit</label><input id="numNoak" type="number" value="8"></div>
          <div><label for="nItc">ITC units</label><input id="nItc" type="number" value="0"></div>
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
    </aside>
    <section>
      <div id="result">
        <h2>Run Output</h2>
        <p>Select a workflow and run it. The GUI saves CSV and dashboard outputs under <code>tutorial/gui_outputs</code>.</p>
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
    const defaultConstructionDuration = {AP1000: 76, SFR: 80, HTGR: 125};
    const default20sLaborHours = {
      AP1000: 51112635,
      SFR: 10402591,
      HTGR: 37288941
    };

    function numberValue(id) {
      const value = $(id).value.trim();
      return value === "" ? null : Number(value);
    }

    function occScenarioValues() {
      const count = Math.max(1, Math.min(3, Number($("scenarioCount").value || 1)));
      const values = [];
      for (let i = 1; i <= count; i++) values.push(numberValue(`occValue${i}`));
      return values;
    }

    function selectedCountries() {
      const isCsvMode = $("iatInputMode").value === "csv" || $("workflow").value === "iat_crt";
      if (isCsvMode) return [$("countrySingle").value];
      return Array.from(document.querySelectorAll("#countryDropdownMenu input[type='checkbox']:checked"))
        .map(cb => cb.value);
    }

    function updateCountryDropdownLabel() {
      const selected = Array.from(
        document.querySelectorAll("#countryDropdownMenu input[type='checkbox']:checked")
      ).map(cb => cb.value);
      $("countryDropdownLabel").textContent = selected.length ? selected.join(", ") : "Select countries";
    }

    function updateDefaultCsvPath() {
      if (_csvFileContent) return;
      const rt = $("iatReactorType").value;
      const path = rt === "SMR" ? "src/crt/data/SFR_baseline.csv" : "src/crt/data/AP1000_baseline.csv";
      _csvFilePath = path;
      $("iatCsvName").value = path;
    }

    function updateElectricOutputDefault() {
      const rt = $("iatReactorType").value;
      $("electricOutputMwe").value = rt === "SMR" ? "310.8" : "2234";
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
      $("constructionDuration").value = String(defaultConstructionDuration[rt] || 76);
      $("total20sLaborHours").value = String(Math.round(default20sLaborHours[rt] || default20sLaborHours.AP1000));
    }

    function apiReactorType() {
      const rt = $("iatReactorType").value;
      const mode = $("iatInputMode").value;
      if (mode === "csv") return rt === "Large Reactor" ? "ACCERT output-LR" : "ACCERT output-SMR";
      return rt === "Large Reactor" ? "large reactor" : "SMR";
    }

    function payload() {
      return {
        workflow: $("workflow").value,
        output_name: $("outputName").value,
        iat: {
          input_mode: $("iatInputMode").value,
          reactor_type: apiReactorType(),
          countries: selectedCountries(),
          year_dollar: 2024,
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
          f_22: numberValue("f22"),
          f_2321: numberValue("f2321"),
          land_cost_per_acre_0: numberValue("landCost"),
          startup_0: numberValue("startup"),
          construction_duration_0: numberValue("constructionDuration"),
          total_20s_labor_hours: numberValue("total20sLaborHours"),
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
      $("iatPanel").classList.toggle("hidden", workflow === "crt_only");
      $("crtPanel").classList.toggle("hidden", workflow === "iat_only");
      $("leverPanel").classList.toggle("hidden", workflow === "iat_only");
      const inputMode = $("iatInputMode").value;
      const isCsvMode = inputMode === "csv" || workflow === "iat_crt";
      if (workflow === "iat_crt") {
        $("iatInputMode").value = "csv";
        $("iatCsvGroup").classList.remove("hidden");
        $("occScenarioGroup").classList.add("hidden");
      } else {
        const isCsv = inputMode === "csv";
        $("iatCsvGroup").classList.toggle("hidden", !isCsv);
        $("occScenarioGroup").classList.toggle("hidden", isCsv);
      }
      $("countrySingle").classList.toggle("hidden", !isCsvMode);
      $("countryMulti").classList.toggle("hidden", isCsvMode);
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

    function enhanceLabels() {
      const helpText = {
        workflow: "Choose whether to run IAT only, CRT only, or pass IAT-adjusted costs into CRT.",
        outputName: "Base filename for CSV and dashboard outputs saved in tutorial/gui_outputs.",
        iatInputMode: "ACCERT CSV uses a COA cost file. Standalone OCC builds a cost structure from the localization shares.",
        iatReactorType: "Large reactor or SMR localization basis. ACCERT output options use the input COA file.",
        country: "Country where localization and adjustment factors are applied.",
        iatCsv: "Input ACCERT/COA CSV. Relative paths are resolved from the ACCERT repository root.",
        scenarioCount: "Standalone IAT scenario count. Choose 1 to 3 OCC scenarios.",
        occValue1: "Scenario 1 U.S.-based OCC input. IAT allocates this OCC to COA accounts using packaged COA breakdown percentages, then applies localization and adjustment factors.",
        occValue2: "Scenario 2 U.S.-based OCC input. IAT allocates this OCC to COA accounts using packaged COA breakdown percentages, then applies localization and adjustment factors.",
        occValue3: "Scenario 3 U.S.-based OCC input. IAT allocates this OCC to COA accounts using packaged COA breakdown percentages, then applies localization and adjustment factors.",
        crtReactorType: "CRT reactor case to run.",
        crtCsvName: "Optional CSV baseline for CRT. Connected IAT-to-CRT runs fill this automatically.",
        f22: "Factory equipment cost input used by the CRT baseline calculations.",
        f2321: "Turbine-generator equipment cost input used by the CRT baseline calculations.",
        landCost: "Land cost per acre for preconstruction land accounts.",
        startup: "FOAK startup duration in months.",
        constructionDuration: "Reference FOAK construction duration in months. Defaults are AP1000 76, SFR 80, and HTGR 125.",
        total20sLaborHours: "Total labor hours assigned across 20s direct accounts when a raw ACCERT account CSV is converted into a CRT/IAT baseline.",
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
        help.dataset.tip = esc(helpText[id]);
        help.addEventListener("mousemove", event => showTip(event, help.dataset.tip));
        help.addEventListener("mouseleave", hideTip);
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

    function metrics(items) {
      return `<div class="summary">${items.map(item => `
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
          <h3>Base Case</h3>
          <div class="cell-sub">${esc(baseCase.source || "Baseline")} shown as $/kWe; factory, material, and labor categories are included.</div>
          ${coaTable(baseCase.comparison, baseCostColumns(v => fmtKwe(v)), 1.0, false)}
        </div>`;
      }
      const unitLabel = coaUnit === "perkw" ? "$/kWe" : coaUnit === "million" ? "M USD" : "B USD";
      return `<div class="base-case">
        <h3>Base Case</h3>
        <div class="cell-sub">${esc(baseCase.source || "Baseline")} shown as ${unitLabel}; factory, material, and labor categories are included.</div>
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
    }

    function bindTips(root) {
      root.querySelectorAll("[data-tip]").forEach(node => {
        node.addEventListener("mousemove", event => showTip(event, node.dataset.tip));
        node.addEventListener("mouseleave", hideTip);
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
      const m = {left: 108, right: 28, top: 34, bottom: 66};
      const innerW = w - m.left - m.right;
      const innerH = h - m.top - m.bottom;
      const max = niceMax(Math.max(...rows.flatMap(r => [Number(r.TCI || 0), Number(r.OCC || 0)])) * 1.08);
      const y = v => m.top + innerH - (Number(v || 0) / max) * innerH;
      const groupW = innerW / rows.length;
      const barW = Math.max(16, Math.min(42, groupW * 0.34));
      let svg = `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="TCI and OCC by plant">`;
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
        const tciH = m.top + innerH - y(r.TCI);
        const occH = m.top + innerH - y(r.OCC);
        svg += `<rect class="hoverable" data-tip="<b>Plant ${esc(r["Plant number"])}</b><br>TCI: ${fmt(r.TCI)}" x="${cx - barW - 2}" y="${y(r.TCI)}" width="${barW}" height="${tciH}" fill="#2ca02c"></rect>`;
        svg += `<rect class="hoverable" data-tip="<b>Plant ${esc(r["Plant number"])}</b><br>OCC: ${fmt(r.OCC)}" x="${cx + 2}" y="${y(r.OCC)}" width="${barW}" height="${occH}" fill="#1f77b4"></rect>`;
        if (idx % Math.ceil(rows.length / 8) === 0 || rows.length <= 8) {
          svg += `<text x="${cx}" y="${h - 28}" text-anchor="middle" fill="#596775" font-size="15" font-weight="700">${esc(r["Plant number"])}</text>`;
        }
      });
      svg += `<text x="${m.left + innerW / 2}" y="${h - 6}" text-anchor="middle" fill="#596775" font-size="15" font-weight="700">Plant number</text>`;
      svg += `<rect x="${w - 170}" y="14" width="14" height="14" fill="#2ca02c"></rect><text x="${w - 148}" y="26" fill="#596775" font-size="15" font-weight="700">TCI</text>`;
      svg += `<rect x="${w - 94}" y="14" width="14" height="14" fill="#1f77b4"></rect><text x="${w - 72}" y="26" fill="#596775" font-size="15" font-weight="700">OCC</text>`;
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

    function iatBlock(iat, title = "") {
      let html = title ? `<div class="scenario-card"><h4>${title}</h4>` : "";
      html += metrics([
        {label: "Base case OCC", value: fmtKwe(iat.input_occ_per_kw)},
        {label: "WE-FOAK OCC ($/kWe)", value: fmtKwe(iat.adjusted_occ_per_kw)},
        {label: "OCC adjustment factor", value: fmt(iat.occ_adjustment_factor)},
        {label: "Country", value: iat.country}
      ]);
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

    function occComparisonChart(rows) {
      if (!rows || !rows.length) return "";
      const countries = [...new Set(rows.map(r => r.country))];
      const scenarios = [...new Set(rows.map(r => r.scenario))];
      const w = 1120, h = 430;
      const m = {left: 108, right: 28, top: 46, bottom: 72};
      const innerW = w - m.left - m.right;
      const innerH = h - m.top - m.bottom;
      const maxVal = Math.max(...rows.map(r => Number(r.adjusted_occ_per_kw || 0))) * 1.12;
      const yScale = v => m.top + innerH - (Number(v || 0) / maxVal) * innerH;
      const palette = ["#4e79a7", "#f28e2b", "#59a14f", "#b07aa1"];
      const groupW = innerW / countries.length;
      const barW = Math.max(28, Math.min(58, groupW / Math.max(1, scenarios.length) * 0.62));
      let svg = `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="OCC comparison by country">`;
      for (let i = 0; i <= 4; i++) {
        const v = maxVal * i / 4;
        const yy = yScale(v);
        svg += `<line stroke="#d5e0ea" x1="${m.left}" y1="${yy}" x2="${w - m.right}" y2="${yy}"></line>`;
        svg += `<text x="${m.left - 10}" y="${yy + 5}" text-anchor="end" fill="#41566d" font-size="15" font-weight="700">${fmt(Math.round(v))}</text>`;
      }
      svg += `<line x1="${m.left}" y1="${m.top + innerH}" x2="${w - m.right}" y2="${m.top + innerH}" stroke="#8093a7"></line>`;
      svg += `<text transform="translate(18,${m.top + innerH / 2}) rotate(-90)" text-anchor="middle" fill="#41566d" font-size="15" font-weight="700">Adjusted OCC ($/kWe)</text>`;
      countries.forEach((country, ci) => {
        const cxBase = m.left + groupW * ci + groupW / 2 - (scenarios.length - 1) * (barW + 6) / 2;
        scenarios.forEach((scenario, si) => {
          const row = rows.find(r => r.country === country && r.scenario === scenario);
          if (!row) return;
          const val = Number(row.adjusted_occ_per_kw || 0);
          const x = cxBase + si * (barW + 6);
          const barH = innerH - (yScale(val) - m.top);
          const color = palette[si % palette.length];
          svg += `<rect class="hoverable" data-tip="<b>${esc(country)} — ${esc(scenario)}</b><br>Adjusted OCC: ${fmt(Math.round(val))} $/kWe" x="${x}" y="${yScale(val)}" width="${barW}" height="${barH}" fill="${color}" rx="2"></rect>`;
          svg += `<text x="${x + barW / 2}" y="${yScale(val) - 8}" text-anchor="middle" fill="#30465c" font-size="13" font-weight="800">$${fmt(Math.round(val))}</text>`;
        });
        svg += `<text x="${m.left + groupW * ci + groupW / 2}" y="${h - 22}" text-anchor="middle" fill="#41566d" font-size="15" font-weight="700">${esc(country)}</text>`;
      });
      scenarios.forEach((scenario, si) => {
        const lx = m.left + si * 170;
        svg += `<rect x="${lx}" y="${m.top - 28}" width="14" height="14" fill="${palette[si % palette.length]}"></rect>`;
        svg += `<text x="${lx + 22}" y="${m.top - 16}" fill="#41566d" font-size="14" font-weight="700">${esc(scenario)}</text>`;
      });
      svg += `</svg>`;
      return svg;
    }

    function localForeignChart(rows) {
      if (!rows || !rows.length) return "";
      const countryOrder = [...new Set(rows.map(r => r.country))];
      const scenarioOrder = [...new Set(rows.map(r => r.scenario))];
      rows = [...rows].sort((a, b) => {
        const countryDiff = countryOrder.indexOf(a.country) - countryOrder.indexOf(b.country);
        if (countryDiff !== 0) return countryDiff;
        return scenarioOrder.indexOf(a.scenario) - scenarioOrder.indexOf(b.scenario);
      });
      const w = 1120, h = 440;
      const m = {left: 108, right: 28, top: 42, bottom: 126};
      const innerW = w - m.left - m.right;
      const innerH = h - m.top - m.bottom;
      const maxVal = Math.max(...rows.map(r => Number(r.adjusted_occ_per_kw || 0))) * 1.12;
      const yScale = v => m.top + innerH - (Number(v || 0) / maxVal) * innerH;
      const step = innerW / rows.length;
      const barW = Math.max(28, Math.min(58, step * 0.62));
      let svg = `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="Local vs Foreign OCC breakdown">`;
      for (let i = 0; i <= 4; i++) {
        const v = maxVal * i / 4;
        const yy = yScale(v);
        svg += `<line stroke="#d5e0ea" x1="${m.left}" y1="${yy}" x2="${w - m.right}" y2="${yy}"></line>`;
        svg += `<text x="${m.left - 10}" y="${yy + 5}" text-anchor="end" fill="#41566d" font-size="15" font-weight="700">${fmt(Math.round(v))}</text>`;
      }
      svg += `<line x1="${m.left}" y1="${m.top + innerH}" x2="${w - m.right}" y2="${m.top + innerH}" stroke="#8093a7"></line>`;
      svg += `<text transform="translate(18,${m.top + innerH / 2}) rotate(-90)" text-anchor="middle" fill="#41566d" font-size="15" font-weight="700">OCC ($/kWe)</text>`;
      rows.forEach((r, idx) => {
        const foreign = Number(r.foreign_per_kw || 0);
        const local = Number(r.local_per_kw || 0);
        const x = m.left + step * idx + (step - barW) / 2;
        const yForeign = yScale(foreign + local);
        const yLocal = yScale(local);
        const localH = Math.max(1, yScale(0) - yLocal);
        const foreignH = Math.max(1, yLocal - yForeign);
        svg += `<rect class="hoverable" data-tip="<b>${esc(r.label)}</b><br>Foreign: ${fmt(Math.round(foreign))} $/kWe" x="${x}" y="${yLocal - foreignH}" width="${barW}" height="${foreignH}" fill="#9c755f" rx="1"></rect>`;
        svg += `<rect class="hoverable" data-tip="<b>${esc(r.label)}</b><br>Local: ${fmt(Math.round(local))} $/kWe" x="${x}" y="${yLocal}" width="${barW}" height="${localH}" fill="#4e79a7" rx="1"></rect>`;
        if (foreign > maxVal * 0.05) svg += `<text x="${x + barW / 2}" y="${yLocal - foreignH / 2 + 4}" text-anchor="middle" fill="#fff" font-size="12" font-weight="800">$${fmt(Math.round(foreign))}</text>`;
        if (local > maxVal * 0.05) svg += `<text x="${x + barW / 2}" y="${yLocal + localH / 2 + 4}" text-anchor="middle" fill="#fff" font-size="12" font-weight="800">$${fmt(Math.round(local))}</text>`;
        const country = String(r.country || "").slice(0, 16);
        const scenario = String(r.scenario || "").slice(0, 18);
        svg += `<text x="${x + barW / 2}" y="${h - 96}" text-anchor="middle" fill="#41566d" font-size="12" font-weight="800">${esc(scenario)}</text>`;
        svg += `<text x="${x + barW / 2}" y="${h - 78}" text-anchor="middle" fill="#41566d" font-size="12" font-weight="700">${esc(country)}</text>`;
      });
      svg += `<rect x="${m.left}" y="${h - 28}" width="14" height="14" fill="#4e79a7"></rect><text x="${m.left + 22}" y="${h - 16}" fill="#41566d" font-size="14" font-weight="700">Local (domestically sourced)</text>`;
      svg += `<rect x="${m.left + 280}" y="${h - 28}" width="14" height="14" fill="#9c755f"></rect><text x="${m.left + 302}" y="${h - 16}" fill="#41566d" font-size="14" font-weight="700">Foreign / imported</text>`;
      svg += `</svg>`;
      return svg;
    }

    function render(data) {
      lastData = data;
      const result = $("result");
      let html = `<div class="hero"><h2>${data.workflow_label}</h2><p>ACCERT workflow results with saved outputs and interactive cost plots.</p></div>`;
      const isStandaloneMultiCountryIat = data.workflow === "iat_only"
        && data.iat
        && data.iat.country_results
        && data.iat.country_results.some(cr => cr.data && cr.data.scenarios && cr.data.scenarios.length);
      if (!isStandaloneMultiCountryIat) {
        html += links(data.files);
      }
      html += baseCaseBlock(data.base_case);
      if (data.iat) {
        if (data.iat.country_results && data.iat.country_results.length) {
          if (isStandaloneMultiCountryIat) {
            html += `<div class="tabs">`;
            data.iat.country_results.forEach((cr, idx) => {
              html += `<button class="${idx === 0 ? "active" : ""}" data-tab="iat-country-${tabSafe(cr.country)}">${esc(cr.country)}</button>`;
            });
            html += `<button data-tab="iat-comparison">Country Comparison</button>`;
            html += `</div>`;
            data.iat.country_results.forEach((cr, idx) => {
              const d = cr.data;
              html += `<div id="tab-iat-country-${tabSafe(cr.country)}" class="tab-panel ${idx === 0 ? "active" : ""}">`;
              html += `<h3>${esc(cr.country)}</h3>`;
              html += fileLink(`IAT CSV (${cr.country})`, data.files && data.files[`IAT CSV (${cr.country})`]);
              html += table(d.summary, [
                {key: "Scenario", label: "Scenario"},
                {key: "Input OCC", label: "Input OCC ($/kWe)", format: fmt},
                {key: "Adjusted OCC", label: "Adjusted OCC ($/kWe)", format: fmt},
                {key: "Adjustment Ratio of OCC", label: "OCC Ratio", format: fmt}
              ]);
              d.scenarios.forEach((s, i) => { html += iatBlock(s, `${s.scenario || `Scenario ${i + 1}`} result`); });
              html += `</div>`;
            });
            html += `<div id="tab-iat-comparison" class="tab-panel">
              <div class="chart-grid">
                <div class="chart-panel"><h3>OCC Comparison by Country</h3><div id="iatOccCompChart"></div></div>
                <div class="chart-panel"><h3>Local vs Foreign OCC</h3><div id="iatLfChart"></div></div>
              </div>
            </div>`;
          } else {
            html += `<div class="tabs">
              <button class="active" data-tab="iat-results">IAT Results</button>
              <button data-tab="iat-comparison">Country Comparison</button>
            </div>`;
            html += `<div id="tab-iat-results" class="tab-panel active">`;
            data.iat.country_results.forEach(cr => {
              const d = cr.data;
              html += `<h3>${esc(cr.country)}</h3>`;
              html += fileLink(`IAT CSV (${cr.country})`, data.files && data.files[`IAT CSV (${cr.country})`]);
              html += iatBlock(d);
            });
            html += `</div>`;
            html += `<div id="tab-iat-comparison" class="tab-panel">
              <div class="chart-grid">
                <div class="chart-panel"><h3>OCC Comparison by Country</h3><div id="iatOccCompChart"></div></div>
                <div class="chart-panel"><h3>Local vs Foreign OCC</h3><div id="iatLfChart"></div></div>
              </div>
            </div>`;
          }
        } else {
          html += `<h3>IAT Result</h3>`;
          if (data.iat.scenarios && data.iat.scenarios.length) {
            html += table(data.iat.summary, [
              {key: "Scenario", label: "Scenario"},
              {key: "Input OCC", label: "Input OCC ($/kWe)", format: fmt},
              {key: "Adjusted OCC", label: "Adjusted OCC ($/kWe)", format: fmt},
              {key: "Adjustment Ratio of OCC", label: "OCC Ratio", format: fmt}
            ]);
            data.iat.scenarios.forEach((scenario, idx) => {
              html += iatBlock(scenario, `${scenario.scenario || `Scenario ${idx + 1}`} result`);
            });
          } else {
            html += iatBlock(data.iat);
          }
        }
      }
      if (data.crt) {
        html += `<h3>CRT Result</h3>`;
        html += `<div class="result-note">The IAT value above is the internationally adjusted WE-FOAK OCC baseline. CRT recalculates FOAK from that baseline using the CRT fixed inputs and first-unit project effects, including factory-equipment inputs, land, construction/startup duration, financing, design completion, and FOAK execution assumptions, so the CRT FOAK OCC can differ from the WE-FOAK OCC.</div>`;
        html += metrics([
          {label: "FOAK OCC ($/kW)", value: fmtInt(data.crt.occ_1)},
          {label: "NOAK OCC ($/kW)", value: fmtInt(data.crt.occ_noak)},
          {label: "Average OCC ($/kW)", value: fmtInt(data.crt.avg_occ)},
          {label: "OCC reduction (%)", value: fmtInt(data.crt.occ_reduction_percent)}
        ]);
        html += metrics([
          {label: "FOAK TCI ($/kW)", value: fmtInt(data.crt.tci_1)},
          {label: "NOAK TCI ($/kW)", value: fmtInt(data.crt.tci_noak)},
          {label: "Average TCI ($/kW)", value: fmtInt(data.crt.avg_tci)},
          {label: "Average duration (months)", value: fmtInt(data.crt.avg_duration)}
        ]);
        html += metrics([
          {label: `Years to build ${fmtInt(data.crt.num_noak)} plants`, value: `${fmtInt(data.crt.years_to_noak)} years`},
          {label: `Years to build ${fmtInt(data.crt.num_orders)} plants`, value: `${fmtInt(data.crt.years_to_orderbook)} years`}
        ]);
        html += `<div class="tabs">
          <button class="active" data-tab="capital">Capital Cost</button>
          <button data-tab="levers">Reduction Levers</button>
          <button data-tab="durations">Construction Durations</button>
          <button data-tab="breakdown">Cost Breakdown</button>
          <button data-tab="dashboard">Dashboard Image</button>
          <button data-tab="results">Results Table</button>
        </div>`;
        html += `<div id="tab-capital" class="tab-panel active"><div class="chart-grid">
          <div class="chart-panel"><h3>Capital Cost: OCC and TCI</h3><div id="capitalChart"></div></div>
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
        if (data.crt.dashboard_url) {
          const dashUrl = `${data.crt.dashboard_url}?t=${Date.now()}`;
          html += `<div class="download-bar"><span>Dashboard image${data.crt.show_levers ? " with lever table" : " without lever table"}</span><a href="${dashUrl}" target="_blank">Download PNG</a></div>`;
          html += `<img class="dashboard" src="${dashUrl}" alt="CRT dashboard">`;
        }
        html += `</div>`;
        html += `<div id="tab-results" class="tab-panel">
          ${fileLink("Download CRT results CSV", data.files && data.files["CRT results CSV"])}
          ${table(data.crt.plants, crtResultsColumns())}
        </div>`;
      }
      if (data.notes && data.notes.length) {
        html += `<h3>Notes</h3><ul>${data.notes.map(n => `<li>${n}</li>`).join("")}</ul>`;
      }
      result.innerHTML = html;
      document.querySelectorAll(".coaUnit").forEach(select => {
        select.addEventListener("change", event => {
          coaUnit = event.target.value;
          render(lastData);
        });
      });
      if (data.crt) {
        $("capitalChart").innerHTML = capitalChart(data.crt.plants);
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
          $("iatOccCompChart").innerHTML = occComparisonChart(data.iat.comparison_chart || []);
          $("iatLfChart").innerHTML = localForeignChart(data.iat.comparison_chart || []);
          bindTips(result);
        }
        setupCoaTables();
      }
    }

    async function runWorkflow() {
      $("runBtn").disabled = true;
      $("status").className = "status";
      $("status").textContent = "Running...";
      try {
        const response = await fetch("/run", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(payload())
        });
        const data = await response.json();
        if (!response.ok || data.error) throw new Error(data.error || "Run failed");
        render(data);
        $("status").textContent = "Complete";
      } catch (error) {
        $("status").className = "status error";
        $("status").textContent = error.message;
        $("result").innerHTML = `<h2>Run failed</h2><pre>${error.message}</pre>`;
      } finally {
        $("runBtn").disabled = false;
      }
    }

    $("workflow").addEventListener("change", updatePanels);
    $("iatInputMode").addEventListener("change", updatePanels);
    $("iatReactorType").addEventListener("change", () => {
      const isCsvMode = $("iatInputMode").value === "csv" || $("workflow").value === "iat_crt";
      if (isCsvMode) {
        if (!_csvFileContent) updateDefaultCsvPath();
        updateElectricOutputDefault();
      }
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
      cb.addEventListener("change", updateCountryDropdownLabel);
    });
    $("iatBrowseBtn").addEventListener("click", () => $("iatCsvFile").click());
    $("iatCsvFile").addEventListener("change", () => {
      const file = $("iatCsvFile").files[0];
      if (!file) return;
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
    });
    $("crtReactorType").addEventListener("change", () => updateCrtDefaults(true));
    $("runBtn").addEventListener("click", runWorkflow);
    $("resetBtn").addEventListener("click", () => location.reload());
    enhanceLabels();
    updatePanels();
  </script>
</body>
</html>
"""


def _safe_name(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value).strip()).strip("._")
    return name or "accert_gui_run"


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
    iat = payload.get("iat", {})
    if iat.get("input_mode") == "occ":
        return 1.0
    mwe = _num(iat.get("electric_output_mwe"), 0.0)
    if mwe and mwe > 0:
        return mwe * 1000.0
    reactor = str(iat.get("reactor_type") or "")
    return 310.8 * 1000.0 if "SMR" in reactor else 2234.0 * 1000.0


def _iat_metrics(adjusted_costs: pd.DataFrame, power_kwe: float) -> dict:
    summary = _coa_sorted_summary(adjusted_costs)
    occ = _occ_rows(summary)
    input_occ = float(occ["Original Total Cost"].sum())
    adjusted_occ = float(occ["Adjusted Total Cost"].sum())
    factor = adjusted_occ / input_occ if input_occ else 0.0
    lf = occ_local_foreign_totals(adjusted_costs)
    return {
        "input_occ_total": input_occ,
        "adjusted_occ_total": adjusted_occ,
        "occ_adjustment_factor": factor,
        "power_kwe": power_kwe,
        "input_occ_per_kw": input_occ / power_kwe if power_kwe else None,
        "adjusted_occ_per_kw": adjusted_occ / power_kwe if power_kwe else None,
        "local_occ_per_kw": lf["local"] / power_kwe if power_kwe else None,
        "foreign_occ_per_kw": lf["foreign"] / power_kwe if power_kwe else None,
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
        country = countries[0] if countries else iat.get("country", "China")
    config = {
        "reactor_type": iat["reactor_type"],
        "country": country,
        "year_dollar": _int(iat["year_dollar"], 2024),
    }
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
        "land_cost_per_acre_0": _num(crt["land_cost_per_acre_0"], 22_000.0),
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


def _summarize_crt_result(result: dict) -> dict:
    noak = int(result.get("num_NOAK", result.get("Num_orders", 1)))
    num_orders = int(result.get("Num_orders", result.get("num_orders", noak)))
    plant_columns = [
        "Plant number",
        "OCC",
        "TCI",
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
        "tci_1": result.get("TCI_1"),
        "tci_noak": result.get(f"TCI_{noak}"),
        "avg_occ": result.get("avg_OCC"),
        "avg_tci": result.get("avg_TCI"),
        "avg_duration": result.get("avg_duration"),
        "occ_reduction_percent": result.get("occ_reduction_from_FOAK_to_NOAK_percent"),
        "years_to_noak": years_by_plant.get(noak),
        "years_to_orderbook": years_by_plant.get(num_orders),
        "show_levers": False,
        "plants": _records(plants[available]),
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

    if workflow == "iat_only":
        iat = payload["iat"]
        countries = iat.get("countries") or [iat.get("country", "China")]
        if not countries:
            raise ValueError("At least one country must be selected")
        power_kwe = _reactor_power_kwe(payload)
        country_results: list[dict] = []
        comparison_chart: list[dict] = []
        base_scenarios_added: set[str] = set()
        for country in countries:
            country_slug = re.sub(r"[^A-Za-z0-9]+", "_", country.lower())
            iat_csv = OUTPUT_DIR / f"{name}_iat_{country_slug}_adjusted.csv"
            config = _iat_config(payload, iat_csv, country=country)
            if iat["input_mode"] == "occ":
                result = run_occ_scenarios(config)
                summary = _summarize_occ_result(result, power_kwe)
                if "base_case" not in response and result["scenario_results"]:
                    response["base_case"] = _base_case_from_iat_result(result["scenario_results"][0], power_kwe)
                for scenario in summary["scenarios"]:
                    scenario_name = scenario.get("scenario", "")
                    if scenario_name not in base_scenarios_added:
                        comparison_chart.append({
                            "country": "Base case",
                            "scenario": scenario_name,
                            "adjusted_occ_per_kw": scenario.get("input_occ_per_kw"),
                            "local_per_kw": scenario.get("input_occ_per_kw"),
                            "foreign_per_kw": 0.0,
                            "label": f"Base case — {scenario_name}",
                        })
                        base_scenarios_added.add(scenario_name)
                    comparison_chart.append({
                        "country": country,
                        "scenario": scenario_name,
                        "adjusted_occ_per_kw": scenario.get("adjusted_occ_per_kw"),
                        "local_per_kw": scenario.get("local_occ_per_kw"),
                        "foreign_per_kw": scenario.get("foreign_occ_per_kw"),
                        "label": f"{country} — {scenario_name}",
                    })
            else:
                result = run_adjustment(config)
                if iat.get("_prepared_from_accert_csv") and "Converted ACCERT baseline" not in files:
                    files["Converted ACCERT baseline"] = _file_info(Path(iat["_prepared_input_csv"]))
                    notes.append("The raw ACCERT account CSV was converted to CRT/IAT baseline format before IAT was run.")
                summary = _summarize_iat_result(result, power_kwe)
                if "base_case" not in response:
                    response["base_case"] = _base_case_from_iat_result(result, power_kwe)
                comparison_chart.append({
                    "country": "Base case",
                    "scenario": "Original OCC",
                    "adjusted_occ_per_kw": summary.get("input_occ_per_kw"),
                    "local_per_kw": summary.get("input_occ_per_kw"),
                    "foreign_per_kw": 0.0,
                    "label": "Base case",
                })
                comparison_chart.append({
                    "country": country,
                    "scenario": "Adjusted OCC",
                    "adjusted_occ_per_kw": summary.get("adjusted_occ_per_kw"),
                    "local_per_kw": summary.get("local_occ_per_kw"),
                    "foreign_per_kw": summary.get("foreign_occ_per_kw"),
                    "label": country,
                })
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
            title=f"{payload['crt']['reactor_type']} Cost Reduction Framework Tool",
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
        save_dashboard(
            crt_result,
            dashboard,
            title=f"{payload['crt']['reactor_type']} {_crt_countries[0]} Cost Reduction Framework Tool",
            show_levers=bool(payload["crt"].get("show_levers", True)),
        )
        response["iat"] = _summarize_iat_result(iat_result, _reactor_power_kwe(payload))
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
        if self.path in {"/", "/index.html"}:
            self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
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
        except Exception as exc:
            body = {
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
            self._send(500, json.dumps(body).encode("utf-8"), "application/json")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}"
    print(f"ACCERT IAT and CRT GUI running at {url}")
    print(f"Outputs will be written to {OUTPUT_DIR}")
    if "--open" in sys.argv:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    server.serve_forever()


if __name__ == "__main__":
    main()
