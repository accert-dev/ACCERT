from __future__ import annotations

from pathlib import Path

import pandas as pd

from .io.excel_inputs import COLS, InputStore, _normalize_account
from .model.core_accounts import DIRECT_DETAIL_ACCOUNTS, update_high_level_costs


ACCERT_ACCOUNT_COLUMNS = {
    "code_of_account": "Account",
    "account_description": "Title",
    "total_cost": "Total Cost (USD)",
}

DIRECT_TOTAL_ACCOUNTS = ["21", "22", "23", "24", "25", "26", "28"]
ACCERT_TO_CRT_DIRECT_ACCOUNT_MAP = {
    "211": "211",
    "212": "212",
    "213": "213",
    "214": "216",
    "215": "214",
    "216": "215",
    "217": "214",
    "22": "22",
    "23": "232.1",
    "24": "24",
    "25": "26",
    "26": "233",
}
ACCOUNT_218_LETTERS = tuple("ABCDEFGHIJKLMNOPQRSTUV")


def accert_output_to_crt_baseline(
    accert_csv: str | Path,
    output_csv: str | Path | None = None,
    *,
    reactor_type: str = "AP1000",
    total_20s_labor_hours: float,
    data_dir: str | Path | None = None,
    template_baseline_csv: str | Path | None = None,
) -> pd.DataFrame:
    """Convert an ACCERT updated-account CSV into a CRT/IAT baseline CSV.

    ACCERT account outputs contain account totals but not the CRT category split
    or labor-hour inputs. This bridge keeps the ACCERT direct-account totals,
    uses the selected CRT baseline's cost-category proportions for factory,
    labor, and material dollars, and distributes the user-provided total 20s
    labor hours using the selected CRT baseline's labor-hour proportions.
    """
    template, power = InputStore(
        data_dir=str(data_dir) if data_dir else None,
        baseline_csv=str(template_baseline_csv) if template_baseline_csv else None,
    ).get_baseline(reactor_type)
    accert_accounts = _read_accert_account_output(accert_csv)

    converted = template.copy()
    totals = _crt_direct_totals_from_accert(accert_accounts)
    _apply_direct_totals(converted, totals, template)
    _apply_labor_hours(converted, float(total_20s_labor_hours), template)

    converted = update_high_level_costs(converted, power)[COLS].copy()
    if output_csv is not None:
        output_path = Path(output_csv)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        converted.to_csv(output_path, index=False)
    return converted


def _read_accert_account_output(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if {"Account", "Title", "Total Cost (USD)"}.issubset(df.columns):
        out = df[["Account", "Title", "Total Cost (USD)"]].copy()
    else:
        missing = set(ACCERT_ACCOUNT_COLUMNS) - set(df.columns)
        if missing:
            raise ValueError(f"{path} missing ACCERT account columns: {sorted(missing)}")
        out = df.rename(columns=ACCERT_ACCOUNT_COLUMNS)[["Account", "Title", "Total Cost (USD)"]].copy()
    out["Account"] = out["Account"].map(_normalize_account)
    out["Total Cost (USD)"] = pd.to_numeric(
        out["Total Cost (USD)"].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    ).fillna(0.0)
    return out


def _value_by_account(df: pd.DataFrame, account: str) -> float:
    matches = df.loc[df["Account"].astype(str).eq(str(account)), "Total Cost (USD)"]
    if matches.empty:
        return 0.0
    return float(matches.iloc[0])


def _crt_direct_totals_from_accert(accert_accounts: pd.DataFrame) -> dict[str, float]:
    totals = {account: 0.0 for account in DIRECT_TOTAL_ACCOUNTS}
    for accert_account, crt_account in ACCERT_TO_CRT_DIRECT_ACCOUNT_MAP.items():
        totals[crt_account] = totals.get(crt_account, 0.0) + _value_by_account(accert_accounts, accert_account)
    totals["214"] = totals.get("214", 0.0) + _sum_218_letter_accounts(accert_accounts)
    return totals


def _sum_218_letter_accounts(df: pd.DataFrame) -> float:
    accounts = df["Account"].astype(str)
    mask = accounts.map(
        lambda account: (
            len(account) == 4
            and account.startswith("218")
            and account[-1] in ACCOUNT_218_LETTERS
        )
    )
    return float(df.loc[mask, "Total Cost (USD)"].sum())


def _category_shares(row: pd.Series) -> dict[str, float]:
    total = float(row["Total Cost (USD)"])
    if total <= 0:
        return {
            "Factory Equipment Cost": 0.0,
            "Site Labor Cost": 0.0,
            "Site Material Cost": 0.0,
        }
    shares = {
        "Factory Equipment Cost": float(row["Factory Equipment Cost"]) / total,
        "Site Labor Cost": float(row["Site Labor Cost"]) / total,
        "Site Material Cost": float(row["Site Material Cost"]) / total,
    }
    allocated = sum(shares.values())
    if allocated <= 0:
        shares["Site Material Cost"] = 1.0
    elif abs(allocated - 1.0) > 1e-12:
        shares["Site Material Cost"] += 1.0 - allocated
    return shares


def _apply_direct_totals(converted: pd.DataFrame, totals: dict[str, float], template: pd.DataFrame) -> None:
    template_rows = template.set_index("Account", drop=False)
    for account, total in totals.items():
        mask = converted["Account"].astype(str).eq(str(account))
        if not mask.any() or account not in template_rows.index:
            continue
        shares = _category_shares(template_rows.loc[account])
        converted.loc[mask, "Total Cost (USD)"] = total
        for column, share in shares.items():
            converted.loc[mask, column] = total * share


def _apply_labor_hours(converted: pd.DataFrame, total_20s_labor_hours: float, template: pd.DataFrame) -> None:
    if total_20s_labor_hours < 0:
        raise ValueError("total_20s_labor_hours must be non-negative")

    template_hours = {
        account: _labor_hours_by_account(template, account)
        for account in DIRECT_DETAIL_ACCOUNTS
    }
    total_template_hours = sum(template_hours.values())
    if total_template_hours <= 0:
        shares = {account: 1.0 / len(DIRECT_DETAIL_ACCOUNTS) for account in DIRECT_DETAIL_ACCOUNTS}
    else:
        shares = {
            account: hours / total_template_hours
            for account, hours in template_hours.items()
        }
    for account, share in shares.items():
        mask = converted["Account"].astype(str).eq(str(account))
        if mask.any():
            converted.loc[mask, "Site Labor Hours"] = total_20s_labor_hours * share


def _labor_hours_by_account(df: pd.DataFrame, account: str) -> float:
    matches = df.loc[df["Account"].astype(str).eq(str(account)), "Site Labor Hours"]
    if matches.empty:
        return 0.0
    return float(matches.iloc[0])
