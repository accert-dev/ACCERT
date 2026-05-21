from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pandas as pd

from necostmain import run_necost


def main():
    input_path = Path(__file__).with_name("EG23.son")
    output_dir = Path(__file__).with_name("outputs") / "eg23_two_island"
    results = run_necost(input_path, output_dir=output_dir)

    details = pd.read_csv(output_dir / "NECOST_reactor_results.csv")
    print("\nEG23 two-island setup")
    print("Driver island mass fraction: 0.80")
    print("Blanket island mass fraction: 0.20")
    print("\nPer-island mean LCOE components ($/MWh):")
    print(details.groupby("reactor_id")[["Capital", "O&M", "FCC", "LCOE"]].mean().round(2).to_string())
    print("\nWeighted cycle mean LCOE components ($/MWh):")
    print(results[["Capital", "O&M", "FCC", "LCOE"]].mean().round(2).to_string())
    print(f"\nResults written to {output_dir}")


if __name__ == "__main__":
    main()
