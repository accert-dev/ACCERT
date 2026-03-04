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


def update_high_level_costs(db: pd.DataFrame, reactor_power: float) -> pd.DataFrame:
    db = ensure_rows_exist(db)
    # change all nan to 0 for cost calculations (but keep original db unchanged for later use)
    db = db.copy()
    db[COST_COLS] = db[COST_COLS].fillna(0.0)
    # account 21
    # Note when sum up the higher lever account like 21,  we need to make sure there are
    # lower level accounts (like 211 plus 214 to 219) to be added before the sum, otherwise 
    # the sum might lead to an empty value and the final result will be misleading.

    db.loc[db.Account == "21", "Factory Equipment Cost"] = (
        db.loc[db.Account == "212", "Factory Equipment Cost"].values
        + db.loc[db.Account == "213", "Factory Equipment Cost"].values
        + db.loc[db.Account == "211 plus 214 to 219", "Factory Equipment Cost"].values
    )
    db.loc[db.Account == "21", "Site Material Cost"] = (
        db.loc[db.Account == "212", "Site Material Cost"].values
        + db.loc[db.Account == "213", "Site Material Cost"].values
        + db.loc[db.Account == "211 plus 214 to 219", "Site Material Cost"].values
    )
    db.loc[db.Account == "21", "Site Labor Cost"] = (
        db.loc[db.Account == "212", "Site Labor Cost"].values
        + db.loc[db.Account == "213", "Site Labor Cost"].values
        + db.loc[db.Account == "211 plus 214 to 219", "Site Labor Cost"].values
    )
    db.loc[db.Account == "21", "Site Labor Hours"] = (
        db.loc[db.Account == "212", "Site Labor Hours"].values
        + db.loc[db.Account == "213", "Site Labor Hours"].values
        + db.loc[db.Account == "211 plus 214 to 219", "Site Labor Hours"].values
    )


    # account 23
    db.loc[db.Account == "23", "Factory Equipment Cost"] = (
        db.loc[db.Account == "232.1", "Factory Equipment Cost"].values
        + db.loc[db.Account == "233", "Factory Equipment Cost"].values
    )
    db.loc[db.Account == "23", "Site Material Cost"] = (
        db.loc[db.Account == "232.1", "Site Material Cost"].values
        + db.loc[db.Account == "233", "Site Material Cost"].values
    )
    db.loc[db.Account == "23", "Site Labor Cost"] = (
        db.loc[db.Account == "232.1", "Site Labor Cost"].values
        + db.loc[db.Account == "233", "Site Labor Cost"].values
    )
    db.loc[db.Account == "23", "Site Labor Hours"] = (
        db.loc[db.Account == "232.1", "Site Labor Hours"].values
        + db.loc[db.Account == "233", "Site Labor Hours"].values
    )

    # total costs for all accounts should be updated except the lines
    # with no Account (subtotals, $/kWe, and final results) but only 
    # accounts under 20s has factory equipment costs, labor hours, and 
    # labor costs, so we can skip accounts 10s, 30s 50s and 60s

    for x in ['21', '211 plus 214 to 219', '212', '213', '22', '23', '232.1', '233', '24', '25', '26']:
        db.loc[db["Account"] == x, "Total Cost (USD)"] = (
            db.loc[db["Account"] == x, "Factory Equipment Cost"]
            + db.loc[db["Account"] == x, "Site Labor Cost"]
            + db.loc[db["Account"] == x, "Site Material Cost"]
        )


    # subtotals
    db.loc[db["Title"] == "10s - Subtotal", "Total Cost (USD)"] = db.loc[
        db["Account"].isin(["11", "12", "13", "14", "15", "16", "18"]), "Total Cost (USD)"
    ].fillna(0.0).sum()

    db.loc[db["Title"] == "20s - Subtotal", "Total Cost (USD)"] = db.loc[
        db["Account"].isin(["21", "22", "23", "24", "25", "26", "28"]), "Total Cost (USD)"
    ].fillna(0.0).sum()

    db.loc[db["Title"] == "20s - Subtotal", "Factory Equipment Cost"] = db.loc[
        db["Account"].isin(["21", "22", "23", "24", "25", "26", "28"]), "Factory Equipment Cost"
    ].fillna(0.0).sum()

    db.loc[db["Title"] == "20s - Subtotal", "Site Material Cost"] = db.loc[
        db["Account"].isin(["21", "22", "23", "24", "25", "26", "28"]), "Site Material Cost"
    ].fillna(0.0).sum()

    db.loc[db["Title"] == "20s - Subtotal", "Site Labor Cost"] = db.loc[
        db["Account"].isin(["21", "22", "23", "24", "25", "26", "28"]), "Site Labor Cost"
    ].fillna(0.0).sum()

    db.loc[db["Title"] == "20s - Subtotal", "Site Labor Hours"] = db.loc[
        db["Account"].isin(["21", "22", "23", "24", "25", "26", "28"]), "Site Labor Hours"
    ].fillna(0.0).sum()

    db.loc[db["Title"] == "30s - Subtotal", "Total Cost (USD)"] = db.loc[
        db["Account"].isin(["31", "32", "33", "34", "35"]), "Total Cost (USD)"
    ].fillna(0.0).sum()

    db.loc[db["Title"] == "50s - Subtotal", "Total Cost (USD)"] = db.loc[
        db["Account"].isin(["51", "52", "54"]), "Total Cost (USD)"
    ].fillna(0.0).sum()

    db.loc[db["Title"] == "60s - Subtotal", "Total Cost (USD)"] = db.loc[
        db["Account"].isin(["62"]), "Total Cost (USD)"
    ].fillna(0.0).sum()

    # $/kWe lines
    for t in ["10s", "20s", "30s", "50s", "60s"]:
        db.loc[db["Title"] == f"{t} - $/kWe", "Total Cost (USD)"] = (
            db.loc[db["Title"] == f"{t} - Subtotal", "Total Cost (USD)"].values / reactor_power
        )
    # 20s equipment, material, labor costs per kWe
    db.loc[db["Title"] == "20s - $/kWe", "Factory Equipment Cost"] = (
        db.loc[db["Title"] == "20s - Subtotal", "Factory Equipment Cost"].values / reactor_power
    )
    db.loc[db["Title"] == "20s - $/kWe", "Site Material Cost"] = (
        db.loc[db["Title"] == "20s - Subtotal", "Site Material Cost"].values / reactor_power
    )
    db.loc[db["Title"] == "20s - $/kWe", "Site Labor Cost"] = (
        db.loc[db["Title"] == "20s - Subtotal", "Site Labor Cost"].values / reactor_power
    )

    # final rollups
    db.loc[db["Title"] == "Total Direct Capital Cost (Accounts 10 to 20)", "Total Cost (USD)"] = (
        db.loc[db["Title"] == "10s - Subtotal", "Total Cost (USD)"].values
        + db.loc[db["Title"] == "20s - Subtotal", "Total Cost (USD)"].values
    )

    db.loc[db["Title"] == "Base Construction Cost (Accounts 20 to 30)", "Total Cost (USD)"] = (
        + db.loc[db["Title"] == "20s - Subtotal", "Total Cost (USD)"].values
        + db.loc[db["Title"] == "30s - Subtotal", "Total Cost (USD)"].values
    )

    db.loc[db["Title"] == "Total Overnight Cost (Accounts 10 to 50)", "Total Cost (USD)"] = (
        db.loc[db["Title"] == "10s - Subtotal", "Total Cost (USD)"].values
        + db.loc[db["Title"] == "Base Construction Cost (Accounts 20 to 30)", "Total Cost (USD)"].values
        + db.loc[db["Title"] == "50s - Subtotal", "Total Cost (USD)"].values
    )

    db.loc[db["Title"] == "Total Capital Investment Cost (All Accounts)", "Total Cost (USD)"] = (
        db.loc[db["Title"] == "Total Overnight Cost (Accounts 10 to 50)", "Total Cost (USD)"].values
        + db.loc[db["Title"] == "60s - Subtotal", "Total Cost (USD)"].values
    )

    # final $/kWe
    db.loc[db["Title"] == "(Accounts 10 to 20) US$/kWe", "Total Cost (USD)"] = (
        db.loc[db["Title"] == "Total Direct Capital Cost (Accounts 10 to 20)", "Total Cost (USD)"].values / reactor_power
    )
    db.loc[db["Title"] == "(Accounts 20 to 30) US$/kWe", "Total Cost (USD)"] = (
        db.loc[db["Title"] == "Base Construction Cost (Accounts 20 to 30)", "Total Cost (USD)"].values / reactor_power
    )
    db.loc[db["Title"] == "(Accounts 10 to 50) US$/kWe", "Total Cost (USD)"] = (
        db.loc[db["Title"] == "Total Overnight Cost (Accounts 10 to 50)", "Total Cost (USD)"].values / reactor_power
    )
    db.loc[db["Title"] == "(Accounts 10 to 60) US$/kWe", "Total Cost (USD)"] = (
        db.loc[db["Title"] == "Total Capital Investment Cost (All Accounts)", "Total Cost (USD)"].values / reactor_power
    )
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
    print(f"in update_cons_duration, sum_old: {sum_old}, sum_new: {sum_new}, lab_delta: {lab_delta}, ref_duration: {ref_duration}")
    return float(0.3 * lab_delta * ref_duration + ref_duration)

def update_cons_duration_2(
    db0: pd.DataFrame,
    db1: pd.DataFrame,
    ref_duration: float,
    prev_cons_duration: float,
    baseline_lab_hours: float
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
    return float(0.3 * lab_delta * ref_duration + float(prev_cons_duration))

