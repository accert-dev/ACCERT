# src/crf/model/finance.py
# Insurance, interest, ITC application

import numpy as np
import pandas as pd
from ..utils.df_ops import setv
from .core_accounts import update_high_level_costs, ITC_reduction_factor

COLS = [
    "Account", "Title", "Total Cost (USD)",
    "Factory Equipment Cost", "Site Labor Hours",
    "Site Labor Cost", "Site Material Cost"
]


def insurance_cost_update(base_df, updated_df, power):
    # Ensure derived rows (subtotals/totals) exist and are up-to-date
    base_df = update_high_level_costs(base_df.copy(), power)
    updated_df = update_high_level_costs(updated_df.copy(), power)

    ref_20 = float(base_df.loc[base_df["Title"].eq("20s - Subtotal"), "Total Cost (USD)"].iloc[0])
    ref_30 = float(base_df.loc[base_df["Title"].eq("30s - Subtotal"), "Total Cost (USD)"].iloc[0])

    new_20 = float(updated_df.loc[updated_df["Title"].eq("20s - Subtotal"), "Total Cost (USD)"].iloc[0])
    new_30 = float(updated_df.loc[updated_df["Title"].eq("30s - Subtotal"), "Total Cost (USD)"].iloc[0])

    denom = ref_20 + ref_30
    change_factor = 1.0 if denom == 0 else (new_20 + new_30) / denom

    # Update Account 52 (Insurance)
    mask52 = updated_df["Account"].astype(str).str.strip().eq("52")
    if not mask52.any():
        raise KeyError("Account 52 (Insurance) not found in dataframe.")
    ins0 = float(np.nan_to_num(updated_df.loc[mask52, "Total Cost (USD)"].iloc[0], nan=0.0))
    updated_df.loc[mask52, "Total Cost (USD)"] = ins0 * change_factor

    # Recompute derived totals after change
    updated_df = update_high_level_costs(updated_df, power)
    return updated_df



def update_interest_cost(
    store,
    df: pd.DataFrame,
    final_construction_duration: float,
    interest_rate: float,
    startup_0: float,
    n_th: int,
    power: float
):
    Months, CDFs = store.get_spending_curve()
    dur = float(final_construction_duration)

    n_years = int(dur / 12)
    if n_years <= 0:
        annual_periods = np.array([dur - 1])
    else:
        annual_periods = np.linspace(12, 12 * n_years, n_years)
        if max(annual_periods) < int(dur) - 1:
            annual_periods = np.append(annual_periods, dur - 1)

    new_period = 103 * annual_periods / dur
    annual_cum_spend = np.interp(new_period, Months, CDFs)
    annual_spend = np.append(annual_cum_spend[0], np.diff(annual_cum_spend))

    tot_overnight_cost = float(
        df.loc[df["Title"].eq("Total Overnight Cost (Accounts 10 to 50)"), "Total Cost (USD)"].iloc[0]
    )

    annual_loan_add = annual_spend * tot_overnight_cost
    interest_exp = ((1 + interest_rate) ** ((dur - annual_periods) / 12)) * annual_loan_add - annual_loan_add
    tot_int_exp_construction = float(np.sum(interest_exp))

    if n_th == 1:
        startup = startup_0
    else:
        startup = max(7, startup_0 * (1 - 0.3) ** np.log2(n_th))
    int_exp_startup = (tot_int_exp_construction + tot_overnight_cost) * ((1 + interest_rate) ** (startup / 12)) \
                      - (tot_int_exp_construction + tot_overnight_cost)

    db = df.copy()
    int_curved = float(tot_int_exp_construction + int_exp_startup)
    setv(db, "62", "Total Cost (USD)", int_curved)

    db2 = update_high_level_costs(db, power)[COLS].copy()

    tot_cap_investment = float(
        db2.loc[db2["Title"].eq("Total Capital Investment Cost (All Accounts)"), "Total Cost (USD)"].iloc[0]
    )
    return db2, tot_overnight_cost, tot_cap_investment


def update_itc(
    df: pd.DataFrame,
    tot_overnight_cost: float,
    tot_cap_investment: float,
    n_th: int,
    ITC_0: float,
    n_ITC: int,
    reactor_power: float
):
    ITC = ITC_0 if n_th <= n_ITC else 0.0

    db = df.copy()

    itc_factor = ITC_reduction_factor(ITC)
    itc_reduced_occ = tot_overnight_cost * itc_factor
    occ_reduction = tot_overnight_cost - itc_reduced_occ

    db.loc[db["Title"].eq("Total Overnight Cost - ITC reduced"), "Total Cost (USD)"] = itc_reduced_occ
    db.loc[db["Title"].eq("Total Overnight Cost -ITC reduced (US$/kWe)"), "Total Cost (USD)"] = itc_reduced_occ / reactor_power
    db.loc[db["Title"].eq("Total Capital Investment Cost - ITC reduced"), "Total Cost (USD)"] = tot_cap_investment - occ_reduction

    levelized_NCI = float(
        db.loc[db["Title"].eq("Total Capital Investment Cost - ITC reduced"), "Total Cost (USD)"].iloc[0] / reactor_power
    )
    db.loc[db["Title"].eq("Total Capital Investment Cost - ITC reduced (US$/kWe)"), "Total Cost (USD)"] = levelized_NCI

    db2 = update_high_level_costs(db, reactor_power)[COLS].copy()
    return db2, itc_reduced_occ / reactor_power, levelized_NCI
