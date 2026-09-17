# src/crt/model/indirect_cost.py
# Indirect costs accounts 31–35, unchanged equations

import pandas as pd

from ..utils.df_ops import setv
from .core_accounts import update_high_level_costs

COLS = [
    "Account", "Title", "Total Cost (USD)",
    "Factory Equipment Cost", "Site Labor Hours",
    "Site Labor Cost", "Site Material Cost"
]


def update_indirect_cost(
    n_th: int,
    standardization_0: float,
    df: pd.DataFrame,
    final_construction_duration: float,
    power: float,
    reactor_type: str
):
    standardization = min(0.7, standardization_0) if n_th == 1 else standardization_0
    factor_35 = (10 / 3) * (1 - standardization)

    db = df.copy()

    sum_new_mat_cost = 0.0
    sum_new_lab_cost = 0.0
    sum_new_lab_hrs = 0.0
    mask = db["Account"].astype(str).str.strip().isin(["21","22","23","24","26"])
    sum_new_mat_cost = float(db.loc[mask, "Site Material Cost"].fillna(0.0).sum())
    sum_new_lab_cost = float(db.loc[mask, "Site Labor Cost"].fillna(0.0).sum())
    sum_new_lab_hrs  = float(db.loc[mask, "Site Labor Hours"].fillna(0.0).sum())
    # print(f"DEBUG: sum_new_mat_cost={sum_new_mat_cost}, sum_new_lab_cost={sum_new_lab_cost}, sum_new_lab_hrs={sum_new_lab_hrs}")


    dur = float(final_construction_duration)
    # print(f"DEBUG: final_construction_duration={dur}, standardization={standardization}, factor_35={factor_35}")
    val31 = (sum_new_mat_cost * 0.785 * sum_new_lab_hrs / dur / 160 / 1058) + sum_new_lab_cost * 0.36
    if reactor_type in ["HTGR", "SFR"]:
        val32 = sum_new_lab_cost * 0.36 * 3.661 * dur / 72
        val35 = (0.27017603 * val32) * factor_35
    elif reactor_type == "AP1000":
        val32 = sum_new_lab_cost * 0.36 * 1.2 * dur / 42
        val35 = 0.27017603 * val32 
    val33 = 0.04207006 * val32
    val34 = 0.00354234616938 * val32
    # print(f"DEBUG: val31={val31}, val32={val32}, val33={val33}, val34={val34}, val35={val35}")
    setv(db, 31, "Total Cost (USD)", val31)
    setv(db, 32, "Total Cost (USD)", val32)
    setv(db, 33, "Total Cost (USD)", val33)
    setv(db, 34, "Total Cost (USD)", val34)
    setv(db, 35, "Total Cost (USD)", val35)

    return update_high_level_costs(db, power)[COLS].copy()
