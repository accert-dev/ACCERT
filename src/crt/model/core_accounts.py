import pandas as pd
import numpy as np

REQUIRED_DERIVED_ROWS = [
    # Subtotals + $/kWe rows
    ("10s - Subtotal", None),
    ("10s - $/kWe", None),
    ("20s - Subtotal", None),
    ("20s - $/kWe", None),
    ("30s - Subtotal", None),
    ("30s - $/kWe", None),
    ("50s - Subtotal", None),
    ("50s - $/kWe", None),
    ("60s - Subtotal", None),
    ("60s - $/kWe", None),

    # Final results
    ("Total Direct Capital Cost (Accounts 10 to 20)", None),
    ("(Accounts 10 to 20) US$/kWe", None),
    ("Base Construction Cost (Accounts 20 to 30)", None),
    ("(Accounts 20 to 30) US$/kWe", None),
    ("Total Overnight Cost (Accounts 10 to 50)", None),
    ("(Accounts 10 to 50) US$/kWe", None),
    ("Total Capital Investment Cost (All Accounts)", None),
    ("(Accounts 10 to 60) US$/kWe", None),

    # ITC reduced outputs (updated later, but create placeholders now)
    ("Total Overnight Cost - ITC reduced", None),
    ("Total Overnight Cost -ITC reduced (US$/kWe)", None),
    ("Total Capital Investment Cost - ITC reduced", None),
    ("Total Capital Investment Cost - ITC reduced (US$/kWe)", None),
]

COST_COLS = [
    "Total Cost (USD)",
    "Factory Equipment Cost",
    "Site Labor Hours",
    "Site Labor Cost",
    "Site Material Cost",
]

ALL_COLS = ["Account", "Title"] + COST_COLS

ACCOUNT_21_DETAIL_ACCOUNTS = ["211", "212", "213", "214", "215", "216", "217"]
DIRECT_DETAIL_ACCOUNTS = [*ACCOUNT_21_DETAIL_ACCOUNTS, "22", "232.1", "233", "24", "26"]
TOTAL_COST_DETAIL_ACCOUNTS = [
    "21",
    *ACCOUNT_21_DETAIL_ACCOUNTS,
    "22",
    "23",
    "232.1",
    "233",
    "24",
    "25",
    "26",
]

ACCOUNT_SUBTOTALS = {
    "10s - Subtotal": ["11", "12", "13", "14", "15", "16", "18"],
    "20s - Subtotal": ["21", "22", "23", "24", "25", "26", "28"],
    "30s - Subtotal": ["31", "32", "33", "34", "35"],
    "50s - Subtotal": ["51", "52", "54"],
    "60s - Subtotal": ["62"],
}

PER_KWE_ROWS = {
    "10s": "10s - Subtotal",
    "20s": "20s - Subtotal",
    "30s": "30s - Subtotal",
    "50s": "50s - Subtotal",
    "60s": "60s - Subtotal",
}

FINAL_TOTAL_ROWS = {
    "Total Direct Capital Cost (Accounts 10 to 20)": ["10s - Subtotal", "20s - Subtotal"],
    "Base Construction Cost (Accounts 20 to 30)": ["20s - Subtotal", "30s - Subtotal"],
    "Total Overnight Cost (Accounts 10 to 50)": [
        "10s - Subtotal",
        "Base Construction Cost (Accounts 20 to 30)",
        "50s - Subtotal",
    ],
    "Total Capital Investment Cost (All Accounts)": [
        "Total Overnight Cost (Accounts 10 to 50)",
        "60s - Subtotal",
    ],
}

FINAL_PER_KWE_ROWS = {
    "(Accounts 10 to 20) US$/kWe": "Total Direct Capital Cost (Accounts 10 to 20)",
    "(Accounts 20 to 30) US$/kWe": "Base Construction Cost (Accounts 20 to 30)",
    "(Accounts 10 to 50) US$/kWe": "Total Overnight Cost (Accounts 10 to 50)",
    "(Accounts 10 to 60) US$/kWe": "Total Capital Investment Cost (All Accounts)",
}


def _blank_row(title: str, account=None) -> dict:
    row = {c: np.nan for c in ALL_COLS}
    row["Title"] = title
    row["Account"] = account
    return row


