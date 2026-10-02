import inspect
import re

import pandas as pd
import pytest
import pytest

from tutorial.gui import crt_iat_gui


def _gui_payload(csv_content: str) -> dict:
    return {
        "workflow": "iat_crt",
        "output_name": "pytest_gui_accert_iat_crt",
        "iat": {
            "input_mode": "csv",
            "reactor_type": "ACCERT output-LR",
            "countries": ["China"],
            "year_dollar": 2024,
            "input_csv": None,
            "csv_content": csv_content,
            "csv_filename": "ap1000_upd_acc_test.csv",
            "electric_output_mwe": 2234,
            "scenario_count": 1,
            "occ_values": [5750],
        },
        "crt": {
            "reactor_type": "AP1000",
            "baseline_csv": None,
            "baseline_csv_content": None,
            "baseline_csv_filename": None,
            "f_22": 250_000_000,
            "f_2321": 150_000_000,
            "land_cost_per_acre_0": 22_000,
            "startup_0": 25,
            "construction_duration_0": 76,
            "total_20s_labor_hours": 51_112_635.470754,
            "staggering_ratio": 0.75,
            "show_levers": False,
        },
        "levers": {
            "num_orders": 2,
            "num_NOAK": 2,
            "itc_percent": 0,
            "n_itc": 0,
            "interest_percent": 6,
            "design_completion_percent": 70,
            "design_maturity": 1,
            "proc_exp": 0.5,
            "N_proc": 3,
            "ce_exp": 0.5,
            "N_cons": 5,
            "ae_exp": 0.5,
            "N_AE": 4,
            "standardization_percent": 80,
            "modularity_code": 0,
            "bop_grade_code": 0,
            "rb_grade_code": 0,
        },
    }


def test_gui_iat_crt_converts_raw_accert_account_csv(monkeypatch, tmp_path):
    raw_accert = pd.DataFrame(
        [
            {"code_of_account": "211", "account_description": "Yardwork", "total_cost": 1_000_000.0},
            {"code_of_account": "212", "account_description": "Reactor building", "total_cost": 2_000_000.0},
            {"code_of_account": "22", "account_description": "Reactor plant equipment", "total_cost": 3_000_000.0},
            {"code_of_account": "23", "account_description": "Turbine plant equipment", "total_cost": 4_000_000.0},
        ]
    )
    monkeypatch.setattr(crt_iat_gui, "OUTPUT_DIR", tmp_path)

    result = crt_iat_gui.run_workflow(_gui_payload(raw_accert.to_csv(index=False)))

    converted = tmp_path / "pytest_gui_accert_iat_crt_accert_baseline_for_iat_crt.csv"
    assert converted.exists()
    converted_df = pd.read_csv(converted)
    assert {"Account", "Title", "Total Cost (USD)", "Factory Equipment Cost", "Site Labor Cost", "Site Material Cost"}.issubset(converted_df.columns)
    assert "Converted ACCERT baseline" in result["files"]
    assert "CRT results CSV" in result["files"]
    assert (tmp_path / "pytest_gui_accert_iat_crt_crt_results.csv").exists()
    assert result["base_case"]["comparison"]
    assert result["base_case"]["comparison"][0]["Total Cost"] > 0
    assert result["iat"]["comparison"]
    assert result["crt"]["plants"]
    assert result["crt"]["num_noak"] == 2
    assert result["crt"]["num_orders"] == 2
    assert result["crt"]["years_to_noak"] > 0
    assert result["crt"]["years_to_orderbook"] > 0
    assert crt_iat_gui._crt_config(_gui_payload(raw_accert.to_csv(index=False)))["construction_duration_0"] == pytest.approx(76)
    assert result["crt"]["plants"][0]["Construction duration"] > 0


