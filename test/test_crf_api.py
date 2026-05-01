import csv
import pickle

import pandas as pd
import pytest

from crf import run_one_scenario, run_sampling_from_excel
from crf.api import normalize_levers
from crf.sampling.lever_schema import EXCEL_NAME_TO_ID_ORDERED


def _config():
    return {
        "reactor_type": "AP1000",
        "f_22": 250_000_000,
        "f_2321": 150_000_000,
        "land_cost_per_acre_0": 22_000,
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
    assert result["ITC"] == 30
    assert result["n_ITC"] == 1
    assert result["OCC_1"] > 0
    assert result["OCC_2"] > 0
    assert result["NETOCC_1"] < result["OCC_1"]
    assert "NETOCC_2" not in result
    assert result["avg_OCC"] > 0
    assert result["avg_TCI"] > 0
    assert result["avg_duration"] > 0


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
