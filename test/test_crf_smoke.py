

import os
import sys

src_path = os.path.abspath(os.path.join(os.pardir, 'src'))
sys.path.insert(0, src_path)
from crf import run_one_scenario


def main():

    config = {
    "reactor_type": "HTGR", # or "SFR"
    "f_22": 250_000_000,
    "f_2321": 150_000_000,
    "land_cost_per_acre_0": 22000,
    "startup_0": 16,
    "staggering_ratio": 0.75,
    }

    # baseline-style levers (raw form, like from Excel)
    levers = {
        "num_orders": 13, 
        "itc_percent": 40,
        "n_itc": 4,
        "interest_percent": 6,
        "design_completion_percent": 80,
        "design_maturity": 1,
        "proc_exp": 0.5,
        "N_proc": 3,
        "ae_exp": 0.5,
        "N_AE": 4,         
        "ce_exp": 1,
        "N_cons": 5,
        "standardization_percent": 80, # 80% standardized
        "modularity_code": 1, # Modularized
        "bop_grade_code": 1, # Non-nuclear
        "rb_grade_code": 0, # Nuclear
    }

    result = run_one_scenario(config, levers)

    print("\nTest Successful")
    print("avg_OCC:", result["avg_OCC"])
    print("avg_TCI:", result["avg_TCI"])
    print("avg_duration:", result["avg_duration"])
    for k, v in result.items():
        if k not in ["avg_OCC", "avg_TCI", "avg_duration"]:
            print(f"{k}: {v}")  

if __name__ == "__main__":
    main()