def test_gui_crt_only_converts_raw_accert_baseline(monkeypatch, tmp_path):
    raw_accert = pd.DataFrame(
        [
            {"code_of_account": "211", "account_description": "Yardwork", "total_cost": 1_000_000.0},
            {"code_of_account": "212", "account_description": "Reactor building", "total_cost": 2_000_000.0},
            {"code_of_account": "22", "account_description": "Reactor plant equipment", "total_cost": 3_000_000.0},
            {"code_of_account": "23", "account_description": "Turbine plant equipment", "total_cost": 4_000_000.0},
        ]
    )
    payload = _gui_payload("")
    payload["workflow"] = "crt_only"
    payload["crt"]["baseline_csv_content"] = raw_accert.to_csv(index=False)
    payload["crt"]["baseline_csv_filename"] = "ap1000_upd_acc_test.csv"
    monkeypatch.setattr(crt_iat_gui, "OUTPUT_DIR", tmp_path)

    result = crt_iat_gui.run_workflow(payload)

    assert (tmp_path / "pytest_gui_accert_iat_crt_accert_baseline_for_crt.csv").exists()
    assert "Converted ACCERT baseline" in result["files"]
    assert "CRT results CSV" in result["files"]
    assert result["base_case"]["comparison"]
    assert result["crt"]["plants"]
    base_coas = [row["COA"] for row in result["base_case"]["comparison"]]
    assert base_coas.index("21") == base_coas.index("20") + 1
    assert base_coas.index("22") == base_coas.index("21") + 1


def test_gui_accepts_large_reactor_with_ap1000(monkeypatch, tmp_path):
    payload = _gui_payload("")
    payload["iat"]["input_csv"] = "src/crt/data/AP1000_baseline.csv"
    monkeypatch.setattr(crt_iat_gui, "OUTPUT_DIR", tmp_path)
    result = crt_iat_gui.run_workflow(payload)
    assert result["crt"]["plants"]


def test_gui_rejects_large_reactor_with_sfr():
    payload = _gui_payload("")
    payload["crt"]["reactor_type"] = "SFR"

    with pytest.raises(ValueError, match="not compatible with IAT reactor type"):
        crt_iat_gui.run_workflow(payload)


def test_gui_rejects_large_reactor_with_htgr():
    payload = _gui_payload("")
    payload["crt"]["reactor_type"] = "HTGR"

    with pytest.raises(ValueError, match="not compatible with IAT reactor type"):
        crt_iat_gui.run_workflow(payload)


def test_gui_accepts_smr_with_sfr(monkeypatch, tmp_path):
    payload = _gui_payload("")
    payload["iat"]["reactor_type"] = "ACCERT output-SMR"
    payload["crt"]["reactor_type"] = "SFR"
    payload["iat"]["electric_output_mwe"] = 310.8
    payload["iat"]["input_csv"] = "src/crt/data/SFR_baseline.csv"
    monkeypatch.setattr(crt_iat_gui, "OUTPUT_DIR", tmp_path)

    result = crt_iat_gui.run_workflow(payload)
    assert result["crt"]["plants"]


def test_gui_accepts_smr_with_htgr_and_uses_iat_output(monkeypatch, tmp_path):
    payload = _gui_payload("")
    payload["iat"]["reactor_type"] = "ACCERT output-SMR"
    payload["iat"]["input_csv"] = "src/crt/data/HTGR_baseline.csv"
    payload["iat"]["electric_output_mwe"] = 1056
    payload["iat"]["baseline_reactor_type"] = "HTGR"
    payload["crt"]["reactor_type"] = "HTGR"
    payload["crt"]["baseline_csv_content"] = "not-used-in-iat-crt"
    monkeypatch.setattr(crt_iat_gui, "OUTPUT_DIR", tmp_path)

    result = crt_iat_gui.run_workflow(payload)

    assert result["crt"]["plants"]
    assert result["files"]["IAT adjusted CSV"]


def test_gui_honors_only_iat_output_for_iat_crt_baseline(monkeypatch, tmp_path):
    payload = _gui_payload("")
    payload["iat"]["input_csv"] = "src/crt/data/AP1000_baseline.csv"
    payload["crt"]["baseline_csv_content"] = "not-used-in-iat-crt"
    monkeypatch.setattr(crt_iat_gui, "OUTPUT_DIR", tmp_path)

    result = crt_iat_gui.run_workflow(payload)

    assert result["crt"]["plants"]
    assert "Optional CRT baseline" not in result["notes"]


def test_capital_chart_uses_calculated_itc_portion_pattern():
    assert 'id="itcHatch"' in crt_iat_gui.HTML
    assert "ITC reduction" in crt_iat_gui.HTML
    assert 'fill="url(#itcHatch)"' in crt_iat_gui.HTML


