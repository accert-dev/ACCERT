import numpy as np
import pandas as pd

def update_high_level_costs(db: pd.DataFrame, reactor_power: float) -> pd.DataFrame:
    # account 21
    db.loc[db.Account == 21, "Factory Equipment Cost"] = (
        db.loc[db.Account == 212, "Factory Equipment Cost"].values
        + db.loc[db.Account == 213, "Factory Equipment Cost"].values
        + db.loc[db.Account == "211 plus 214 to 219", "Factory Equipment Cost"].values
    )
    db.loc[db.Account == 21, "Site Material Cost"] = (
        db.loc[db.Account == 212, "Site Material Cost"].values
        + db.loc[db.Account == 213, "Site Material Cost"].values
        + db.loc[db.Account == "211 plus 214 to 219", "Site Material Cost"].values
    )
    db.loc[db.Account == 21, "Site Labor Cost"] = (
        db.loc[db.Account == 212, "Site Labor Cost"].values
        + db.loc[db.Account == 213, "Site Labor Cost"].values
        + db.loc[db.Account == "211 plus 214 to 219", "Site Labor Cost"].values
    )
    db.loc[db.Account == 21, "Site Labor Hours"] = (
        db.loc[db.Account == 212, "Site Labor Hours"].values
        + db.loc[db.Account == 213, "Site Labor Hours"].values
        + db.loc[db.Account == "211 plus 214 to 219", "Site Labor Hours"].values
    )

    # account 23
    db.loc[db.Account == 23, "Factory Equipment Cost"] = (
        db.loc[db.Account == "232.1", "Factory Equipment Cost"].values
        + db.loc[db.Account == 233, "Factory Equipment Cost"].values
    )
    db.loc[db.Account == 23, "Site Material Cost"] = (
        db.loc[db.Account == "232.1", "Site Material Cost"].values
        + db.loc[db.Account == 233, "Site Material Cost"].values
    )
    db.loc[db.Account == 23, "Site Labor Cost"] = (
        db.loc[db.Account == "232.1", "Site Labor Cost"].values
        + db.loc[db.Account == 233, "Site Labor Cost"].values
    )
    db.loc[db.Account == 23, "Site Labor Hours"] = (
        db.loc[db.Account == "232.1", "Site Labor Hours"].values
        + db.loc[db.Account == 233, "Site Labor Hours"].values
    )

    # total costs for 21..26 components
    for x in [21, 212, 213, "211 plus 214 to 219", 22, 23, "232.1", 233, 24, 26]:
        db.loc[db["Account"] == x, "Total Cost (USD)"] = (
            db.loc[db["Account"] == x, "Factory Equipment Cost"]
            + db.loc[db["Account"] == x, "Site Labor Cost"]
            + db.loc[db["Account"] == x, "Site Material Cost"]
        )

    # subtotals
    db.loc[db["Title"] == "10s - Subtotal", "Total Cost (USD)"] = db.loc[
        db["Account"].isin([11, 12, 13, 14, 15, 16, 18]), "Total Cost (USD)"
    ].sum()

    db.loc[db["Title"] == "20s - Subtotal", "Total Cost (USD)"] = db.loc[
        db["Account"].isin([21, 22, 23, 24, 25, 26, 28]), "Total Cost (USD)"
    ].sum()

    db.loc[db["Title"] == "30s - Subtotal", "Total Cost (USD)"] = db.loc[
        db["Account"].isin([31, 32, 33, 34, 35]), "Total Cost (USD)"
    ].sum()

    db.loc[db["Title"] == "50s - Subtotal", "Total Cost (USD)"] = db.loc[
        db["Account"].isin([51, 52, 54]), "Total Cost (USD)"
    ].sum()

    db.loc[db["Title"] == "60s - Subtotal", "Total Cost (USD)"] = db.loc[
        db["Account"].isin([62]), "Total Cost (USD)"
    ].sum()

    # $/kWe lines
    for t in ["10s", "20s", "30s", "40s", "50s", "60s"]:
        db.loc[db["Title"] == f"{t} - $/kWe", "Total Cost (USD)"] = (
            db.loc[db["Title"] == f"{t} - Subtotal", "Total Cost (USD)"].values / reactor_power
        )

    # final rollups
    db.loc[db["Title"] == "Total Direct Capital Cost (Accounts 10 to 20)", "Total Cost (USD)"] = (
        db.loc[db["Title"] == "10s - Subtotal", "Total Cost (USD)"].values
        + db.loc[db["Title"] == "20s - Subtotal", "Total Cost (USD)"].values
    )

    db.loc[db["Title"] == "Base Construction Cost (Accounts 10 to 30)", "Total Cost (USD)"] = (
        db.loc[db["Title"] == "Total Direct Capital Cost (Accounts 10 to 20)", "Total Cost (USD)"].values
        + db.loc[db["Title"] == "30s - Subtotal", "Total Cost (USD)"].values
    )

    db.loc[db["Title"] == "Total Overnight Cost (Accounts 10 to 50)", "Total Cost (USD)"] = (
        db.loc[db["Title"] == "Base Construction Cost (Accounts 10 to 30)", "Total Cost (USD)"].values
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
    db.loc[db["Title"] == "(Accounts 10 to 30) US$/kWe", "Total Cost (USD)"] = (
        db.loc[db["Title"] == "Base Construction Cost (Accounts 10 to 30)", "Total Cost (USD)"].values / reactor_power
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

def sum_lab_hrs(db: pd.DataFrame):
    return (
        db.loc[db.Account == 21, "Site Labor Hours"].values
        + db.loc[db.Account == 22, "Site Labor Hours"].values
        + db.loc[db.Account == 23, "Site Labor Hours"].values
        + db.loc[db.Account == 24, "Site Labor Hours"].values
        + db.loc[db.Account == 26, "Site Labor Hours"].values
    )

def update_cons_duration(db0: pd.DataFrame, db1: pd.DataFrame, ref_duration: float):
    sum_old = (
        db0.loc[db0.Account == 21, "Site Labor Hours"].values
        + db0.loc[db0.Account == 22, "Site Labor Hours"].values
        + db0.loc[db0.Account == 23, "Site Labor Hours"].values
        + db0.loc[db0.Account == 24, "Site Labor Hours"].values
        + db0.loc[db0.Account == 26, "Site Labor Hours"].values
    )
    sum_new = (
        db1.loc[db1.Account == 21, "Site Labor Hours"].values
        + db1.loc[db1.Account == 22, "Site Labor Hours"].values
        + db1.loc[db1.Account == 23, "Site Labor Hours"].values
        + db1.loc[db1.Account == 24, "Site Labor Hours"].values
        + db1.loc[db1.Account == 26, "Site Labor Hours"].values
    )
    lab_delta = (sum_new - sum_old) / sum_old
    return 0.3 * lab_delta * ref_duration + ref_duration

def update_cons_duration_2(db0, db1, ref_duration, prev_cons_duration, baseline_lab_hours):
    sum_old = (
        db0.loc[db0.Account == 21, "Site Labor Hours"].values
        + db0.loc[db0.Account == 22, "Site Labor Hours"].values
        + db0.loc[db0.Account == 23, "Site Labor Hours"].values
        + db0.loc[db0.Account == 24, "Site Labor Hours"].values
        + db0.loc[db0.Account == 26, "Site Labor Hours"].values
    )
    sum_new = (
        db1.loc[db1.Account == 21, "Site Labor Hours"].values
        + db1.loc[db1.Account == 22, "Site Labor Hours"].values
        + db1.loc[db1.Account == 23, "Site Labor Hours"].values
        + db1.loc[db1.Account == 24, "Site Labor Hours"].values
        + db1.loc[db1.Account == 26, "Site Labor Hours"].values
    )
    lab_delta = (sum_new - sum_old) / baseline_lab_hours
    return 0.3 * lab_delta * ref_duration + prev_cons_duration
