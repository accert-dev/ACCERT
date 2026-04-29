

import os
import sys
import pandas as pd
src_path = os.path.abspath(os.path.join(os.pardir, 'src'))
sys.path.insert(0, src_path)
from crf import run_one_scenario, print_scenario_result


def main():

    config = {
    # "reactor_type": "HTGR", # or "SFR"
    "reactor_type": "AP1000", # or "SFR"    
    "f_22": 250_000_000,
    "f_2321": 150_000_000,
    "land_cost_per_acre_0": 22000,
    # "startup_0": 16,
    "startup_0": 28,
    "staggering_ratio": 0.75,
    }

    levers = {
        "num_orders": 10, 
        "num_NOAK": 8,
        "itc_percent": 0,
        "n_itc": 0,
        "interest_percent": 6,
        # "design_completion_percent": 80,
        "design_completion_percent": 70,
        "design_maturity": 1,
        "proc_exp": 0.5,
        "N_proc": 3,
        "ae_exp": 0.5,
        "N_AE": 4,         
        # "ce_exp": 1,
        "ce_exp": 0.5,
        "N_cons": 5,
        "standardization_percent": 80, # 80% standardized
        "modularity_code": 1, # Modularized
        "bop_grade_code": 1, # Non-nuclear
        "rb_grade_code": 0, # Nuclear
    }

    result = run_one_scenario(config, levers)
    print_scenario_result(result)

    print("\nTest Successful")


if __name__ == "__main__":
    main()
