from pathlib import Path

import pandas as pd
import pytest

from iat import available_countries, level_account_summary, occ_cost_dataframe, occ_totals, run_adjustment, run_occ_scenarios
from iat.data_loader import load_assumptions


def test_iat_available_countries():
    assert available_countries() == ["China", "Korea", "UAE"]


def test_iat_packaged_localization_csvs_store_leaf_level_2_accounts_only():
    for path in Path("src/iat/data").glob("*_localization.csv"):
        df = pd.read_csv(path, dtype={"account": str})
        assert not any(col.startswith("scenario_") for col in df.columns)
        stored_accounts = df["account"].astype(str).str.replace(r"\.0$", "", regex=True)
        deeper_accounts = [
            account
            for account in stored_accounts
            if len(account.split(".", 1)[0]) > 2
        ]
        rollup_accounts = [
            account
            for account in stored_accounts
            if len(account) == 2 and account[1] == "0"
        ]
        assert deeper_accounts == []
        assert rollup_accounts == []


def test_iat_requires_accert_csv_or_occ_input():
    with pytest.raises(ValueError, match="input_csv.*occ_value"):
        run_adjustment(
            {
                "reactor_type": "large reactor",
                "country": "China",
                "year_dollar": 2024,
            }
        )


def test_iat_china_account_22_formula(tmp_path):
    csv_path = tmp_path / "accert_output.csv"
    pd.DataFrame(
        [
            {
                "Account": "22",
                "Title": "Reactor System",
                "Total Cost (USD)": 1_000.0,
                "Factory Equipment Cost": 100.0,
                "Site Labor Hours": 0.0,
                "Site Labor Cost": 300.0,
                "Site Material Cost": 600.0,
            }
        ]
    ).to_csv(csv_path, index=False)

    result = run_adjustment(
        {
            "reactor_type": "ACCERT output-LR",
            "country": "China",
            "year_dollar": 2024,
            "input_csv": csv_path,
        }
    )
    row = result["adjusted_costs"].iloc[0]

    expected_equipment = 0.15 * 100.0 * 1.01 + 0.85 * 100.0 * 0.6586985391766269
    expected_labor = 0.05 * 300.0 * 1.01 + 0.95 * 300.0 * 0.7852999699594179
    expected_material = 1.0 * 600.0 * 0.5783938223938224

    assert row["Matched IAT Account"] == "22"
    assert row["Adjusted Factory Equipment Cost"] == pytest.approx(expected_equipment)
    assert row["Adjusted Site Labor Cost"] == pytest.approx(expected_labor)
    assert row["Adjusted Site Material Cost"] == pytest.approx(expected_material)
    assert result["adjusted_total"] == pytest.approx(expected_equipment + expected_labor + expected_material)


def test_iat_china_account_211_inherits_account_21_localization(tmp_path):
    csv_path = tmp_path / "accert_output.csv"
    pd.DataFrame(
        [
            {
                "Account": "211",
                "Title": "Site Preparation/Yard Work",
                "Total Cost (USD)": 1_000.0,
                "Factory Equipment Cost": 100.0,
                "Site Labor Hours": 0.0,
                "Site Labor Cost": 300.0,
                "Site Material Cost": 600.0,
            }
        ]
    ).to_csv(csv_path, index=False)

    result = run_adjustment(
        {
            "reactor_type": "ACCERT output-LR",
            "country": "China",
            "year_dollar": 2024,
            "input_csv": csv_path,
        }
    )
    row = result["adjusted_costs"].iloc[0]

    expected_equipment = 0.02 * 100.0 * 1.01 + 0.98 * 100.0 * 0.6586985391766269
    expected_material = 1.0 * 600.0 * 0.5783938223938224
    expected_labor = 1.0 * 300.0 * 0.7852999699594179

    assert row["Matched IAT Account"] == "21"
    assert row["Adjusted Factory Equipment Cost"] == pytest.approx(expected_equipment)
    assert row["Adjusted Site Material Cost"] == pytest.approx(expected_material)
    assert row["Adjusted Site Labor Cost"] == pytest.approx(expected_labor)
    assert result["adjusted_total"] < result["input_total"]


def test_iat_china_level_3_accounts_use_level_2_localization(tmp_path):
    csv_path = tmp_path / "accert_output.csv"
    pd.DataFrame(
        [
            {
                "Account": "121",
                "Title": "Federal Site Permits",
                "Total Cost (USD)": 1_000.0,
            },
            {
                "Account": "232.1",
                "Title": "Electricity Generation Systems",
                "Total Cost (USD)": 1_000.0,
            },
        ]
    ).to_csv(csv_path, index=False)

    result = run_adjustment(
        {
            "reactor_type": "ACCERT output-LR",
            "country": "China",
            "year_dollar": 2024,
            "input_csv": csv_path,
        }
    )
    adjusted = result["adjusted_costs"].set_index("Account")

    account_121 = adjusted.loc["121"]
    account_2321 = adjusted.loc["232.1"]

    assert account_121["Matched IAT Account"] == "12"
    assert account_121["Original Catch-All Cost"] == pytest.approx(1_000.0)
    assert account_121["Adjusted Total Cost"] == pytest.approx(1_000.0 * 0.59)

    assert account_2321["Matched IAT Account"] == "23"
    assert account_2321["Original Equipment Cost"] == pytest.approx(1_000.0 * 0.706982819)
    assert account_2321["Original Material Cost"] == pytest.approx(1_000.0 * 0.243644672)
    assert account_2321["Original Labor Cost"] == pytest.approx(1_000.0 * 0.049372509)


