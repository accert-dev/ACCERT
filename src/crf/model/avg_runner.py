import numpy as np
from .pipeline import calculate_final_result
# Ignore runtime warning 

def run_avg_all_units(config: dict, inp: dict, store, details=False):
    """
    Runs n_th=1..num_orders and returns a CSV-friendly dict:
      OCC_i, TCI_i, duration_i plus summary metrics.
    """
    num_orders = int(inp["num_orders"])
    n_itc = int(inp["n_ITC"])

    OCC, NETOCC, TCI, NCI, DUR, STAUP = [], [], [], [], [], []
    if details:
        # Stores the 10s, 20s, 30s, 50s and 60s, with 20s equipment, material, labor costs
        D10s, D20s, D30s, D50s, D60s = [], [], [], [], []
        D20_equip, D20_mat, D20_labor = [], [], []


    for n_th in range(1, num_orders + 1):
        final_df, occ, netocc, tci, nci, dur = calculate_final_result(config, inp, store, n_th=n_th)
        OCC.append(occ)
        TCI.append(tci)
        DUR.append(dur)
        STAUP.append(max(7, config["startup_0"] * (1 - 0.3) ** np.log2(n_th)))
        if n_th <= n_itc:
            NETOCC.append(netocc)
            NCI.append(nci)
        if details:
            D10s.append(float(final_df.loc[final_df["Title"].eq("10s - $/kWe"), "Total Cost (USD)"].iloc[0]))
            D20s.append(float(final_df.loc[final_df["Title"].eq("20s - $/kWe"), "Total Cost (USD)"].iloc[0]))
            D30s.append(float(final_df.loc[final_df["Title"].eq("30s - $/kWe"), "Total Cost (USD)"].iloc[0]))
            D50s.append(float(final_df.loc[final_df["Title"].eq("50s - $/kWe"), "Total Cost (USD)"].iloc[0]))
            D60s.append(float(final_df.loc[final_df["Title"].eq("60s - $/kWe"), "Total Cost (USD)"].iloc[0]))
            D20_equip.append(float(final_df.loc[final_df["Title"].eq("20s - $/kWe"), "Factory Equipment Cost"].iloc[0]))
            D20_mat.append(float(final_df.loc[final_df["Title"].eq("20s - $/kWe"), "Site Material Cost"].iloc[0]))
            D20_labor.append(float(final_df.loc[final_df["Title"].eq("20s - $/kWe"), "Site Labor Cost"].iloc[0])) 

    OCC = np.array(OCC, dtype=float)
    NETOCC = np.array(NETOCC, dtype=float)
    TCI = np.array(TCI, dtype=float)
    NCI = np.array(NCI, dtype=float)
    DUR = np.array(DUR, dtype=float)
    STAUP = np.array(STAUP, dtype=float)
    if details:
        D10s = np.array(D10s, dtype=float)
        D20s = np.array(D20s, dtype=float)
        D30s = np.array(D30s, dtype=float)
        D50s = np.array(D50s, dtype=float)
        D60s = np.array(D60s, dtype=float)
        D20_equip = np.array(D20_equip, dtype=float)
        D20_mat = np.array(D20_mat, dtype=float)
        D20_labor = np.array(D20_labor, dtype=float)

    # summaries
    occLastUnit = float(OCC[-1])
    TCILastUnit = float(TCI[-1])
    durationsLastUnit = float(DUR[-1])
    if n_itc > 0:
        # from 1st to n_ITC-th unit (inclusive) have ITC, so use NETOCC/NCI for avg; from (n_ITC+1)-th to last unit have no ITC, so use OCC/TCI for avg; 
        avg_OCC = float(np.mean(NETOCC))*(n_itc/num_orders) + float(np.mean(OCC[n_itc:]))*((num_orders-n_itc)/num_orders)
        avg_TCI = float(np.mean(NCI))*(n_itc/num_orders) + float(np.mean(TCI[n_itc:]))*((num_orders-n_itc)/num_orders)
    else:
        avg_OCC = float(np.mean(OCC))
        avg_TCI = float(np.mean(TCI))
    avg_duration = float(np.mean(DUR))


    final_startup_duration = max(7, config["startup_0"] * (1 - 0.3) ** np.log2(num_orders))
    cons_duration_cumulative_wz_startup = (
        (1 - config["staggering_ratio"]) * np.sum(DUR[:-1]) + DUR[-1] + final_startup_duration
    )

    # expand arrays to OCC_i / TCI_i / duration_i
    out = {}
    for i, v in enumerate(OCC):
        out[f"OCC_{i+1}"] = float(v)
    for i, v in enumerate(NETOCC):
        out[f"NETOCC_{i+1}"] = float(v)
    for i, v in enumerate(TCI):
        out[f"TCI_{i+1}"] = float(v)
    for i, v in enumerate(NCI):
        out[f"NCI_{i+1}"] = float(v)
    for i, v in enumerate(DUR):
        out[f"duration_{i+1}"] = float(v)
    for i, v in enumerate(STAUP):
        out[f"STAUP_{i+1}"] = float(v)
    if details:
        for i, v in enumerate(D10s):
            out[f"D10s_{i+1}"] = float(v)
        for i, v in enumerate(D20s):
            out[f"D20s_{i+1}"] = float(v)
        for i, v in enumerate(D30s):
            out[f"D30s_{i+1}"] = float(v)
        for i, v in enumerate(D50s):
            out[f"D50s_{i+1}"] = float(v)
        for i, v in enumerate(D60s):
            out[f"D60s_{i+1}"] = float(v)
        for i, v in enumerate(D20_equip):
            out[f"D20_equip_{i+1}"] = float(v)
        for i, v in enumerate(D20_mat):
            out[f"D20_mat_{i+1}"] = float(v)
        for i, v in enumerate(D20_labor):
            out[f"D20_labor_{i+1}"] = float(v)

    out.update({
        "cons_duration_cumulative_wz_startup": float(cons_duration_cumulative_wz_startup),
        "occLastUnit": occLastUnit,
        "TCILastUnit": TCILastUnit,
        "durationsLastUnit": durationsLastUnit,
        "avg_OCC": avg_OCC,
        "avg_TCI": avg_TCI,
        "avg_duration": avg_duration,
    })
    return out
