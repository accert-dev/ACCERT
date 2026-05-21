"""Run EG03-EG40 NEcost examples and compare their 5% LCAE mean to the report."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

from necostmain import run_necost  # noqa: E402


def report_mean_5pct(input_file: Path):
    match = re.search(
        r"Report LCAE at 5% discount rate: mean ([0-9.]+)",
        input_file.read_text(),
    )
    return None if match is None else float(match.group(1))


def main():
    output_root = Path(__file__).with_name("outputs") / "report_check"
    output_root.mkdir(parents=True, exist_ok=True)
    rows = []
    for input_file in sorted(Path(__file__).parent.glob("EG[0-9][0-9].*.son")):
        eg = input_file.name[:4]
        if not 3 <= int(eg[2:]) <= 40:
            continue
        report = report_mean_5pct(input_file)
        try:
            results = run_necost(input_file, output_dir=output_root / eg, make_plot=False)
            computed = float(results["LCOE"].mean())
            status = "ok"
        except Exception as exc:
            computed = None
            status = f"{type(exc).__name__}: {exc}"
        rows.append(
            {
                "case": eg,
                "input": input_file.name,
                "report_5pct_mean_mills_per_kwh": report,
                "computed_5pct_mean_mills_per_kwh": computed,
                "delta_mills_per_kwh": None if report is None or computed is None else computed - report,
                "relative_delta_pct": None
                if report in (None, 0) or computed is None
                else (computed - report) / report * 100,
                "status": status,
            }
        )

    summary = pd.DataFrame(rows)
    summary_file = output_root / "summary.csv"
    summary.to_csv(summary_file, index=False)
    print(summary.to_string(index=False, max_colwidth=80))
    print(f"\nSaved comparison summary to {summary_file}")


if __name__ == "__main__":
    main()