def test_iat_china_account_18_uses_land_and_60_series_passes_through(tmp_path):
    csv_path = tmp_path / "accert_output.csv"
    pd.DataFrame(
        [
            {
                "Account": "18",
                "Title": "Other Pre-Construction Costs",
                "Total Cost (USD)": 1_000.0,
            },
            {
                "Account": "62",
                "Title": "Interest",
                "Total Cost (USD)": 2_000.0,
            },
        ]
    ).to_csv(csv_path, index=False)

    result = run_adjustment(
        {
            "reactor_type": "ACCERT output-LR",
            "country": "China",
            "year_dollar": 2024,
            "input_csv": csv_path,
        }
    )
    adjusted = result["adjusted_costs"].set_index("Account")

    account_18 = adjusted.loc["18"]
    account_62 = adjusted.loc["62"]

    assert account_18["Original Land Cost"] == pytest.approx(1_000.0)
    assert account_18["Adjusted Total Cost"] == pytest.approx(account_18["Original Total Cost"])

    assert account_62["Matched IAT Account"] == ""
    assert account_62["Adjusted Total Cost"] == pytest.approx(account_62["Original Total Cost"])
    assert result["input_occ"] == pytest.approx(1_000.0)
    assert result["adjusted_occ"] == pytest.approx(1_000.0)
    assert result["occ_adjustment_ratio"] == pytest.approx(1.0)


def test_iat_runs_on_packaged_ap1000_baseline():
    baseline = Path("src/crf/data/AP1000_baseline.csv")
    result = run_adjustment(
        {
            "reactor_type": "ACCERT output-LR",
            "country": "China",
            "year_dollar": 2024,
            "input_csv": baseline,
        }
    )
    assert result["reactor_family"] == "LR"
    assert result["adjusted_total"] > 0
    assert "Adjusted Total Cost" in result["adjusted_costs"].columns
    assert "Is Leaf Account" in result["adjusted_costs"].columns
    input_occ, adjusted_occ = occ_totals(result["adjusted_costs"])
    assert result["input_occ"] == pytest.approx(input_occ)
    assert result["adjusted_occ"] == pytest.approx(adjusted_occ)
    assert result["occ_adjustment_ratio"] == pytest.approx(adjusted_occ / input_occ)
    assert result["occ_adjustment_ratio"] != pytest.approx(result["adjustment_ratio"])

    comparison = result["comparison"]
    coa_20 = comparison.loc[comparison["COA"].eq("20")].iloc[0]
    leaf_20s = result["adjusted_costs"].loc[
        result["adjusted_costs"]["Is Leaf Account"]
        & result["adjusted_costs"]["Account"].astype(str).str.startswith("2")
    ]
    assert coa_20["Original Total Cost"] == pytest.approx(leaf_20s["Original Total Cost"].sum())
    assert coa_20["Adjusted Total Cost"] == pytest.approx(leaf_20s["Adjusted Total Cost"].sum())


def test_iat_level_account_summary_includes_level_1_and_2():
    baseline = Path("src/crf/data/AP1000_baseline.csv")
    result = run_adjustment(
        {
            "reactor_type": "ACCERT output-LR",
            "country": "China",
            "year_dollar": 2024,
            "input_csv": baseline,
        }
    )
    summary = level_account_summary(result["adjusted_costs"], max_level=2)
    assert {"10", "20", "30", "50", "60"}.issubset(set(summary["COA"]))
    assert {"11", "21", "22", "23", "31", "51", "62"}.issubset(set(summary["COA"]))


def test_iat_ap1000_china_keeps_account_18_and_60_from_increasing():
    baseline = Path("src/crf/data/AP1000_baseline.csv")
    result = run_adjustment(
        {
            "reactor_type": "ACCERT output-LR",
            "country": "China",
            "year_dollar": 2024,
            "input_csv": baseline,
        }
    )
    summary = level_account_summary(result["adjusted_costs"], max_level=2).set_index("COA")

    assert summary.loc["18", "Adjusted Total Cost"] == pytest.approx(summary.loc["18", "Original Total Cost"])
    assert summary.loc["60", "Adjusted Total Cost"] == pytest.approx(summary.loc["60", "Original Total Cost"])


def test_iat_occ_cost_dataframe_allocates_occ_from_breakdowns():
    assumptions = load_assumptions()
    df = occ_cost_dataframe(assumptions, "LR", 1_000.0)
    assert df["Total Cost (USD)"].sum() == pytest.approx(1_000.0)

    account_22 = df.loc[df["Account"].eq("22")].iloc[0]
    assert account_22["Total Cost (USD)"] == pytest.approx(1_000.0 * 0.1313794024201299)
    assert account_22["Factory Equipment Cost"] == pytest.approx(
        account_22["Total Cost (USD)"] * 0.7666660792206735
    )


def test_iat_runs_multiple_standalone_occ_scenarios():
    result = run_occ_scenarios(
        {
            "reactor_type": "large reactor",
            "country": "China",
            "year_dollar": 2024,
            "occ_values": [5000.0, 6000.0, 7000.0],
        }
    )
    assert list(result["summary"]["Input OCC"]) == [5000.0, 6000.0, 7000.0]
    assert "Adjustment Ratio of OCC" in result["summary"].columns
    assert len(result["scenario_results"]) == 3
    assert all(value > 0 for value in result["summary"]["Adjusted OCC"])