def test_capital_cost_records_split_tci_into_nci_and_actual_itc_reduction():
    rows = pd.DataFrame(
        [
            {"Plant number": 1, "TCI": 6000.0, "NCI": 4000.0, "OCC": 5000.0, "Net OCC": 3200.0},
            {"Plant number": 2, "TCI": 5000.0, "NCI": None, "OCC": 4200.0, "Net OCC": None},
        ]
    )

    records = crt_iat_gui._capital_cost_records(rows)

    assert records[0]["NCI"] == pytest.approx(4000.0)
    assert records[0]["ITC reduction"] == pytest.approx(2000.0)
    assert records[0]["TCI ITC reduction"] == pytest.approx(2000.0)
    assert records[0]["OCC ITC reduction"] == pytest.approx(1800.0)
    assert records[0]["NCI"] + records[0]["ITC reduction"] == pytest.approx(records[0]["TCI"])
    assert records[1]["NCI"] == pytest.approx(records[1]["TCI"])
    assert records[1]["ITC reduction"] == pytest.approx(0.0)
    assert records[1]["TCI ITC reduction"] == pytest.approx(0.0)
    assert records[1]["OCC ITC reduction"] == pytest.approx(0.0)
    assert records[0]["OCC"] == pytest.approx(5000.0)
    assert records[0]["Net OCC"] == pytest.approx(3200.0)


def test_capital_chart_uses_trace_specific_tooltips_and_reductions():
    assert 'const tciReduction = Math.max(0, Number(r["TCI ITC reduction"] ?? (tci - netTci)));' in crt_iat_gui.HTML
    assert 'const occReduction = Math.max(0, Number(r["OCC ITC reduction"] ?? (occ - netOccValueActual)));' in crt_iat_gui.HTML
    assert 'const tciTip =' in crt_iat_gui.HTML
    assert 'const occTip =' in crt_iat_gui.HTML
    assert 'data-tip="${tciTip}"' in crt_iat_gui.HTML
    assert 'data-tip="${occTip}"' in crt_iat_gui.HTML
    assert 'TCI / Net TCI ($/kW)' in crt_iat_gui.HTML
    assert 'OCC / Net OCC ($/kW)' in crt_iat_gui.HTML
    assert "tciReduction > 0" in crt_iat_gui.HTML
    assert "occReduction > 0" in crt_iat_gui.HTML
    assert "TCI ($/kW)" in crt_iat_gui.HTML
    assert "OCC ($/kW)" in crt_iat_gui.HTML


def test_gui_display_units_convert_to_native_crt_units():
    assert crt_iat_gui.land_cost_from_gui(22) == pytest.approx(22_000.0)
    assert crt_iat_gui.land_cost_from_gui(25) == pytest.approx(25_000.0)
    assert crt_iat_gui.labor_hours_from_gui(51.11) == pytest.approx(51_110_000.0)
    assert crt_iat_gui.labor_hours_from_gui(52.5) == pytest.approx(52_500_000.0)


def test_gui_defaults_are_derived_from_native_reactor_config():
    ap1000 = crt_iat_gui.REACTOR_CONFIGS["AP1000"]
    assert crt_iat_gui.DEFAULT_LAND_COST_PER_ACRE == pytest.approx(22_000.0)
    assert crt_iat_gui.land_cost_from_gui(
        crt_iat_gui.DEFAULT_LAND_COST_PER_ACRE / crt_iat_gui.LAND_COST_PER_GUI_UNIT
    ) == pytest.approx(22_000.0)
    assert ap1000["labor_hours_20s"] / crt_iat_gui.LABOR_HOURS_PER_MILLION == pytest.approx(51.112635470753975)


def test_gui_uses_human_scale_labels_and_explicit_conversion_layer():
    assert 'Land Cost ($k/acre)' in crt_iat_gui.HTML
    assert 'Total labor hours (million)' in crt_iat_gui.HTML
    assert "landCostToBackend(numberValue(\"landCost\"))" in crt_iat_gui.HTML
    assert "laborHoursToBackend(numberValue(\"total20sLaborHours\"))" in crt_iat_gui.HTML


