import csv
import pickle
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

from crf import (
    accert_output_to_crf_baseline,
    levers_to_dataframe,
    occ_reduction_from_foak_to_noak,
    results_to_dataframe,
    run_one_scenario,
    run_sampling_from_excel,
    save_dashboard,
    tci_reduction_from_foak_to_noak,
    waterfall_to_dataframe,
)
from crf.api import normalize_levers
from crf.io.excel_inputs import InputStore
from crf.model.schedule import build_schedule_timeline
from crf.sampling.lever_schema import EXCEL_NAME_TO_ID_ORDERED


def _config():
    return {
        "reactor_type": "AP1000",
        "f_22": 250_000_000,
        "f_2321": 150_000_000,
        "land_cost_per_acre_0": 22_000,
        "construction_duration_0": 76,
        "startup_0": 28,
        "staggering_ratio": 0.75,
    }


def _levers(**overrides):
    levers = {
        "num_orders": 2,
        "num_NOAK": 2,
        "itc_percent": 30,
        "n_itc": 1,
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
        "modularity_code": 1,
        "bop_grade_code": 1,
        "rb_grade_code": 0,
    }
    levers.update(overrides)
    return levers


def _lever_workbook(path):
    baseline = _levers()
    rows = []
    for excel_name, lever_id in EXCEL_NAME_TO_ID_ORDERED:
        value = baseline[lever_id]
        rows.append(
            {
                "Levers": excel_name,
                "Min": value,
                "Low": value,
                "Median": value,
                "High": value,
                "Max": value,
                "Distribution": "set",
                "Type": "discrete",
                "Set": str(value),
                "Probabilities": "1",
            }
        )

    with pd.ExcelWriter(path) as writer:
        pd.DataFrame(rows).to_excel(writer, sheet_name="Levers", index=False)


def test_normalize_levers_converts_external_inputs_to_model_values():
    normalized = normalize_levers(_levers(num_NOAK=5))

    assert normalized["num_orders"] == 2
    assert normalized["num_NOAK"] == 5
    assert normalized["ITC_0"] == pytest.approx(0.30)
    assert normalized["interest_rate_0"] == pytest.approx(0.06)
    assert normalized["design_completion_0"] == pytest.approx(0.70)
    assert normalized["standardization_0"] == pytest.approx(0.80)
    assert normalized["mod_0"] == "modularized"
    assert normalized["BOP_grade_0"] == "non_nuclear"
    assert normalized["RB_grade_0"] == "nuclear"


def test_run_one_scenario_returns_static_inputs_and_unit_results():
    result = run_one_scenario(_config(), _levers())

    assert result["Num_orders"] == 2
    assert result["num_NOAK"] == 2
    assert result["ITC"] == 30
    assert result["n_ITC"] == 1
    assert result["staggering_ratio"] == pytest.approx(_config()["staggering_ratio"])
    assert result["effective_staggering_ratio"] == pytest.approx(_config()["staggering_ratio"])
    assert result["OCC_1"] > 0
    assert result["OCC_2"] > 0
    assert result["NETOCC_1"] < result["OCC_1"]
    assert "NETOCC_2" not in result
    assert result["avg_OCC"] > 0
    assert result["avg_TCI"] > 0
    assert result["avg_duration"] > 0
    assert result["occ_reduction_from_FOAK_to_NOAK_percent"] == pytest.approx(
        (result["OCC_1"] - result["OCC_2"]) / result["OCC_1"] * 100
    )
    assert result["tci_waterfall"]
    waterfall = waterfall_to_dataframe(result)
    assert waterfall["label"].tolist() == [
        "FOAK \n(no firm orders)",
        "Bulk-ordering",
        "Elimination of rework",
        "Supplychain efficiency",
        "Labor productivity",
        "Experience and cross-site standardization",
        "Modular Construction",
        "Commercial BOP",
        "Non safety-related Reactor Building",
        "NOAK \n(firm orders)",
    ]
    assert waterfall.iloc[0]["cumulative_tci"] == pytest.approx(result["TCI_1"])
    assert waterfall.iloc[-1]["cumulative_tci"] == pytest.approx(result["TCI_2"])
    assert waterfall.iloc[1:-1]["absolute_change"].sum() == pytest.approx(
        result["TCI_2"] - result["TCI_1"]
    )
    supplychain_delta = waterfall.loc[
        waterfall["label"].eq("Supplychain efficiency"),
        "absolute_change",
    ].iloc[0]
    assert abs(supplychain_delta) < abs(result["TCI_2"] - result["TCI_1"]) * 0.1

    timeline = build_schedule_timeline(
        {**_config(), "staggering_ratio": result["staggering_ratio"]},
        [1, 2],
        [result["duration_1"], result["duration_2"]],
        [result["STAUP_1"], result["STAUP_2"]],
    )
    assert timeline["construction_finish_month"][1] >= timeline["construction_finish_month"][0]
    assert timeline["startup_finish_month"][1] >= timeline["startup_finish_month"][0]

    levers = levers_to_dataframe(result)
    assert levers.loc[0, "Design Completion"] == "70%"
    assert levers.loc[1, "Design Completion"] == "100%"
    assert levers.loc[0, "Cross Site Standardization"] == ""
    assert levers.loc[1, "Cross Site Standardization"] == "80%"


