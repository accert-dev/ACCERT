from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .data_loader import (
    COUNTRY_ALIASES,
    COST_CATEGORIES,
    STANDARD_COST_COLUMNS,
    load_assumptions,
    normalize_account,
    normalize_country,
    reactor_family_from_type,
)


ADJUSTED_COLUMNS = {
    "equipment": "Adjusted Factory Equipment Cost",
    "material": "Adjusted Site Material Cost",
    "labor": "Adjusted Site Labor Cost",
    "land": "Adjusted Land Cost",
    "catchall": "Adjusted Catch-All Cost",
}

COMPARISON_GROUPS = {
    "20": "Capitalized Direct Costs",
}

LEVEL_2_GROUP_TITLES = {
    "10": "Capitalized Pre-Construction Costs",
    "20": "Capitalized Direct Costs",
    "30": "Capitalized Indirect Services Costs",
    "50": "Capitalized Supplementary Costs",
    "60": "Capitalized Financial Costs",
}


def available_countries() -> list[str]:
    """Return countries currently available in the packaged IAT assumptions."""
    return sorted(load_assumptions()["adjustment_factors"])


def run_adjustment(config: dict[str, Any]) -> dict[str, Any]:
    """Run an International Adjustment Tool scenario.

    Parameters
    ----------
    config:
        Required keys are ``reactor_type``, ``country``, and ``year_dollar``.
        For ACCERT outputs, pass ``input_csv`` with a CSV containing the ACCERT
        COA columns. ``reactor_type`` can be values such as
        ``"ACCERT output-LR"``, ``"ACCERT output-SMR"``, ``"large reactor"``,
        or ``"SMR"``.

    Returns
    -------
    dict
        Scenario metadata, totals, and the adjusted dataframe.
    """
    reactor_type = config["reactor_type"]
    country = normalize_country(config["country"])
    year_dollar = config["year_dollar"]
    family = reactor_family_from_type(reactor_type)
    assumptions = load_assumptions(config.get("assumptions_path"))

    if "input_csv" in config and config["input_csv"]:
        df = read_accert_cost_csv(config["input_csv"])
        input_source = str(config["input_csv"])
    else:
        scenario = config.get("reference_scenario", "scenario_1")
        df = reference_cost_dataframe(assumptions, family, scenario)
        input_source = f"{family} {scenario} packaged IAT reference"

    adjusted = adjust_cost_dataframe(
        df,
        country=country,
        reactor_type=reactor_type,
        assumptions=assumptions,
    )

    output_csv = config.get("output_csv")
    if output_csv:
        Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
        adjusted.to_csv(output_csv, index=False)

    total_mask = adjusted["Is Leaf Account"]
    input_total = float(adjusted.loc[total_mask, "Original Total Cost"].sum())
    adjusted_total = float(adjusted.loc[total_mask, "Adjusted Total Cost"].sum())
    comparison = account_group_comparison(adjusted)
    return {
        "reactor_type": reactor_type,
        "reactor_family": family,
        "country": country,
        "year_dollar": year_dollar,
        "input_source": input_source,
        "input_total": input_total,
        "adjusted_total": adjusted_total,
        "adjustment_ratio": adjusted_total / input_total if input_total else 0.0,
        "comparison": comparison,
        "adjusted_costs": adjusted,
        "output_csv": output_csv,
    }


def read_accert_cost_csv(path: str | Path) -> pd.DataFrame:
    """Read an ACCERT/CRF-style COA CSV and normalize numeric cost columns."""
    df = pd.read_csv(path)
    missing = {"Account", "Title"} - set(df.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")

    df = df.copy()
    df["Account"] = df["Account"].map(normalize_account)
    for col in STANDARD_COST_COLUMNS:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce",
        ).fillna(0.0)
    return df


def reference_cost_dataframe(assumptions: dict[str, Any], family: str, scenario: str) -> pd.DataFrame:
    """Create a standalone LR/SMR dataframe from packaged IAT reference costs."""
    if family not in assumptions["families"]:
        raise ValueError(f"Unknown reactor family: {family}")

    rows = []
    for record in assumptions["families"][family]:
        costs = record["reference_costs_usd_per_kwe"].get(scenario)
        if costs is None:
            raise ValueError(f"Unknown reference scenario: {scenario}")
        rows.append(
            {
                "Account": record["account"],
                "Title": record["title"],
                "Total Cost (USD)": sum(float(costs.get(cat, 0.0)) for cat in COST_CATEGORIES),
                "Factory Equipment Cost": float(costs.get("equipment", 0.0)),
                "Site Labor Hours": 0.0,
                "Site Labor Cost": float(costs.get("labor", 0.0)),
                "Site Material Cost": float(costs.get("material", 0.0)),
                "Land Cost": float(costs.get("land", 0.0)),
                "Catch-All Cost": float(costs.get("catchall", 0.0)),
            }
        )
    return pd.DataFrame(rows)