def test_gui_groups_conditional_inputs_and_aligns_crt_cost_fields():
    assert 'class="triple crt-cost-row"' in crt_iat_gui.HTML
    assert 'class="baseline-control-row"' in crt_iat_gui.HTML
    assert 'id="iatUploadGroup"' in crt_iat_gui.HTML
    assert 'id="crtReactorTypeGroup"' in crt_iat_gui.HTML
    assert '$("iatUploadGroup").classList.toggle("hidden", !isCustom)' in crt_iat_gui.HTML
    assert '$("crtReactorTypeGroup").classList.toggle("hidden", workflow !== "crt_only")' in crt_iat_gui.HTML


def test_capital_chart_keeps_paired_bars_compact():
    assert "Math.min(34, groupW * 0.28)" in crt_iat_gui.HTML


def test_capital_chart_uses_consistent_outlines_and_compact_legend_tooltip():
    assert 'top: 58' in crt_iat_gui.HTML
    assert 'fill="#2ca02c" stroke="#2ca02c" stroke-width="1.5"' in crt_iat_gui.HTML
    assert 'TCI / Net TCI ($/kW)' in crt_iat_gui.HTML
    assert 'OCC / Net OCC ($/kW)' in crt_iat_gui.HTML
    assert 'ITC Reduction ($/kW)' in crt_iat_gui.HTML
    assert 'TCI / Net TCI' in crt_iat_gui.HTML
    assert 'OCC / Net OCC' in crt_iat_gui.HTML


def test_capital_tooltip_keeps_gross_net_pairs_together():
    assert '#tooltip .tip-label' in crt_iat_gui.HTML
    assert 'white-space: nowrap' in crt_iat_gui.HTML
    assert "class='tip-label'>TCI / Net TCI ($/kW)</span><span class='tip-value'>" in crt_iat_gui.HTML
    assert "class='tip-label'>OCC / Net OCC ($/kW)</span><span class='tip-value'>" in crt_iat_gui.HTML


def test_phase_one_gui_has_three_step_input_flow_and_advanced_sections():
    assert 'class="workflow-steps"' in crt_iat_gui.HTML
    assert 'data-step="1"' in crt_iat_gui.HTML
    assert 'data-step="2"' in crt_iat_gui.HTML
    assert 'data-step="3"' in crt_iat_gui.HTML
    assert '<details class="advanced-section"' in crt_iat_gui.HTML
    assert 'Advanced IAT assumptions' in crt_iat_gui.HTML
    assert 'Advanced CRT assumptions' in crt_iat_gui.HTML
    assert 'CRT levers' in crt_iat_gui.HTML


def test_phase_one_gui_explains_terms_and_exposes_run_summary_states():
    for term in ["International Adjustment Tool", "Cost Reduction Tool", "First-of-a-Kind", "Nth-of-a-Kind", "cost-reduction levers"]:
        assert term in crt_iat_gui.HTML
    assert 'id="runSummary"' in crt_iat_gui.HTML
    assert 'id="processingStage"' in crt_iat_gui.HTML
    assert 'id="emptyState"' in crt_iat_gui.HTML
    assert "Running IAT" in crt_iat_gui.HTML
    assert "Running CRT" in crt_iat_gui.HTML


def test_phase_one_results_include_prominent_summary_cards():
    for label in ["Total OCC", "Adjusted OCC", "$/kW", "Cost change", "Construction duration"]:
        assert label in crt_iat_gui.HTML
    assert 'class="result-summary-cards"' in crt_iat_gui.HTML


def test_empty_state_updates_for_selected_workflow_and_terms_are_visible():
    assert 'id="emptyTitle"' in crt_iat_gui.HTML
    assert 'id="emptyDescription"' in crt_iat_gui.HTML
    assert 'id="termGuide"' in crt_iat_gui.HTML
    assert 'function updateEmptyState()' in crt_iat_gui.HTML
    assert 'IAT results will appear here' in crt_iat_gui.HTML
    assert 'CRT results will appear here' in crt_iat_gui.HTML
    assert 'Connected IAT → CRT results will appear here' in crt_iat_gui.HTML
    assert 'color: var(--ink);' in crt_iat_gui.HTML


def test_combined_results_keep_iat_summary_before_crt_details():
    assert 'class="iat-results-section"' in crt_iat_gui.HTML
    assert 'IAT Results' in crt_iat_gui.HTML
    assert 'Original OCC' in crt_iat_gui.HTML
    assert 'IAT-adjusted OCC' in crt_iat_gui.HTML
    assert 'OCC Change' in crt_iat_gui.HTML
    assert 'CRT Results' in crt_iat_gui.HTML
    assert 'class="iat-breakdown"' in crt_iat_gui.HTML
    assert 'crt-key-cards' in crt_iat_gui.HTML
    assert 'if (!data.iat) html += resultSummaryCards(data);' in crt_iat_gui.HTML


