"""Run IAT from standalone LR OCC values instead of an ACCERT output CSV.

Run from the repository root with:

    python tutorial/iat/iat_lr_occ_china_example.py
"""

from pathlib import Path
import sys

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from iat import level_account_summary, run_occ_scenarios


BASE_CONFIG = {
    "reactor_type": "large reactor",
    "year_dollar": 2024,
    "occ_values": [5_250, 5_750, 6_250],
    "scenario_names": ["LR OCC case 1", "LR OCC case 2", "LR OCC case 3"],
}

COUNTRIES = ["China", "Korea", "UAE"]


if __name__ == "__main__":
    for country in COUNTRIES:
        output_csv = REPO_ROOT / "tutorial" / "iat" / "outputs" / f"iat_lr_occ_{country.lower()}_adjusted.csv"
        config = {**BASE_CONFIG, "country": country, "output_csv": output_csv}
        result = run_occ_scenarios(config)

        print(f"Standalone LR OCC scenarios adjusted to {country}\n")
        print(result["summary"].round(2).to_string(index=False))

        print("\nLevel 1 and level 2 OCC account comparison for first OCC case, excluding 60s financing:")
        first = result["scenario_results"][0]
        summary = level_account_summary(first["adjusted_costs"], max_level=2)
        summary = summary.loc[~summary["COA"].astype(str).str.startswith("6")]
        summary = summary.sort_values(
            "COA", key=lambda s: pd.to_numeric(s, errors="coerce")
        ).reset_index(drop=True)
        columns = ["COA", "Title", "Original Total Cost", "Adjusted Total Cost", "Adjustment Ratio"]
        display = summary[columns].copy()
        display["COA"] = summary.apply(
            lambda row: ("  " if row["Level"] >= 2 else "") + str(row["COA"]), axis=1
        )
        coa_width = display["COA"].str.len().max() + 1
        print(display.round(2).to_string(
            index=False,
            formatters={"COA": lambda x: str(x).ljust(coa_width)},
        ))

        print(f"\nSaved adjusted detail CSV to: {result['output_csv']}\n")
