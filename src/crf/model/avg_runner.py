import numpy as np
from .pipeline import calculate_final_result
# Ignore runtime warning 

def run_avg_all_units(config: dict, inp: dict, store):
    """
    Runs n_th=1..num_orders and returns a CSV-friendly dict:
      OCC_i, TCI_i, duration_i plus summary metrics.
    """
    num_orders = int(inp["num_orders"])
    n_itc = int(inp["n_ITC"])

    OCC, NETOCC, TCI, NCI, DUR = [], [], [], [], []


    for n_th in range(1, num_orders + 1):
        _, occ, netocc, tci, nci, dur = calculate_final_result(config, inp, store, n_th=n_th)
        OCC.append(occ)
        TCI.append(tci)
        DUR.append(dur)
        if n_th <= n_itc:
            NETOCC.append(netocc)
            NCI.append(nci)


    OCC = np.array(OCC, dtype=float)
    NETOCC = np.array(NETOCC, dtype=float)
    TCI = np.array(TCI, dtype=float)
    NCI = np.array(NCI, dtype=float)
    DUR = np.array(DUR, dtype=float)

    # summaries
    occLastUnit = float(OCC[-1])
    TCILastUnit = float(TCI[-1])
    durationsLastUnit = float(DUR[-1])
    if n_itc > 0:
        avg_OCC = float(np.mean(NETOCC))
        avg_TCI = float(np.mean(NCI))
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
