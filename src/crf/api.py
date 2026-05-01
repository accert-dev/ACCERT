import csv
from typing import Optional

import numpy as np
import pandas as pd

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
from .model.pipeline import calculate_final_result
from .model.schedule import effective_staggering_ratio
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
    out = {**static_vals, **result}
    out["reactor_type"] = config.get("reactor_type", "")
    out["staggering_ratio"] = effective_staggering_ratio(config)
    out["occ_waterfall"] = calculate_occ_waterfall(config, levers)
    return out


def calculate_occ_waterfall(config: dict, levers: dict) -> list[dict]:
    """Calculate FOAK-to-NOAK OCC waterfall contributions by model stage."""
    store = InputStore(config.get("data_dir"))
    normalized = normalize_levers(levers)
    noak_unit = min(max(int(normalized.get("num_NOAK", normalized["num_orders"])), 1), int(normalized["num_orders"]))

    foak_trace = {}
    noak_trace = {}
    calculate_final_result(config=config, inp=normalized, store=store, n_th=1, trace=foak_trace)
    calculate_final_result(config=config, inp=normalized, store=store, n_th=noak_unit, trace=noak_trace)

    foak_occ = float(foak_trace["final_occ"])
    noak_occ = float(noak_trace["final_occ"])

    labels = [
        "Bulk-ordering",
        "Elimination of rework",
        "Supplychain efficiency",
        "Labor productivity",
        "Experience and cross-site standardization",
        "Modular Construction",
        "Commercial BOP",
        "Non safety-related Reactor Building",
    ]

    contributions = {
        "Bulk-ordering": _trace_delta(noak_trace, foak_trace, "Bulk-ordering"),
        "Elimination of rework": _trace_delta(noak_trace, foak_trace, "Elimination of rework"),
        "Supplychain efficiency": _trace_delta(noak_trace, foak_trace, "Supplychain efficiency"),
        "Labor productivity": _trace_delta(noak_trace, foak_trace, "Labor productivity"),
        "Experience and cross-site standardization": _trace_delta(
            noak_trace, foak_trace, "Experience and cross-site standardization"
        ),
        "Modular Construction": _trace_delta(noak_trace, foak_trace, "Modular Construction"),
        "Commercial BOP": _trace_delta(noak_trace, foak_trace, "Commercial BOP"),
        "Non safety-related Reactor Building": _trace_delta(
            noak_trace, foak_trace, "Non safety-related Reactor Building"
        ),
    }
    _allocate_waterfall_residual(contributions, (noak_occ - foak_occ) - sum(contributions.values()))

    rows = [
        {
            "label": "FOAK \n(no firm orders)",
            "absolute_change": foak_occ,
            "cumulative_occ": foak_occ,
            "kind": "total",
        }
    ]
    cumulative = foak_occ
    for label in labels:
        change = float(contributions[label])
        cumulative += change
        rows.append(
            {
                "label": label,
                "absolute_change": change,
                "cumulative_occ": cumulative,
                "kind": "change",
            }
        )
    rows.append(
        {
            "label": "NOAK \n(firm orders)",
            "absolute_change": noak_occ,
            "cumulative_occ": noak_occ,
            "kind": "total",
        }
    )
    return rows


def _trace_delta(noak_trace: dict, foak_trace: dict, key: str) -> float:
    return float(noak_trace.get(key, 0.0)) - float(foak_trace.get(key, 0.0))


def _allocate_waterfall_residual(contributions: dict, residual: float) -> None:
    """Allocate downstream model effects across levers that reduce OCC.

    Some model terms, especially indirect and supplementary costs, are
    recalculated after direct-cost levers have changed the cost base. The
    spreadsheet waterfall distributes those downstream effects across the
    levers instead of assigning them to one lever. Do the same here so the
    waterfall reconciles without overstating experience/standardization.
    """
    if abs(residual) < 1e-9:
        return

    if residual < 0:
        keys = [
            key for key, value in contributions.items()
            if value < 0 and key != "Supplychain efficiency"
        ]
    else:
        keys = [
            key for key, value in contributions.items()
            if value > 0 and key != "Supplychain efficiency"
        ]

    weight_total = sum(abs(contributions[key]) for key in keys)
    if weight_total == 0:
        contributions["Experience and cross-site standardization"] += residual
        return

    for key in keys:
        contributions[key] += residual * abs(contributions[key]) / weight_total

