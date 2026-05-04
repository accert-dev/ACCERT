"""Run an International Adjustment Tool scenario for an ACCERT-style AP1000 CSV.

Run from the repository root with:

    python tutorial/izt_ap1000_china_example.py
"""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from izt import level_account_summary, print_adjustment_result, run_adjustment


config = {
    "reactor_type": "ACCERT output-LR",
    "country": "China",
    "year_dollar": 2024,
    "input_csv": REPO_ROOT / "src" / "crf" / "data" / "AP1000_baseline.csv",
    "output_csv": REPO_ROOT / "tutorial" / "izt_ap1000_china_adjusted.csv",
}


if __name__ == "__main__":
    result = run_adjustment(config)
    print_adjustment_result(result)
    print("\nLevel 1 and level 2 account comparison:")
    columns = [
        "COA",
        "Level",
        "Title",
        "Original Total Cost",
        "Adjusted Total Cost",
        "Adjustment Ratio",
    ]
    summary = level_account_summary(result["adjusted_costs"], max_level=2)
    print(summary[columns].round(2).to_string(index=False))
