"""Run a deterministic Cost Reduction Framework scenario.

Run from the repository root with:

    PYTHONPATH=src python tutorial/crf_quickstart.py
"""

from pathlib import Path

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
    "modularity_code": 1,
    "bop_grade_code": 1,
    "rb_grade_code": 0,
}


if __name__ == "__main__":
    result = run_one_scenario(config, levers)
    print_scenario_result(result)

    output_path = Path("cost_reduction_framework_dashboard.png")
    save_dashboard(result, output_path, title="AP1000 Cost Reduction Framework")
    print(f"\nSaved dashboard figure to: {output_path.resolve()}")