def test_run_one_scenario_can_use_iat_adjusted_baseline_csv(tmp_path):
    baseline, _ = InputStore().get_baseline("AP1000")
    adjusted = baseline.copy()
    adjusted["Adjusted Total Cost"] = adjusted["Total Cost (USD)"] * 0.5
    adjusted["Adjusted Factory Equipment Cost"] = adjusted["Factory Equipment Cost"] * 0.5
    adjusted["Adjusted Site Labor Cost"] = adjusted["Site Labor Cost"] * 0.5
    adjusted["Adjusted Site Material Cost"] = adjusted["Site Material Cost"] * 0.5
    adjusted_path = tmp_path / "iat_adjusted_ap1000.csv"
    adjusted.to_csv(adjusted_path, index=False)

    default_result = run_one_scenario(_config(), _levers())
    adjusted_result = run_one_scenario(
        {**_config(), "baseline_csv": str(adjusted_path)},
        _levers(),
    )

    assert adjusted_result["OCC_1"] < default_result["OCC_1"]
    assert adjusted_result["D20s_1"] < default_result["D20s_1"]


def test_accert_output_can_be_converted_to_crf_baseline_and_run(tmp_path):
    baseline, _ = InputStore().get_baseline("AP1000")
    accert_like = baseline.rename(
        columns={
            "Account": "code_of_account",
            "Title": "account_description",
            "Total Cost (USD)": "total_cost",
        }
    )[["code_of_account", "account_description", "total_cost"]]
    accert_path = tmp_path / "ap1000_upd_acc_example.csv"
    output_path = tmp_path / "ap1000_accert_for_crf.csv"
    accert_like.to_csv(accert_path, index=False)

    total_hours = float(
        baseline.loc[
            baseline["Account"].astype(str).isin(["21", "22", "23", "24", "26"]),
            "Site Labor Hours",
        ].sum()
    )
    converted = accert_output_to_crf_baseline(
        accert_path,
        output_path,
        reactor_type="AP1000",
        total_20s_labor_hours=total_hours,
    )
    converted_direct = converted.loc[
        converted["Account"].astype(str).isin(["21", "22", "23", "24", "26"]),
        "Site Labor Hours",
    ].sum()

    assert output_path.exists()
    assert converted_direct == pytest.approx(total_hours)
    converted_totals = converted.set_index("Account")["Total Cost (USD)"]
    baseline_totals = baseline.set_index("Account")["Total Cost (USD)"]
    assert converted_totals.loc["214"] == pytest.approx(
        baseline_totals.loc[["215", "217"]].sum()
    )
    assert converted_totals.loc["215"] == pytest.approx(baseline_totals.loc["216"])
    assert converted_totals.loc["216"] == pytest.approx(baseline_totals.loc["214"])
    assert converted_totals.loc["232.1"] == pytest.approx(baseline_totals.loc["23"])
    assert converted_totals.loc["233"] == pytest.approx(baseline_totals.loc["26"])
    assert converted_totals.loc["26"] == pytest.approx(baseline_totals.loc["25"])

    default_result = run_one_scenario(_config(), _levers())
    converted_result = run_one_scenario(
        {**_config(), "baseline_csv": str(output_path)},
        _levers(),
    )
    assert converted_result["OCC_1"] > 0
    assert converted_result["TCI_1"] > 0
    assert converted_result["OCC_1"] == pytest.approx(default_result["OCC_1"], rel=0.1)
    assert converted_result["TCI_1"] == pytest.approx(default_result["TCI_1"], rel=0.1)


def test_visualization_helpers_create_dashboard(tmp_path):
    result = run_one_scenario(_config(), _levers())
    frame = results_to_dataframe(result)
    out_png = tmp_path / "cost_reduction_framework_dashboard.png"
    compact_png = tmp_path / "cost_reduction_framework_compact_dashboard.png"

    assert list(frame["Plant number"]) == [1, 2]
    assert frame.loc[1, "OCC reduction from FOAK"] == pytest.approx(
        occ_reduction_from_foak_to_noak(result)
    )
    assert frame.loc[1, "TCI reduction from FOAK"] == pytest.approx(
        tci_reduction_from_foak_to_noak(result)
    )

    save_dashboard(result, str(out_png), title="Cost Reduction Framework Test")
    save_dashboard(
        result,
        str(compact_png),
        title="Cost Reduction Framework Test",
        show_levers=False,
    )

    assert out_png.exists()
    assert out_png.stat().st_size > 0
    assert compact_png.exists()
    assert compact_png.stat().st_size > 0


def test_run_sampling_from_excel_writes_csv_and_pickle_outputs(tmp_path):
    levers_xlsx = tmp_path / "crf_levers.xlsx"
    out_csv = tmp_path / "crf_samples.csv"
    out_pkl = tmp_path / "crf_samples.pkl"
    _lever_workbook(levers_xlsx)

    run_sampling_from_excel(
        _config(),
        str(levers_xlsx),
        n_samples=2,
        out_csv=str(out_csv),
        out_pkl=str(out_pkl),
        seed=7,
    )

    with out_csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 2
    assert rows[0]["OCC_1"]
    assert rows[0]["OCC_2"]
    assert rows[0]["NETOCC_1"]
    assert rows[0]["NCI_1"]
    assert rows[0]["avg_OCC"]

    with out_pkl.open("rb") as handle:
        sampled_rows = [pickle.load(handle), pickle.load(handle)]

    assert sampled_rows[0]["Num_orders"] == 2
    assert sampled_rows[1]["NETOCC_1"] < sampled_rows[1]["OCC_1"]
