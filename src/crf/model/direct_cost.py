# src/crf/model/direct_cost.py
# Direct-cost pipeline:
#   add_factory_cost -> add_land_cost -> add_BOP_RP_grades -> add_bulk_ordering -> add_reworking_productivity
# Returns updated df and construction duration (no supply-chain delay yet)

import numpy as np
import pandas as pd

from ..utils.df_ops import getv, setv, mulv
from .core_accounts import (
    update_high_level_costs,
    sum_lab_hrs,
    update_cons_duration,
    update_cons_duration_2,
)

COLS = [
    "Account", "Title", "Total Cost (USD)",
    "Factory Equipment Cost", "Site Labor Hours",
    "Site Labor Cost", "Site Material Cost"
]

ACCT_DIRECT = [212, 213, "211 plus 214 to 219", 22, "232.1", 233, 24, 26]


def add_factory_cost(df: pd.DataFrame, power: float, f_22: float, f_2321: float, num_orders: int):
    db = df.copy()

    # Add factory-building shares; clear old values first (keep numeric dtype)
    setv(db, 22, "Factory Equipment Cost", np.nan)
    setv(db, "232.1", "Factory Equipment Cost", np.nan)

    setv(db, 22, "Factory Equipment Cost", float(getv(df, 22, "Factory Equipment Cost")) + f_22 / num_orders)
    setv(db, "232.1", "Factory Equipment Cost", float(getv(df, "232.1", "Factory Equipment Cost")) + f_2321 / num_orders)

    db = update_high_level_costs(db, power)[COLS].copy()
    baseline_lab_hours = sum_lab_hrs(db)
    return db, baseline_lab_hours


def add_land_cost(df: pd.DataFrame, land_cost_per_acre: float, power: float):
    db = df.copy()
    factor = land_cost_per_acre / 22000.0
    for acct in [11, 12, 51]:
        setv(db, acct, "Total Cost (USD)", np.nan)
        setv(db, acct, "Total Cost (USD)", float(getv(df, acct, "Total Cost (USD)")) * factor)
    return update_high_level_costs(db, power)[COLS].copy()


def add_BOP_RP_grades(
    df: pd.DataFrame,
    RB_grade_0: str,
    BOP_grade_0: str,
    power: float,
    reactor_type: str,
    n_th: int,
    mod_0: str
):
    # RB grade does not change; BOP becomes non_nuclear after FOAK
    RB_grade = RB_grade_0
    BOP_grade = BOP_grade_0 if n_th == 1 else "non_nuclear"

    db = df.copy()

    if RB_grade == "non_nuclear":
        mulv(
            db, [212],
            ["Site Material Cost", "Site Labor Cost", "Site Labor Hours", "Factory Equipment Cost"],
            0.6
        )

    if BOP_grade == "non_nuclear":
        mulv(
            db, [213],
            ["Site Material Cost", "Site Labor Cost", "Site Labor Hours", "Factory Equipment Cost"],
            0.6
        )
        # for 232.1 apply to factory+labor but NOT material (matches your original)
        mulv(
            db, ["232.1"],
            ["Factory Equipment Cost", "Site Labor Cost", "Site Labor Hours"],
            0.6
        )

    db2 = update_high_level_costs(db, power)[COLS].copy()

    # duration update from grade change
    duration_ref = 125 if reactor_type == "Concept A" else 80
    new_dur = float(update_cons_duration(df, db2, duration_ref))

    # modularity factor on duration; for n>=2 assume modularized
    mod = mod_0 if n_th == 1 else "modularized"
    mod_factor = 0.8 if mod == "modularized" else 1.0

    return db2, new_dur * mod_factor


