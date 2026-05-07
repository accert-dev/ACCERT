"""Run IAT on the AP1000 baseline, then use that China-adjusted CSV in CRF.

This example keeps the original AP1000 baseline in ``src/crf/data`` unchanged.
IAT writes a separate adjusted CSV into ``tutorial/combined``. CRF then uses
that file through ``config["baseline_csv"]``.

Run from the repository root with:

    python tutorial/combined/crf_iat_ap1000_china_example.py
"""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from crf import print_scenario_result, run_one_scenario, save_dashboard
from iat import print_adjustment_result, run_adjustment


ORIGINAL_AP1000_BASELINE = REPO_ROOT / "src" / "crf" / "data" / "AP1000_baseline.csv"
IAT_OUTPUT_CSV = REPO_ROOT / "tutorial" / "combined" / "iat_ap1000_china_for_crf.csv"
DASHBOARD_OUTPUT = REPO_ROOT / "tutorial" / "combined" / "crf_iat_ap1000_china_dashboard.png"

iat_config = {
    "reactor_type": "ACCERT output-LR",
    "country": "China",
    "year_dollar": 2024,
    "input_csv": ORIGINAL_AP1000_BASELINE,
    "output_csv": IAT_OUTPUT_CSV,
}

crf_config = {
    "reactor_type": "AP1000",
    "baseline_csv": IAT_OUTPUT_CSV,
    "f_22": 250_000_000,
    "f_2321": 150_000_000,
    "land_cost_per_acre_0": 22_000,
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


if __name__ == "__main__":
    print("Step 1: Run IAT on the original AP1000 baseline for China\n")
    print(f"Original AP1000 baseline: {ORIGINAL_AP1000_BASELINE}")
    print(f"IAT adjusted baseline output: {IAT_OUTPUT_CSV}\n")
    iat_result = run_adjustment(iat_config)
    print_adjustment_result(iat_result)

    print("\nStep 2: Run CRF using the IAT-adjusted AP1000 baseline\n")
    print(f"CRF baseline_csv: {crf_config['baseline_csv']}\n")
    crf_result = run_one_scenario(crf_config, levers)
    print_scenario_result(crf_result)

    save_dashboard(
        crf_result,
        DASHBOARD_OUTPUT,
        title="AP1000 China Cost Reduction Framework",
        show_levers=True,
    )
    print("\nOutputs:")
    print(f"IAT-adjusted CRF baseline CSV: {IAT_OUTPUT_CSV}")
    print(f"CRF dashboard figure: {DASHBOARD_OUTPUT}")