def run_sampling_from_excel(
    config: dict,
    levers_xlsx: str,
    n_samples: int,
    out_csv: str,
    out_pkl: str,
    seed: Optional[int] = None
):
    levers_df = read_levers_sheet(levers_xlsx, sheet_name="Levers")
    levers_df = attach_internal_ids(levers_df)   

    samples = sample_levers(n_samples, levers_df, seed=seed)  # shape (n_levers, n_samples)

    # headers: build from max num_orders in sampled set
    max_orders = int(np.max(samples[0, :]))
    has_itc = bool(np.any(samples[2, :] > 0))

    headers_wo_itc = (
    STATIC_KEYS
    + [f"OCC_{i}" for i in range(1, max_orders + 1)]
    + [f"TCI_{i}" for i in range(1, max_orders + 1)]
    + [f"duration_{i}" for i in range(1, max_orders + 1)]
    + [
        "cons_duration_cumulative_wz_startup",
        "occLastUnit", "occNOAKUnit", "occ_reduction_from_FOAK_to_NOAK_percent",
        "TCILastUnit", "durationsLastUnit",
        "avg_OCC", "avg_TCI", "avg_duration",
    ]
    )
    headers_w_itc = (
    STATIC_KEYS
    + [f"OCC_{i}" for i in range(1, max_orders + 1)]
    + [f"NETOCC_{i}" for i in range(1, max_orders + 1)]
    + [f"TCI_{i}" for i in range(1, max_orders + 1)]
    + [f"NCI_{i}" for i in range(1, max_orders + 1)]
    + [f"duration_{i}" for i in range(1, max_orders + 1)]
    + [
        "cons_duration_cumulative_wz_startup",
        "occLastUnit", "occNOAKUnit", "occ_reduction_from_FOAK_to_NOAK_percent",
        "TCILastUnit", "durationsLastUnit",
        "avg_OCC", "avg_TCI", "avg_duration",
    ]
    )

    headers = headers_w_itc if has_itc else headers_wo_itc

    with open(out_csv, "w", newline="", encoding="utf-8") as csv_f, open(out_pkl, "wb") as pkl_f:
        writer = csv.DictWriter(csv_f, fieldnames=headers)
        writer.writeheader()
        for i in range(n_samples):
            levers_raw = sample_column_to_levers(samples, levers_df, i)
            row = run_one_scenario(config, levers_raw)
            write_csv_row(writer, row, headers)
            stream_pickle_dump(row, pkl_f)

def print_scenario_result(result: dict):
    print("Results by plant number:\n")
    max_orders = max([int(k.split("_")[1]) for k in result.keys() if k.startswith("OCC_")])
    results_df = pd.DataFrame({"Plant_number": list(range(1, max_orders+1))})
    for k, v in result.items():
        if k.startswith("OCC_"):
            results_df[f"OCC"] = results_df["Plant_number"].apply(lambda x: result.get(f"OCC_{x}", None))
        elif k.startswith("NETOCC_"):
            results_df[f"NETOCC"] = results_df["Plant_number"].apply(lambda x: result.get(f"NETOCC_{x}", None))
        elif k.startswith("TCI_"):
            results_df[f"TCI"] = results_df["Plant_number"].apply(lambda x: result.get(f"TCI_{x}", None))
        elif k.startswith("NCI_"):
            results_df[f"NCI"] = results_df["Plant_number"].apply(lambda x: result.get(f"NCI_{x}", None))
        elif k.startswith("duration_"):
            results_df[f"duration"] = results_df["Plant_number"].apply(lambda x: result.get(f"duration_{x}", None))
        elif k.startswith("STAUP_"):
            results_df[f"STAUP"] = results_df["Plant_number"].apply(lambda x: result.get(f"STAUP_{x}", None))
        elif k.startswith("D10s_"):
            results_df[f"D10s"] = results_df["Plant_number"].apply(lambda x: result.get(f"D10s_{x}", None))
        elif k.startswith("D20s_"):
            results_df[f"D20s"] = results_df["Plant_number"].apply(lambda x: result.get(f"D20s_{x}", None))
        elif k.startswith("D30s_"): 
            results_df[f"D30s"] = results_df["Plant_number"].apply(lambda x: result.get(f"D30s_{x}", None))
        elif k.startswith("D50s_"):
            results_df[f"D50s"] = results_df["Plant_number"].apply(lambda x: result.get(f"D50s_{x}", None))
        elif k.startswith("D60s_"):
            results_df[f"D60s"] = results_df["Plant_number"].apply(lambda x: result.get(f"D60s_{x}", None))
        elif k.startswith("D20_equip_"):
            results_df[f"D20_equip"] = results_df["Plant_number"].apply(lambda x: result.get(f"D20_equip_{x}", None))
        elif k.startswith("D20_mat_"):
            results_df[f"D20_mat"] = results_df["Plant_number"].apply(lambda x: result.get(f"D20_mat_{x}", None))
        elif k.startswith("D20_labor_"):
            results_df[f"D20_labor"] = results_df["Plant_number"].apply(lambda x: result.get(f"D20_labor_{x}", None)) 
        
    print(results_df.round(2).fillna("").to_string(index=False))

    summary_metrics = [
        "cons_duration_cumulative_wz_startup",
        "occLastUnit",
        "occNOAKUnit",
        "occ_reduction_from_FOAK_to_NOAK_percent",
        "TCILastUnit",
        "durationsLastUnit",
        "avg_OCC",
        "avg_TCI",
        "avg_duration",
    ]
    print("\nSummary metrics:\n")
    for metric in summary_metrics:
        print(f"{metric}: {result[metric]:.2f}")
