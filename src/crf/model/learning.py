# src/crf/model/learning.py
# Learning effects:
#  - learning_effect (cost learning by doing on direct accounts)
#  - act_cons_duration_plus_delay (supply chain delay model)
#  - duration_learning_effect (duration learning by doing)

import numpy as np
import pandas as pd

from ..utils.df_ops import getv, setv
from .core_accounts import update_high_level_costs

COLS = [
    "Account", "Title", "Total Cost (USD)",
    "Factory Equipment Cost", "Site Labor Hours",
    "Site Labor Cost", "Site Material Cost"
]

ACCT_DIRECT = [212, 213, "211 plus 214 to 219", 22, "232.1", 233, 24, 26]


def learning_effect(df: pd.DataFrame, n_th: int, standardization_0: float, power: float, reactor_type: str):
    # standardization cap for FOAK
    standardization = min(0.7, standardization_0) if n_th == 1 else standardization_0

    # fitted learning rates (same order as ACCT_DIRECT)
    # n_noak is the number of units after which the learning effect is fully realized, which is set to 8 based on expert elicitation. The learning rate is then calculated as 1-(1-std_learning_rate)^(1/log2(n_noak)).
    # std_learning_rate for HTGR:
    #     	    Fac	    Mat	    Lab Cost	Lab Hrs
    # 21		0.96	0.73	0.55	    0.55
    # 22		0.55	0.78	0.62	    0.62
    # 232.1	    0.40		    0.64	    0.64
    # 233		0.96	0.73	0.55	    0.55
    # 24		0.96	0.73	0.55	    0.55
    # 26		0.96	0.73	0.55	    0.55
    # std_learning_rate for SFR :
    #     	    Fac	    Mat	    Lab Cost	Lab Hrs
    # 21		0.96	0.73	0.55	    0.55
    # 22		0.49	0.73	0.55        0.55
    # 232.1	    0.47		    0.55        0.55        
    # 233		0.96	0.73	0.55	    0.55
    # 24		0.96	0.73	0.55	    0.55
    # 26		0.96	0.73	0.55        0.55

    # However, learning is not applied to the factory cost
    if reactor_type == "HTGR":
        mat_lr = np.array([
            0.099588665391, 0.099588665391, 0.099588665391, 0.080817992281,
            0.0, 0.099588665391, 0.099588665391, 0.099588665391
        ]) * standardization / 0.7

        lab_lr = np.array([
            0.180678729399, 0.180678729399, 0.180678729399, 0.146555539499,
            0.137148574884, 0.180678729399, 0.180678729399, 0.180678729399
        ]) * standardization / 0.7
    elif reactor_type == "SFR":
        mat_lr = np.array([
            0.099588665391, 0.099588665391, 0.099588665391, 0.099588665391,
            0.099588665391, 0.099588665391, 0.099588665391, 0.099588665391
        ]) * standardization / 0.7

        lab_lr = np.array([
            0.180678729399, 0.180678729399, 0.180678729399, 0.180678729399,
            0.180678729399, 0.180678729399, 0.180678729399, 0.180678729399
        ]) * standardization / 0.7
    else:
        raise ValueError(f"Unknown reactor type: {reactor_type}")
    db = df.copy()

    for idx, acct in enumerate(ACCT_DIRECT):
        mat_mult = (1 - float(mat_lr[idx])) ** np.log2(n_th)
        lab_mult = (1 - float(lab_lr[idx])) ** np.log2(n_th)

        setv(db, acct, "Site Material Cost", float(getv(df, acct, "Site Material Cost")) * mat_mult)
        setv(db, acct, "Site Labor Hours", float(getv(df, acct, "Site Labor Hours")) * lab_mult)
        setv(db, acct, "Site Labor Cost", float(getv(df, acct, "Site Labor Cost")) * lab_mult)

    return update_high_level_costs(db, power)[COLS].copy()


def act_cons_duration_plus_delay(
    reactor_type: str,
    n_th: int,
    Design_Maturity_0,
    proc_exp_0,
    N_proc,
    cons_duration_no_delay: float
):
    if n_th == 1:
        Design_Maturity = Design_Maturity_0
        proc_exp = proc_exp_0
    else:
        Design_Maturity = 2
        proc_exp = min(proc_exp_0 + (2 / N_proc) * (n_th - 1), 2)

    if reactor_type == "HTGR":
        task_length_multiplier = 100 / 64
        ref_construction_duration = 100
    elif reactor_type == "SFR":
        task_length_multiplier = 1.0
        ref_construction_duration = 64

    B_21 = 42.1 * task_length_multiplier
    B_22 = 60.2 * task_length_multiplier
    B_23 = 14.8 * task_length_multiplier
    B_24 = 3.6 * task_length_multiplier
    B_25 = 10.1 * task_length_multiplier
    B_26 = 43.9 * task_length_multiplier

    D = -6 * Design_Maturity - 3 * proc_exp + 18

    T_21 = B_21 + D
    T_22 = 0.09 * (B_21 + D) + B_22 + D
    T_23 = 0.24 * (B_21 + D) + B_23 + D
    T_24 = 0.24 * (B_21 + D) + 0.34 * (B_23 + D) + B_24 + D
    T_25 = 0.18 * (B_21 + D) + B_25 + D # NOTE: need to check  whether the delay should be applied to B_25
    T_26 = 0.21 * (B_21 + D) + B_26 + D

    T_end = max(T_21, T_22, T_23, T_24, T_25, T_26)
    supply_chain_delay = max(T_end - ref_construction_duration, 0)                   
    return float(cons_duration_no_delay) + float(supply_chain_delay)

def duration_learning_effect(reactor_type: str, 
                             n_th: int, 
                             standardization_0: float, 
                             actual_construction_duration_plus_delay: float):
    standardization = min(0.7, standardization_0) if n_th == 1 else standardization_0
    if reactor_type == "HTGR":
        fitted_LR_duration = 0.103719051 * standardization / 0.7
    elif reactor_type == "SFR":
        fitted_LR_duration = 0.15*standardization/0.7
    duration_multiplier = (1 - fitted_LR_duration) ** np.log2(n_th)
    return float(duration_multiplier) * float(actual_construction_duration_plus_delay)
