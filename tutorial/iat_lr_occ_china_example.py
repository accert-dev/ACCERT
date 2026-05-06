"""Run IAT from standalone LR OCC values instead of an ACCERT output CSV.

Run from the repository root with:

    python tutorial/iat_lr_occ_china_example.py
"""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
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
        output_csv = REPO_ROOT / "tutorial" / f"iat_lr_occ_{country.lower()}_adjusted.csv"
        config = {**BASE_CONFIG, "country": country, "output_csv": output_csv}
        result = run_occ_scenarios(config)

        print(f"Standalone LR OCC scenarios adjusted to {country}\n")
        print(result["summary"].round(2).to_string(index=False))

        print("\nLevel 1 and level 2 account comparison for first OCC case:")
        first = result["scenario_results"][0]
        summary = level_account_summary(first["adjusted_costs"], max_level=2)
        columns = [
            "COA",
            "Level",
            "Title",
            "Original Total Cost",
            "Adjusted Total Cost",
            "Adjustment Ratio",
        ]
        print(summary[columns].round(2).to_string(index=False))

        print(f"\nSaved adjusted detail CSV to: {result['output_csv']}\n")
