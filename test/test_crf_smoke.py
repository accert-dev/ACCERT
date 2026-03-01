

import os
import sys
import pandas as pd
src_path = os.path.abspath(os.path.join(os.pardir, 'src'))
sys.path.insert(0, src_path)
from crf import run_one_scenario


def main():

    config = {
    # "reactor_type": "HTGR", # or "SFR"
    "reactor_type": "SFR", # or "SFR"    
    "f_22": 250_000_000,
    "f_2321": 150_000_000,
    "land_cost_per_acre_0": 22000,
    "startup_0": 16,
    "staggering_ratio": 0.75,
    }

    levers = {
        "num_orders": 13, 
        "itc_percent": 0,
        "n_itc": 0,
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
    # transfer the result into more readable format
    # all OCC, NETOCC, TCI, NCI can be put into a table with columns plant number and metric name, but for simplicity we just print them out here.
    results_df = pd.DataFrame({"Plant_number": list(range(1, int(levers["num_orders"])+1))})
    for k, v in result.items():
        if k.startswith("OCC_"):
            results_df[f"OCC"] = results_df["Plant_number"].apply(lambda x: result.get(f"OCC_{x}", None))
        elif k.startswith("NETOCC_"):
            results_df[f"NETOCC"] = results_df["Plant_number"].apply(lambda x: result.get(f"NETOCC_{x}", None))
        elif k.startswith("TCI_"):
            results_df[f"TCI"] = results_df["Plant_number"].apply(lambda x: result.get(f"TCI_{x}", None))
        elif k.startswith("NCI_"):
            results_df[f"NCI"] = results_df["Plant_number"].apply(lambda x: result.get(f"NCI_{x}", None))
        elif k.startswith("duration_"):
            results_df[f"duration"] = results_df["Plant_number"].apply(lambda x: result.get(f"duration_{x}", None))
        elif k.startswith("D10s_"):
            results_df[f"D10s"] = results_df["Plant_number"].apply(lambda x: result.get(f"D10s_{x}", None))
        elif k.startswith("D20s_"):
            results_df[f"D20s"] = results_df["Plant_number"].apply(lambda x: result.get(f"D20s_{x}", None))
        elif k.startswith("D30s_"): 
            results_df[f"D30s"] = results_df["Plant_number"].apply(lambda x: result.get(f"D30s_{x}", None))
        elif k.startswith("D50s_"):
            results_df[f"D50s"] = results_df["Plant_number"].apply(lambda x: result.get(f"D50s_{x}", None))
        elif k.startswith("D60s_"):
            results_df[f"D60s"] = results_df["Plant_number"].apply(lambda x: result.get(f"D60s_{x}", None))
        elif k.startswith("D20_equip_"):
            results_df[f"D20_equip"] = results_df["Plant_number"].apply(lambda x: result.get(f"D20_equip_{x}", None))
        elif k.startswith("D20_mat_"):
            results_df[f"D20_mat"] = results_df["Plant_number"].apply(lambda x: result.get(f"D20_mat_{x}", None))
        elif k.startswith("D20_labor_"):
            results_df[f"D20_labor"] = results_df["Plant_number"].apply(lambda x: result.get(f"D20_labor_{x}", None)) 

        
    print("Results by plant number:\n")
    print(results_df.round(2).fillna("").to_string(index=False))

    summary_metrics = ["cons_duration_cumulative_wz_startup", "occLastUnit", "TCILastUnit", "durationsLastUnit", "avg_OCC", "avg_TCI", "avg_duration"]
    print("\nSummary metrics:\n")
    for metric in summary_metrics:
        print(f"{metric}: {result[metric]:.2f}")    



    # for k, v in result.items():
    #     print(f"{k}: {v}")
    print("\nTest Successful")


if __name__ == "__main__":
    main()
