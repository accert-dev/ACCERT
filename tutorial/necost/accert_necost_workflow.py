from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from necostmain import run_necost


def main():
    input_path = Path(__file__).with_name("AP1000_ACCERT_NECost.son")
    output_dir = Path(__file__).with_name("outputs") / "ap1000_accert_necost"
    results = run_necost(input_path, output_dir=output_dir)
    summary = results[["Capital", "O&M", "FCC", "LCOE"]].mean().round(2)
    print("\nACCERT to NEcost mean LCOE components ($/MWh):")
    print(summary.to_string())
    print(f"\nResults written to {output_dir}")


if __name__ == "__main__":
    main()
