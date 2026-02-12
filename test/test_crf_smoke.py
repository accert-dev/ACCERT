

import os
import sys

src_path = os.path.abspath(os.path.join(os.pardir, 'src'))
sys.path.insert(0, src_path)
from crf import run_one_scenario


def main():

    config = {
        "inputs_xlsx": "Inputs.xlsx",
        "reactor_type": "Concept A",
        "f_22": 250_000_000,
        "f_2321": 150_000_000,
        "land_cost_per_acre_0": 22000,
        "startup_0": 16,
        "staggering_ratio": 0.75,
    }

    # baseline-style levers (raw form, like from Excel)
    levers = {
        "num_orders": 3,
        "itc_percent": 30,
        "n_itc": 1,
        "interest_percent": 6.5,
        "design_completion_percent": 90,
        "design_maturity": 2,
        "proc_exp": 0.6,
        "N_proc": 3,
        "ce_exp": 0.6,
        "N_cons": 5,
        "ae_exp": 0.6,
        "N_AE": 4,
        "standardization_percent": 70,
        "modularity_code": 1,
        "bop_grade_code": 1,
        "rb_grade_code": 0,
    }

    result = run_one_scenario(config, levers)

    print("\nTest Successful")
    print("avg_OCC:", result["avg_OCC"])
    print("avg_TCI:", result["avg_TCI"])
    print("avg_duration:", result["avg_duration"])


if __name__ == "__main__":
    main()
