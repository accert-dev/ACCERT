import csv
import numpy as np

from .io.excel_inputs import InputStore
from .io.excel_levers import read_levers_sheet
from .sampling.sampler import sample_levers
from .sampling.lever_schema import (
    STATIC_KEYS,
    attach_internal_ids,
    sample_column_to_levers,
    static_row_from_levers,
)
from .sampling.postprocess import apply_itc_rounding
from .model.avg_runner import run_avg_all_units
from .utils.serialize import write_csv_row, stream_pickle_dump


def normalize_levers(levers: dict) -> dict:
    """Convert raw lever dict to model-ready normalized values."""
    def label01(x, zero_label, one_label):
        if x == 0: return zero_label
        if x == 1: return one_label
        return x

    return {
      "num_orders": int(levers["num_orders"]),
      "ITC_0": float(levers["itc_percent"]) / 100.0,
      "n_ITC": levers["n_itc"],
      "interest_rate_0": float(levers["interest_percent"]) / 100.0,
      "design_completion_0": float(levers["design_completion_percent"]) / 100.0,
      "Design_Maturity_0": levers["design_maturity"],
      "proc_exp_0": levers["proc_exp"],
      "N_proc": levers["N_proc"],
      "ce_exp_0": levers["ce_exp"],
      "N_cons": levers["N_cons"],
      "ae_exp_0": levers["ae_exp"],
      "N_AE": levers["N_AE"],
      "standardization_0": float(levers["standardization_percent"]) / 100.0,
      "mod_0": label01(levers["modularity_code"], "stick_built", "modularized"),
      "BOP_grade_0": label01(levers["bop_grade_code"], "nuclear", "non_nuclear"),
      "RB_grade_0": label01(levers["rb_grade_code"], "nuclear", "non_nuclear"),
      "num_NOAK": int(levers["num_NOAK"]) if "num_NOAK" in levers else int(levers["num_orders"]),
    }


def run_one_scenario(config: dict, levers: dict) -> dict:
    store = InputStore(config.get("data_dir"))
    levers = apply_itc_rounding(levers)
    inp = normalize_levers(levers)

    result = run_avg_all_units(config=config, inp=inp, store=store, details=True)
    static_vals = static_row_from_levers(levers)
    return {**static_vals, **result}


def run_sampling_from_excel(
    config: dict,
    levers_xlsx: str,
    n_samples: int,
    out_csv: str,
    out_pkl: str,
    seed: int | None = None
):
    levers_df = read_levers_sheet(levers_xlsx, sheet_name="Levers")
    levers_df = attach_internal_ids(levers_df)   

    samples = sample_levers(n_samples, levers_df, seed=seed)  # shape (n_levers, n_samples)

    # headers: build from max num_orders in sampled set
    max_orders = int(np.max(samples[0, :]))

    headers_wo_itc = (
    STATIC_KEYS
    + [f"OCC_{i}" for i in range(max_orders)]
    + [f"TCI_{i}" for i in range(max_orders)]
    + [f"duration_{i}" for i in range(max_orders)]
    + [
        "cons_duration_cumulative_wz_startup",
        "occLastUnit", "TCILastUnit", "durationsLastUnit",
        "avg_OCC", "avg_TCI", "avg_duration",
    ]
    )
    headers_w_itc = (
    STATIC_KEYS
    + [f"OCC_{i}" for i in range(max_orders)]
    + [f"NETOCC_{i}" for i in range(max_orders)]
    + [f"TCI_{i}" for i in range(max_orders)]
    + [f"NCI_{i}" for i in range(max_orders)]
    + [f"duration_{i}" for i in range(max_orders)]
    + [
        "cons_duration_cumulative_wz_startup",
        "occLastUnit", "TCILastUnit", "durationsLastUnit",
        "avg_OCC", "avg_TCI", "avg_duration",
    ]
    )

    with open(out_csv, "w", newline="", encoding="utf-8") as csv_f, open(out_pkl, "wb") as pkl_f:
        writer = csv.DictWriter(csv_f, fieldnames=headers)
        writer.writeheader()
        for i in range(n_samples):
            levers_raw = sample_column_to_levers(samples, levers_df, i)
            row = run_one_scenario(config, levers_raw)
            n_itc = int(levers_raw["n_itc"])
            if n_itc > 0:
                headers = headers_w_itc
            else:
                headers = headers_wo_itc
            write_csv_row(writer, row, headers)
            stream_pickle_dump(row, pkl_f)

    levers = apply_itc_rounding(levers)
    inp = normalize_levers(levers)

    result = run_avg_all_units(config=config, inp=inp, store=store, details=False)
    static_vals = static_row_from_levers(levers)
    return {**static_vals, **result}
