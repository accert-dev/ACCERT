import os
import sys
from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

from necost import generate_monte_carlo_samples
from input_processor import parse_son_input
from necostmain import _read_accert_occ_per_kw, run_necost


def _has_sonvalidxml():
    exe = PROJECT_ROOT / "bin" / "sonvalidxml"
    return exe.exists() and os.access(exe, os.X_OK)


def test_triangular_sampler_allows_constant_bounds():
    params = pd.DataFrame(
        {"capital_cost": {"low": 7205.48, "nominal": 7205.48, "high": 7205.48, "distribution": 1}}
    )

    samples = generate_monte_carlo_samples(params, sampling_amount=5, discount_rate=5)

    assert samples["capital_cost"].tolist() == [7205.48] * 5


def test_read_accert_occ_for_necost(tmp_path):
    post_csv = tmp_path / "ap1000_post.csv"
    pd.DataFrame(
        [
            {"metric": "total_direct_cost", "value_2024_dollar_per_kw": 3731.86},
            {"metric": "total_OCC", "value_2024_dollar_per_kw": 7205.48},
        ]
    ).to_csv(post_csv, index=False)

    assert _read_accert_occ_per_kw(post_csv) == pytest.approx(7205.48)


@pytest.mark.skipif(not _has_sonvalidxml(), reason="NEcost SON validation requires Workbench sonvalidxml")
def test_necost_eg13_tutorial_runs(tmp_path):
    results = run_necost(
        PROJECT_ROOT / "tutorial" / "necost" / "EG13.son",
        output_dir=tmp_path,
        make_plot=False,
    )

    assert (tmp_path / "NECOST_results.csv").exists()
    assert (tmp_path / "NECOST_reactor_results.csv").exists()
    assert set(["Capital", "O&M", "FCC", "LCOE"]).issubset(results.columns)
    assert results["reactor_id"].eq("weighted_cycle").all()


@pytest.mark.skipif(not _has_sonvalidxml(), reason="NEcost SON validation requires Workbench sonvalidxml")
def test_eg23_uses_report_driver_blanket_mass_fractions():
    parsed = parse_son_input(
        str(PROJECT_ROOT / "tutorial" / "necost" / "EG23.son"),
        str(PROJECT_ROOT),
    )
    reactors = {
        row["reactor"]: row["mass_fraction"]
        for row in parsed["fuel_cycles"][0]["reactors"]
    }

    assert reactors == {"FR_DRIVER": pytest.approx(0.8), "FR_BLANKET": pytest.approx(0.2)}


@pytest.mark.skipif(not _has_sonvalidxml(), reason="NEcost SON validation requires Workbench sonvalidxml")
def test_eg13_uses_report_energy_fractions():
    parsed = parse_son_input(
        str(PROJECT_ROOT / "tutorial" / "necost" / "EG13.son"),
        str(PROJECT_ROOT),
    )
    reactors = {
        row["reactor"]: row["energy_fraction"]
        for row in parsed["fuel_cycles"][0]["reactors"]
    }

    assert reactors == {"PWR_UOX": pytest.approx(0.902), "PWR_MOX": pytest.approx(0.098)}
