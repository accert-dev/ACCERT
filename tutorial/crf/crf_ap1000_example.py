"""Run a deterministic Cost Reduction Framework scenario.

Run from the repository root with:

    python tutorial/crf/crf_ap1000_example.py
"""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from crf import print_scenario_result, run_one_scenario, save_dashboard


config = {
    "reactor_type": "AP1000",
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

show_lever_table = True


if __name__ == "__main__":
    result = run_one_scenario(config, levers)
    print_scenario_result(result)

    output_path = Path("cost_reduction_framework_AP1000.png")
    save_dashboard(
        result,
        output_path,
        title="AP1000 Cost Reduction Framework",
        show_levers=show_lever_table,
    )
    print(f"\nSaved dashboard figure to: {output_path.resolve()}")