def test_dashboard_title_uses_custom_display_name_but_sanitizes_filename():
    assert crt_iat_gui._dashboard_title("China AP1000 – Fast Learning", "iat_crt", "AP1000", "China") == "China AP1000 – Fast Learning"
    assert crt_iat_gui._dashboard_title("AP1000_China_Fast_Learning", "iat_crt", "AP1000", "China") == "AP1000 China Fast Learning"
    assert crt_iat_gui._dashboard_title("", "crt_only", "AP1000", "") == "AP1000 CRT Dashboard"
    assert crt_iat_gui._safe_name("China AP1000 – Fast Learning") == "China_AP1000_Fast_Learning"


def test_crt_summary_uses_consistent_metric_grid_and_conditional_gross_net_values():
    assert "function crtResultsGrid(crt)" in crt_iat_gui.HTML
    assert "function crtMetricGroup(title, explanation, cards" in crt_iat_gui.HTML
    assert "crt-metric-cards" in crt_iat_gui.HTML
    assert "Construction duration (months)" in crt_iat_gui.HTML
    assert "function crtGridValue(gross, net, reduction)" in crt_iat_gui.HTML
    assert "reduction > 0" in crt_iat_gui.HTML


def test_output_name_is_generated_from_reactor_and_country_without_overwriting_custom_text():
    assert "function outputNameParts()" in crt_iat_gui.HTML
    assert "function updateOutputName()" in crt_iat_gui.HTML
    assert "_outputNameCustomized" in crt_iat_gui.HTML
    assert "${parts.reactor} ${parts.country} Baseline" in crt_iat_gui.HTML


def test_crt_result_cards_explain_occ_tci_and_duration_accessibly():
    assert "Overnight Capital Cost (OCC)" in crt_iat_gui.HTML
    assert "Total Capital Investment (TCI)" in crt_iat_gui.HTML
    assert "Construction Duration" in crt_iat_gui.HTML
    assert "excluding financing costs incurred during construction" in crt_iat_gui.HTML
    assert "60-series financing costs, including interest during construction" in crt_iat_gui.HTML
    assert "info-tip" in crt_iat_gui.HTML
    assert 'aria-label="Explain ${esc(label)}"' in crt_iat_gui.HTML
    assert 'node.addEventListener("focus"' in crt_iat_gui.HTML
    assert 'node.addEventListener("click"' in crt_iat_gui.HTML
    assert "class='tip-label'" in crt_iat_gui.HTML
    assert 'data-tip="${tciTip}"' in crt_iat_gui.HTML
    assert 'data-tip="${occTip}"' in crt_iat_gui.HTML


def test_crt_summary_cards_show_foak_gross_and_net_values():
    assert 'FOAK OCC / Net OCC ($/kW)' in crt_iat_gui.HTML
    assert 'FOAK TCI / Net TCI ($/kW)' in crt_iat_gui.HTML
    assert 'crt.net_occ_1' in crt_iat_gui.HTML
    assert 'crt.net_tci_1' in crt_iat_gui.HTML


def test_crt_fixed_inputs_use_short_labels_and_structural_field_alignment():
    assert ".row > div" in crt_iat_gui.HTML
    assert ".triple > div" in crt_iat_gui.HTML
    assert "Account 22 ($M)" in crt_iat_gui.HTML
    assert "Account 232.1 ($M)" in crt_iat_gui.HTML
    assert "Land Cost ($k/acre)" in crt_iat_gui.HTML
    assert "Construction duration (months)" in crt_iat_gui.HTML
    assert "Total labor hours (million)" in crt_iat_gui.HTML


def test_gui_startup_opens_local_address_automatically():
    source = inspect.getsource(crt_iat_gui.main)
    assert "webbrowser.open(url)" in source
    assert "if \"--open\" in sys.argv" not in source


def test_gui_http_handler_does_not_mask_request_errors_with_broken_pipe():
    source = inspect.getsource(crt_iat_gui.Handler.do_POST)
    assert "except BrokenPipeError" in source
    assert "traceback.print_exc()" in source