def add_bulk_ordering(df: pd.DataFrame, num_orders: int, f_22: float, f_2321: float, power: float):
    """
    Applies average learning reduction to factory equipment cost of 22 and 232.1,
    but keeps factory-building portion intact.
    """
    db = df.copy()

    lr22 = 0.1802341659291420
    lr2321 = 0.2607462372040820

    red22 = 0.0
    red2321 = 0.0
    for ith in range(1, num_orders + 1):
        red22 += ((1 - lr22) ** np.log2(ith)) / num_orders
        red2321 += ((1 - lr2321) ** np.log2(ith)) / num_orders

    old22 = float(getv(df, 22, "Factory Equipment Cost"))
    new22 = red22 * (old22 - (f_22 / num_orders)) + (f_22 / num_orders)
    setv(db, 22, "Factory Equipment Cost", new22)

    old2321 = float(getv(df, "232.1", "Factory Equipment Cost"))
    new2321 = red2321 * (old2321 - (f_2321 / num_orders)) + (f_2321 / num_orders)
    setv(db, "232.1", "Factory Equipment Cost", new2321)

    return update_high_level_costs(db, power)[COLS].copy()


def add_reworking_productivity(
    df: pd.DataFrame,
    reactor_type: str,
    n_th: int,
    design_completion_0: float,
    ae_exp_0: float,
    N_AE: float,
    ce_exp_0: float,
    N_cons: float,
    power: float,
    prev_cons_duration: float,
    baseline_lab_hours
):
    if n_th == 1:
        design_completion = design_completion_0
        ae_exp = ae_exp_0
        ce_exp = ce_exp_0
    else:
        design_completion = 1.0
        ae_exp = min(ae_exp_0 + (2 / N_AE) * (n_th - 1), 2)
        ce_exp = min(ce_exp_0 + (2 / N_cons) * (n_th - 1), 2)

    productivity = 0.145 * ce_exp + 0.71

    if reactor_type == "Concept B":
        rework = (-0.9 * design_completion + 1.9) * (-0.15 * ae_exp + 1.3) * (-0.15 * ce_exp + 1.3)
        ref_duration = 80
    else:
        rework = (-0.69 * design_completion + 1.69) * (-0.125 * ae_exp + 1.25) * (-0.125 * ce_exp + 1.25)
        ref_duration = 125

    db = df.copy()

    for acct in ACCT_DIRECT:
        setv(db, acct, "Factory Equipment Cost", float(getv(df, acct, "Factory Equipment Cost")) * rework)
        setv(db, acct, "Site Material Cost", float(getv(df, acct, "Site Material Cost")) * rework)
        setv(db, acct, "Site Labor Hours", float(getv(df, acct, "Site Labor Hours")) * rework / productivity)
        setv(db, acct, "Site Labor Cost", float(getv(df, acct, "Site Labor Cost")) * rework / productivity)

    db2 = update_high_level_costs(db, power)[COLS].copy()

    new_dur = float(update_cons_duration_2(df, db2, ref_duration, prev_cons_duration, baseline_lab_hours))
    return db2, new_dur


def update_direct_cost(
    store,
    reactor_type: str,
    n_th: int,
    f_22: float,
    f_2321: float,
    land_cost_per_acre_0: float,
    RB_grade_0: str,
    BOP_grade_0: str,
    num_orders: int,
    design_completion_0: float,
    ae_exp_0: float,
    N_AE: float,
    ce_exp_0: float,
    N_cons: float,
    mod_0: str
):
    reactor_df, power = store.get_baseline(reactor_type)

    db, baseline_lab_hours = add_factory_cost(reactor_df, power, f_22, f_2321, num_orders)
    db = add_land_cost(db, land_cost_per_acre_0, power)
    db, prev_dur = add_BOP_RP_grades(db, RB_grade_0, BOP_grade_0, power, reactor_type, n_th, mod_0)
    db = add_bulk_ordering(db, num_orders, f_22, f_2321, power)
    db, dur_no_delay = add_reworking_productivity(
        db, reactor_type, n_th,
        design_completion_0, ae_exp_0, N_AE, ce_exp_0, N_cons,
        power, prev_dur, baseline_lab_hours
    )

    return db, dur_no_delay
