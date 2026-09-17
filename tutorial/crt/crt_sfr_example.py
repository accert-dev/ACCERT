from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from crt import print_scenario_result, run_one_scenario, save_dashboard


config = {
    "reactor_type": "SFR",
    "f_22": 250_000_000,
    "f_2321": 150_000_000,
    "land_cost_per_acre_0": 22_000,
    "startup_0": 16,
    "staggering_ratio": 0.75,
}

levers = {
    "num_orders": 13,
    "num_NOAK": 8,
    "itc_percent": 0,
    "n_itc": 0,
    "interest_percent": 6,
    "design_completion_percent": 80,
    "design_maturity": 1,
    "proc_exp": 0.5,
    "N_proc": 3,
    "ce_exp": 1.0,
    "N_cons": 5,
    "ae_exp": 0.5,
    "N_AE": 4,
    "standardization_percent": 80,
    "modularity_code": 1,
    "bop_grade_code": 1,
    "rb_grade_code": 0,
}

show_lever_table = True


if __name__ == "__main__":
    result = run_one_scenario(config, levers)
    print_scenario_result(result)

    output_path = Path("cost_reduction_tool_sfr_dashboard.png")
    save_dashboard(
        result,
        output_path,
        title="SFR Cost Reduction Framework Tool",
        show_levers=show_lever_table,
    )
    print(f"\nSaved dashboard figure to: {output_path.resolve()}")