def adjust_cost_dataframe(
    df: pd.DataFrame,
    country: str,
    reactor_type: str,
    assumptions: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Apply IAT localization and country adjustment factors to a COA dataframe."""
    assumptions = load_assumptions() if assumptions is None else assumptions
    country = normalize_country(country)
    family = reactor_family_from_type(reactor_type)
    if country not in assumptions["adjustment_factors"]:
        raise ValueError(
            f"Unsupported country {country!r}. Available countries: {sorted(assumptions['adjustment_factors'])}"
        )

    records = assumptions["families"][family]
    factors = assumptions["adjustment_factors"][country]

    out = df.copy()
    out["Account"] = out["Account"].map(normalize_account)
    for col in STANDARD_COST_COLUMNS:
        if col not in out.columns:
            out[col] = 0.0
        out[col] = pd.to_numeric(
            out[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce",
        ).fillna(0.0)

    adjusted_rows = []
    for _, row in out.iterrows():
        record = _find_localization_record(str(row["Account"]), records, country)
        original = _category_costs(row, record)
        localization = record["localization"][country] if record is not None else {}
        adjusted = {
            category: _adjust_category_cost(
                amount=original[category],
                local_share=float(localization.get(category, 0.0)),
                factor=float(factors[category]),
                tariff=float(factors["import_tariff"]),
            )
            for category in COST_CATEGORIES
        }
        adjusted_rows.append(
            {
                "Matched IAT Account": record["account"] if record is not None else "",
                "Matched IAT Title": record["title"] if record is not None else "",
                "Original Equipment Cost": original["equipment"],
                "Original Material Cost": original["material"],
                "Original Labor Cost": original["labor"],
                "Original Land Cost": original["land"],
                "Original Catch-All Cost": original["catchall"],
                "Original Total Cost": sum(original.values()),
                **{ADJUSTED_COLUMNS[category]: adjusted[category] for category in COST_CATEGORIES},
                "Adjusted Total Cost": sum(adjusted.values()),
            }
        )

    adjusted_df = pd.concat([out.reset_index(drop=True), pd.DataFrame(adjusted_rows)], axis=1)
    adjusted_df["Is Leaf Account"] = _leaf_account_mask(adjusted_df["Account"].tolist())
    return adjusted_df


def print_adjustment_result(result: dict[str, Any]) -> None:
    """Print a concise IAT result summary."""
    print("International Adjustment Tool result\n")
    print(f"Reactor type: {result['reactor_type']}")
    print(f"Country: {result['country']}")
    print(f"Year dollar: {result['year_dollar']}")
    print(f"Input source: {result['input_source']}")
    print(f"Input total: {result['input_total']:,.2f}")
    print(f"Adjusted total: {result['adjusted_total']:,.2f}")
    print(f"Adjustment ratio: {result['adjustment_ratio']:.4f}")
    if "comparison" in result and not result["comparison"].empty:
        print("\nCOA comparison:")
        print(result["comparison"].round(2).to_string(index=False))
    if result.get("output_csv"):
        print(f"Saved adjusted CSV to: {result['output_csv']}")


def account_group_comparison(adjusted_df: pd.DataFrame) -> pd.DataFrame:
    """Summarize original and adjusted costs by requested high-level COA groups."""
    rows = []
    leaf_df = adjusted_df.loc[adjusted_df["Is Leaf Account"]].copy()
    account_series = leaf_df["Account"].astype(str).map(normalize_account)

    for group, title in COMPARISON_GROUPS.items():
        group_digit = group[0]
        mask = account_series.str.startswith(group_digit)
        original = float(leaf_df.loc[mask, "Original Total Cost"].sum())
        adjusted = float(leaf_df.loc[mask, "Adjusted Total Cost"].sum())
        rows.append(
            {
                "COA": group,
                "Title": title,
                "Original Total Cost": original,
                "Adjusted Total Cost": adjusted,
                "Difference": adjusted - original,
                "Adjustment Ratio": adjusted / original if original else 0.0,
            }
        )
    return pd.DataFrame(rows)


def level_account_summary(adjusted_df: pd.DataFrame, max_level: int = 2) -> pd.DataFrame:
    """Return comparison rows for level-1 and level-2 accounts.

    Level-1 rows are synthesized as `10`, `20`, etc. Level-2 rows use the
    detailed accounts such as `11`, `21`, `22`, and `31`. Totals are calculated
    from leaf rows to avoid double-counting when parent accounts are present.
    """
    leaf_df = adjusted_df.loc[adjusted_df["Is Leaf Account"]].copy()
    leaf_accounts = leaf_df["Account"].astype(str).map(normalize_account)
    all_accounts = adjusted_df["Account"].astype(str).map(normalize_account)
    rows = []

    if max_level >= 1:
        for group in sorted({account[0] for account in leaf_accounts if account and account[0].isdigit()}):
            code = f"{group}0"
            rows.append(
                _summary_row(
                    code=code,
                    title=LEVEL_2_GROUP_TITLES.get(code, ""),
                    level=1,
                    df=leaf_df.loc[leaf_accounts.str.startswith(group)],
                )
            )

    if max_level >= 2:
        level_2_codes = sorted(
            {
                account[:2]
                for account in all_accounts
                if len(account) >= 2 and account[:2].isdigit()
            }
        )
        for code in level_2_codes:
            matching_leaf = leaf_df.loc[leaf_accounts.str.startswith(code)]
            if matching_leaf.empty:
                continue
            title = _account_title(adjusted_df, code)
            rows.append(_summary_row(code=code, title=title, level=2, df=matching_leaf))

    return pd.DataFrame(rows)


def _find_localization_record(account: str, records: list[dict[str, Any]], country: str) -> dict[str, Any] | None:
    account = normalize_account(account)
    by_account = {record["account"]: record for record in records}

    for candidate in _account_candidates(account):
        record = by_account.get(candidate)
        if record is not None and _has_localization_assumptions(record, country):
            return record

    if account in by_account:
        return by_account[account]
    return None


def _account_candidates(account: str) -> list[str]:
    candidates = [account]
    base = account.split(".", 1)[0]
    if base != account:
        candidates.append(base)

    for length in range(len(base) - 1, 1, -1):
        candidates.append(base[:length])

    seen = set()
    return [candidate for candidate in candidates if not (candidate in seen or seen.add(candidate))]


def _has_localization_assumptions(record: dict[str, Any], country: str) -> bool:
    localization = record["localization"].get(country, {})
    shares = record.get("category_shares", {})
    return any(float(localization.get(category, 0.0)) > 0.0 for category in COST_CATEGORIES) or any(
        float(shares.get(category, 0.0)) > 0.0 for category in COST_CATEGORIES
    )


def _leaf_account_mask(accounts: list[str]) -> list[bool]:
    normalized = [normalize_account(account) for account in accounts]
    return [
        not any(other != account and other.startswith(account) for other in normalized)
        for account in normalized
    ]


def _summary_row(code: str, title: str, level: int, df: pd.DataFrame) -> dict[str, Any]:
    original = float(df["Original Total Cost"].sum())
    adjusted = float(df["Adjusted Total Cost"].sum())
    return {
        "COA": code,
        "Level": level,
        "Title": title,
        "Original Total Cost": original,
        "Adjusted Total Cost": adjusted,
        "Difference": adjusted - original,
        "Adjustment Ratio": adjusted / original if original else 0.0,
    }


def _account_title(adjusted_df: pd.DataFrame, account: str) -> str:
    matching = adjusted_df.loc[adjusted_df["Account"].astype(str).map(normalize_account).eq(account), "Title"]
    if not matching.empty:
        return str(matching.iloc[0])
    return LEVEL_2_GROUP_TITLES.get(account, "")


def _category_costs(row: pd.Series, record: dict[str, Any] | None) -> dict[str, float]:
    equipment = float(row.get("Factory Equipment Cost", 0.0) or 0.0)
    material = float(row.get("Site Material Cost", 0.0) or 0.0)
    labor = float(row.get("Site Labor Cost", 0.0) or 0.0)
    land = float(row.get("Land Cost", 0.0) or 0.0)
    catchall = float(row.get("Catch-All Cost", 0.0) or 0.0)
    total = float(row.get("Total Cost (USD)", 0.0) or 0.0)

    categorized = equipment + material + labor + land + catchall
    residual = total - categorized
    if abs(residual) > 1e-6:
        shares = record.get("category_shares", {}) if record is not None else {}
        missing_categories = [
            category
            for category, amount in {
                "equipment": equipment,
                "material": material,
                "labor": labor,
                "land": land,
                "catchall": catchall,
            }.items()
            if abs(amount) <= 1e-12 and float(shares.get(category, 0.0)) > 0
        ]
        share_total = sum(float(shares.get(category, 0.0)) for category in missing_categories)
        if share_total > 0:
            for category in missing_categories:
                amount = residual * float(shares.get(category, 0.0)) / share_total
                if category == "equipment":
                    equipment += amount
                elif category == "material":
                    material += amount
                elif category == "labor":
                    labor += amount
                elif category == "land":
                    land += amount
                elif category == "catchall":
                    catchall += amount
        else:
            catchall += residual

    return {
        "equipment": equipment,
        "material": material,
        "labor": labor,
        "land": land,
        "catchall": catchall,
    }


def _adjust_category_cost(amount: float, local_share: float, factor: float, tariff: float) -> float:
    imported_share = 1.0 - local_share
    return amount * (imported_share * (1.0 + tariff) + local_share * factor)
