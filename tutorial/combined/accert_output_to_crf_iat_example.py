"""Use an ACCERT updated-account CSV as a CRF and IAT baseline.

Run from the repository root with:

    python tutorial/combined/accert_output_to_crf_iat_example.py
"""

from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from crf import accert_output_to_crf_baseline, print_scenario_result, run_one_scenario
from crf.io.excel_inputs import InputStore
from iat import level_account_summary, run_adjustment


OUTPUT_DIR = REPO_ROOT / "tutorial" / "combined" / "outputs"
ACCERT_INPUT = REPO_ROOT / "tutorial" / "accert" / "AP1000.son"
CONVERTED_BASELINE = OUTPUT_DIR / "ap1000_accert_for_crf_iat.csv"
IAT_OUTPUT = OUTPUT_DIR / "ap1000_accert_china_iat.csv"


config = {
    "reactor_type": "AP1000",
    "f_22": 250_000_000,
    "f_2321": 150_000_000,
    "land_cost_per_acre_0": 22_000,
    "construction_duration_0": 76,
    "startup_0": 28,
    "staggering_ratio": 0.75,
}

levers = {
    "num_orders": 10,
    "num_NOAK": 8,
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
}


def ap1000_total_20s_labor_hours() -> float:
    baseline, _ = InputStore().get_baseline("AP1000")
    mask = baseline["Account"].astype(str).isin(["21", "22", "23", "24", "26"])
    return float(baseline.loc[mask, "Site Labor Hours"].sum())


def run_accert_ap1000() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "accertdb.sqlite"
        shutil.copy2(REPO_ROOT / "src" / "accertdb.sqlite", db_path)
        env = {**os.environ, "ACCERT_SQLITE_DB": str(db_path)}
        subprocess.run(
            [sys.executable, str(REPO_ROOT / "src" / "Main.py"), "-i", str(ACCERT_INPUT)],
            cwd=OUTPUT_DIR,
            env=env,
            check=True,
        )
    candidates = sorted(OUTPUT_DIR.glob("ap1000_upd_acc_*.csv"))
    if not candidates:
        raise FileNotFoundError("ACCERT did not create an ap1000_upd_acc CSV")
    return candidates[-1]


if __name__ == "__main__":
    print("Step 1: Run ACCERT AP1000 and collect the updated-account CSV")
    accert_csv = run_accert_ap1000()
    print(f"ACCERT account CSV: {accert_csv}")

    print("\nStep 2: Convert ACCERT output to CRF/IAT baseline shape")
    total_hours = ap1000_total_20s_labor_hours()
    accert_output_to_crf_baseline(
        accert_csv,
        CONVERTED_BASELINE,
        reactor_type="AP1000",
        total_20s_labor_hours=total_hours,
    )
    print(f"Converted baseline: {CONVERTED_BASELINE}")
    print(f"Assigned total 20s labor hours: {total_hours:,.2f}")

    print("\nStep 3: Run CRF with the ACCERT-derived baseline")
    crf_result = run_one_scenario({**config, "baseline_csv": str(CONVERTED_BASELINE)}, levers)
    print_scenario_result(crf_result)

    print("\nStep 4: Run IAT with the same ACCERT-derived baseline")
    iat_result = run_adjustment(
        {
            "reactor_type": "ACCERT output-LR",
            "country": "China",
            "year_dollar": 2024,
            "input_csv": CONVERTED_BASELINE,
            "output_csv": IAT_OUTPUT,
        }
    )
    print(level_account_summary(iat_result["adjusted_costs"], max_level=2).to_string(index=False))
    print(f"\nIAT adjusted output: {IAT_OUTPUT}")