def ensure_rows_exist(db: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure all derived rows exist (by Title). If missing, append them.
    """
    if not set(ALL_COLS).issubset(db.columns):
        missing = set(ALL_COLS) - set(db.columns)
        raise ValueError(f"DB missing columns: {sorted(missing)}")

    existing_titles = set(db["Title"].astype(str).tolist())
    rows_to_add = []
    for title, acct in REQUIRED_DERIVED_ROWS:
        if title not in existing_titles:
            rows_to_add.append(_blank_row(title, acct))

    if rows_to_add:
        db = pd.concat([db, pd.DataFrame(rows_to_add)], ignore_index=True)

    return db


def _index_rows_by_value(series: pd.Series) -> dict[str, list[int]]:
    rows: dict[str, list[int]] = {}
    for pos, value in enumerate(series.to_numpy()):
        rows.setdefault(str(value).strip(), []).append(pos)
    return rows


def _sum_accounts(db: pd.DataFrame, account_rows: dict[str, list[int]], accounts: list[str], col: str) -> float:
    rows = [idx for account in accounts for idx in account_rows.get(str(account), [])]
    if not rows:
        return 0.0
    return float(db[col].to_numpy()[rows].sum())


def _sum_titles(db: pd.DataFrame, title_rows: dict[str, list[int]], titles: list[str], col: str) -> float:
    rows = [idx for title in titles for idx in title_rows.get(title, [])]
    if not rows:
        return 0.0
    return float(db[col].to_numpy()[rows].sum())


def _set_account_value(db: pd.DataFrame, account_rows: dict[str, list[int]], account: str, col: str, value: float) -> None:
    rows = account_rows.get(str(account), [])
    if rows:
        db.iloc[rows, db.columns.get_loc(col)] = value


def _set_title_value(db: pd.DataFrame, title_rows: dict[str, list[int]], title: str, col: str, value: float) -> None:
    rows = title_rows.get(title, [])
    if rows:
        db.iloc[rows, db.columns.get_loc(col)] = value


def _roll_up_detail_accounts(db: pd.DataFrame, account_rows: dict[str, list[int]]) -> None:
    for col in ["Factory Equipment Cost", "Site Material Cost", "Site Labor Cost", "Site Labor Hours"]:
        _set_account_value(db, account_rows, "21", col, _sum_accounts(db, account_rows, ACCOUNT_21_DETAIL_ACCOUNTS, col))

    for col in ["Factory Equipment Cost", "Site Material Cost", "Site Labor Cost", "Site Labor Hours"]:
        _set_account_value(db, account_rows, "23", col, _sum_accounts(db, account_rows, ["232.1", "233"], col))


def _update_total_cost_rows(db: pd.DataFrame, account_rows: dict[str, list[int]]) -> None:
    rows = [idx for account in TOTAL_COST_DETAIL_ACCOUNTS for idx in account_rows.get(account, [])]
    if rows:
        total_col = db.columns.get_loc("Total Cost (USD)")
        factory_col = db.columns.get_loc("Factory Equipment Cost")
        labor_col = db.columns.get_loc("Site Labor Cost")
        material_col = db.columns.get_loc("Site Material Cost")
        db.iloc[rows, total_col] = (
            db.iloc[rows, factory_col].to_numpy()
            + db.iloc[rows, labor_col].to_numpy()
            + db.iloc[rows, material_col].to_numpy()
        )


def _update_subtotals(db: pd.DataFrame, account_rows: dict[str, list[int]], title_rows: dict[str, list[int]]) -> None:
    for title, accounts in ACCOUNT_SUBTOTALS.items():
        _set_title_value(db, title_rows, title, "Total Cost (USD)", _sum_accounts(db, account_rows, accounts, "Total Cost (USD)"))

    for col in ["Factory Equipment Cost", "Site Material Cost", "Site Labor Cost", "Site Labor Hours"]:
        _set_title_value(
            db,
            title_rows,
            "20s - Subtotal",
            col,
            _sum_accounts(db, account_rows, ACCOUNT_SUBTOTALS["20s - Subtotal"], col),
        )


def _update_per_kwe_rows(db: pd.DataFrame, title_rows: dict[str, list[int]], reactor_power: float) -> None:
    for prefix, subtotal_title in PER_KWE_ROWS.items():
        subtotal = _sum_titles(db, title_rows, [subtotal_title], "Total Cost (USD)")
        _set_title_value(db, title_rows, f"{prefix} - $/kWe", "Total Cost (USD)", subtotal / reactor_power)

    for col in ["Factory Equipment Cost", "Site Material Cost", "Site Labor Cost"]:
        value = _sum_titles(db, title_rows, ["20s - Subtotal"], col) / reactor_power
        _set_title_value(db, title_rows, "20s - $/kWe", col, value)


def _update_final_totals(db: pd.DataFrame, title_rows: dict[str, list[int]], reactor_power: float) -> None:
    for title, input_titles in FINAL_TOTAL_ROWS.items():
        _set_title_value(db, title_rows, title, "Total Cost (USD)", _sum_titles(db, title_rows, input_titles, "Total Cost (USD)"))

    for title, source_title in FINAL_PER_KWE_ROWS.items():
        value = _sum_titles(db, title_rows, [source_title], "Total Cost (USD)") / reactor_power
        _set_title_value(db, title_rows, title, "Total Cost (USD)", value)


def update_high_level_costs(db: pd.DataFrame, reactor_power: float) -> pd.DataFrame:
    db = ensure_rows_exist(db).copy().reset_index(drop=True)
    db[COST_COLS] = db[COST_COLS].fillna(0.0)
    account_rows = _index_rows_by_value(db["Account"])
    title_rows = _index_rows_by_value(db["Title"])

    _roll_up_detail_accounts(db, account_rows)
    _update_total_cost_rows(db, account_rows)
    _update_subtotals(db, account_rows, title_rows)
    _update_per_kwe_rows(db, title_rows, reactor_power)
    _update_final_totals(db, title_rows, reactor_power)

    return db

def ITC_reduction_factor(itc_level: float) -> float:
    itc_values = [0, 0.06, 0.3, 0.4, 0.5]
    factors = [1, 0.95, 0.73, 0.63, 0.53]
    return float(np.interp(itc_level, itc_values, factors))

def sum_lab_hrs(db: pd.DataFrame) -> float:
    return float(
        db.loc[db["Account"].astype(str).str.strip().isin(["21","22","23","24","26"]), "Site Labor Hours"]
          .fillna(0.0)
          .sum()
    )

def update_cons_duration(db0: pd.DataFrame, db1: pd.DataFrame, ref_duration: float) -> float:
    """Calculate new construction duration based on change in labor hours for accounts 21, 22, 23, 24, and 26.
    The formula is: new_duration = 0.3 * labor_hours_delta * ref_duration + ref_duration, where labor_hours_delta = (new_hours - old_hours) / old_hours.
    this function should be used before the standardization effect is applied.
    """
    def _sum_hours(db):
        return float(
            db.loc[db["Account"].astype(str).str.strip().isin(["21","22","23","24","26"]), "Site Labor Hours"]
              .fillna(0.0)
              .sum()
        )

    sum_old = _sum_hours(db0)
    sum_new = _sum_hours(db1)
    lab_delta = (sum_new - sum_old) / sum_old
    # print(f"in update_cons_duration, sum_old: {sum_old}, sum_new: {sum_new}, lab_delta: {lab_delta}, ref_duration: {ref_duration}")
    return float(0.3 * lab_delta * ref_duration + ref_duration)

def update_cons_duration_2(
    db0: pd.DataFrame,
    db1: pd.DataFrame,
    ref_duration: float,
    prev_cons_duration: float,
    baseline_lab_hours: float,
    reactor_type: str
) -> float:
    """Calculate new construction duration based on change in labor hours for accounts 21, 22, 23, 24, and 26. This should be used after the standardization effect is applied, so the labor hours change should be compared to the baseline labor hours instead of the previous labor hours. NOTE I think I should merge this with the previous function and just pass in the baseline labor hours as an argument.
    """
    def _sum_hours(db):
        return float(
            db.loc[db["Account"].astype(str).str.strip().isin(["21","22","23","24","26"]), "Site Labor Hours"]
              .fillna(0.0)
              .sum()
        )

    sum_old = _sum_hours(db0)
    sum_new = _sum_hours(db1)
    lab_delta = (sum_new - sum_old) / float(baseline_lab_hours)
    # NOTE ref_duration here should be modulized?
    # ref_duration=ref_duration*0.8 
    if reactor_type in ["HTGR", "SFR"]:
        return float(0.3 * lab_delta * ref_duration + float(prev_cons_duration))
    elif reactor_type == "AP1000":
        return float(0.04 * lab_delta * ref_duration + float(prev_cons_duration))
    else:
        raise ValueError(f"Unknown reactor type: {reactor_type}")
