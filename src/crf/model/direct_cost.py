# src/crf/model/direct_cost.py
# Direct-cost pipeline:
#   add_factory_cost -> add_land_cost -> add_commercial_bop
#   -> add_non_safety_related_rb -> add_modular_civil_construction
#   -> add_bulk_ordering -> add_reworking_productivity
# Returns updated df and construction duration (no supply-chain delay yet)

import numpy as np
import pandas as pd

from ..utils.df_ops import getv, setv, mulv
from .core_accounts import (
    ACCOUNT_21_DETAIL_ACCOUNTS,
    DIRECT_DETAIL_ACCOUNTS,
    TOTAL_COST_DETAIL_ACCOUNTS,
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
# exclude account 25 because it is the initial fuel cost and 
# should not be affected by rework. Those accounts are end level accounts
# that do not have sub-accounts 
ACCT_DIRECT = DIRECT_DETAIL_ACCOUNTS


def _total_occ_per_kwe(df: pd.DataFrame, power: float) -> float:
    db = update_high_level_costs(df.copy(), power)
    return float(
        db.loc[
            db["Title"].eq("Total Overnight Cost (Accounts 10 to 50)"),
            "Total Cost (USD)",
        ].iloc[0]
        / power
    )


def _record_delta(trace, key: str, before: pd.DataFrame, after: pd.DataFrame, power: float):
    if trace is not None:
        trace[key] = _total_occ_per_kwe(after, power) - _total_occ_per_kwe(before, power)


def add_factory_cost(df: pd.DataFrame, power: float, f_22: float, f_2321: float, num_orders: int, reactor_type: str):
    db = df.copy()
    if reactor_type in ["HTGR", "SFR"]:
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


def _grade_ref_duration(reactor_type: str, construction_duration_0: float | None = None) -> float:
    if construction_duration_0 is not None:
        return float(construction_duration_0)
    if reactor_type == "HTGR":
        return 125
    if reactor_type == "SFR":
        return 80
    if reactor_type == "AP1000":
        return 76
    raise ValueError(f"Unknown reactor type: {reactor_type}")


def add_commercial_bop(
    df: pd.DataFrame,
    BOP_grade_0: str,
    power: float,
    reactor_type: str,
    n_th: int,
    trace=None,
):
    """Apply the commercial BOP grade lever."""
    if reactor_type in ["HTGR", "SFR"]:
        BOP_grade = BOP_grade_0 if n_th == 1 else "non_nuclear"
    elif reactor_type == "AP1000":
        BOP_grade = BOP_grade_0 if n_th == 1 else "nuclear"
    else:
        raise ValueError(f"Unknown reactor type: {reactor_type}")

    db = df.copy()
    before_bop = db.copy()
    if BOP_grade == "non_nuclear":
        if reactor_type in ["HTGR", "SFR"]:
            mulv(
                db, [213],
                ["Site Material Cost", "Site Labor Cost", "Site Labor Hours", "Factory Equipment Cost"],
                0.6
            )
            # for 232.1 apply to factory+labor but NOT material 
            mulv(
                db, ["232.1"],
                ["Factory Equipment Cost", "Site Labor Cost", "Site Labor Hours"],
                0.6
            )
        elif reactor_type == "AP1000":
            # for AP1000 applied BOP tpp 213.1 and 232.1 but applied to 213 instead
            mulv(
                db, [ 213, "232.1"],
                ["Site Material Cost", "Site Labor Cost", "Site Labor Hours", "Factory Equipment Cost"],
                0.6
            )
    _record_delta(trace, "Commercial BOP", before_bop, db, power)
    return update_high_level_costs(db, power)[COLS].copy()


def add_non_safety_related_rb(
    df: pd.DataFrame,
    RB_grade_0: str,
    power: float,
    trace=None,
):
    """Apply the non-safety-related reactor building lever."""
    db = df.copy()
    before_rb = db.copy()
    if RB_grade_0 == "non_nuclear":
        mulv(
            db, [212],
            ["Site Material Cost", "Site Labor Cost", "Site Labor Hours", "Factory Equipment Cost"],
            0.6,
        )
    _record_delta(trace, "Non safety-related Reactor Building", before_rb, db, power)
    return update_high_level_costs(db, power)[COLS].copy()


def add_modular_civil_construction(
    df: pd.DataFrame,
    power: float,
    reactor_type: str,
    n_th: int,
    mod_0: str,
    base_duration: float,
    trace=None,
):
    """Apply the modular civil construction lever."""
    # applying modularity civil construction if HTGR of SFR, for n>=2 assume 
    # modularized, if other reactor type such as AP1000, we assume no modularity 
    # effect on duration for now.
    if reactor_type in ["HTGR", "SFR"]:
        mod = mod_0 if n_th == 1 else "modularized"    
    elif reactor_type == "AP1000":
        mod = mod_0 if n_th == 1 else "non_modularized"

    mod_factor = 0.8 if mod == "modularized" else 1.0 # NOTE see excel Relationship sheet D4
    # NOTE in excel tool HTGR does nothing here, SFR factory cost of 21 with the 20% reduction 
    # with AP1000 all labor cost with the 20% reduction in 20s accounts, 
    db = df.copy()
    before_mod = db.copy()
    if reactor_type == "SFR":
        for acct in ACCOUNT_21_DETAIL_ACCOUNTS:
            setv(db, acct, "Factory Equipment Cost", float(getv(db, acct, "Factory Equipment Cost")) * mod_factor)
        db = update_high_level_costs(db, power)[COLS].copy()
    elif reactor_type == "AP1000":
        for acct in ACCT_DIRECT:
            setv(db, acct, "Site Labor Cost", float(getv(db, acct, "Site Labor Cost")) * mod_factor)
            setv(db, acct, "Site Labor Hours", float(getv(db, acct, "Site Labor Hours")) * mod_factor)
        db = update_high_level_costs(db, power)[COLS].copy()
    _record_delta(trace, "Modular Construction", before_mod, db, power)

    return db, base_duration * mod_factor


def add_bulk_ordering(df: pd.DataFrame, num_orders: int, f_22: float, f_2321: float, power: float, reactor_type: str, trace=None):
    """
    Applies average learning reduction to factory equipment cost of 22 and 232.1,
    but keeps factory-building portion intact.
    """
    db = df.copy()
    if reactor_type == "HTGR":
        lr22 = 0.1802341659291420
        lr2321 = 0.2607462372040820
    elif reactor_type == "SFR":
        lr22 = 0.209920296472118
        lr2321 = 0.222118386536136
    elif reactor_type == "AP1000":
        # no learning for AP1000 since it is already modularized and we assume no modularity effect
        lr22 = 0.0
        lr2321 = 0.0
    else:
        raise ValueError(f"Unknown reactor type: {reactor_type}")

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

    db2 = update_high_level_costs(db, power)[COLS].copy()
    _record_delta(trace, "Bulk-ordering", df, db2, power)
    return db2


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
    baseline_lab_hours,
    ref_duration: float | None = None,
    trace=None
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

    if reactor_type == "HTGR":
        rework = (-0.69 * design_completion + 1.69) * (-0.125 * ae_exp + 1.25) * (-0.125 * ce_exp + 1.25)
        ref_duration = 125 if ref_duration is None else ref_duration
    elif reactor_type == "SFR":
        rework = (-0.9 * design_completion + 1.9) * (-0.15 * ae_exp + 1.3) * (-0.15 * ce_exp + 1.3)
        ref_duration = 80 if ref_duration is None else ref_duration
    elif reactor_type == "AP1000":
        rework = (-0.69 * design_completion + 1.69) * (-0.125 * ae_exp + 1.25) * (-0.125 * ce_exp + 1.25)
        ref_duration = 76 if ref_duration is None else ref_duration
    else:
        raise ValueError(f"Unknown reactor type: {reactor_type}")
    db = df.copy()

    for acct in ACCT_DIRECT:
        setv(db, acct, "Factory Equipment Cost", float(getv(df, acct, "Factory Equipment Cost")) * rework)
        setv(db, acct, "Site Material Cost", float(getv(df, acct, "Site Material Cost")) * rework)
        setv(db, acct, "Site Labor Hours", float(getv(df, acct, "Site Labor Hours")) * rework)
        setv(db, acct, "Site Labor Cost", float(getv(df, acct, "Site Labor Cost")) * rework)

    rework_db = update_high_level_costs(db, power)[COLS].copy()
    _record_delta(trace, "Elimination of rework", df, rework_db, power)

    db = rework_db.copy()
    for acct in ACCT_DIRECT:
        setv(db, acct, "Site Labor Hours", float(getv(rework_db, acct, "Site Labor Hours")) / productivity)
        setv(db, acct, "Site Labor Cost", float(getv(rework_db, acct, "Site Labor Cost")) / productivity)

    db2 = update_high_level_costs(db, power)[COLS].copy()
    _record_delta(trace, "Labor productivity", rework_db, db2, power)
    new_dur = float(update_cons_duration_2(df, db2, ref_duration, prev_cons_duration, baseline_lab_hours, reactor_type))
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
    mod_0: str,
    construction_duration_0: float | None = None,
    trace=None
):
    reactor_df, power = store.get_baseline(reactor_type)
    db, baseline_lab_hours = add_factory_cost(reactor_df, power, f_22, f_2321, num_orders, reactor_type)   
    # all Total Cost (USD) columns should be 0 
    # when accounts are in 20s
    db.loc[db["Account"].isin(TOTAL_COST_DETAIL_ACCOUNTS), "Total Cost (USD)"] = 0.0
    db = update_high_level_costs(db, power)[COLS].copy()
    db = add_land_cost(db, land_cost_per_acre_0, power)
    before_grades = db.copy()
    db = add_commercial_bop(db, BOP_grade_0, power, reactor_type, n_th, trace=trace)
    db = add_non_safety_related_rb(db, RB_grade_0, power, trace=trace)
    ref_duration = _grade_ref_duration(reactor_type, construction_duration_0)
    prev_dur = update_cons_duration(before_grades, db, ref_duration)
    db, prev_dur = add_modular_civil_construction(db, power, reactor_type, n_th, mod_0, prev_dur, trace=trace)
    db = add_bulk_ordering(db, num_orders, f_22, f_2321, power, reactor_type, trace=trace)
    db, dur_no_delay = add_reworking_productivity(
        db, reactor_type, n_th,
        design_completion_0, ae_exp_0, N_AE, ce_exp_0, N_cons,
        power, prev_dur, baseline_lab_hours, ref_duration=ref_duration, trace=trace
    )
    return db, dur_no_delay
