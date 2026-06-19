import pandas as pd
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
