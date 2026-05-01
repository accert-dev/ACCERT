"""Visualization helpers for Cost Reduction Framework results."""

from __future__ import annotations

import os
import tempfile
import textwrap
from pathlib import Path
from typing import Dict, Iterable, Optional

os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


CAPITAL_COLORS = {
    "occ": "#1f77b4",
    "net_occ": "#7fb3d5",
    "tci": "#2ca02c",
    "nci": "#98df8a",
    "duration": "#9467bd",
    "startup": "#c5b0d5",
    "preconstruction": "#4c78a8",
    "equipment": "#72b7b2",
    "material": "#f58518",
    "labor": "#e45756",
    "indirect": "#54a24b",
    "supplementary": "#b279a2",
    "finance": "#ff9da6",
    "reduction": "#d62728",
}


def _ordered_suffixes(result: dict, prefix: str) -> list[int]:
    suffixes = []
    for key in result:
        if key.startswith(prefix):
            try:
                suffixes.append(int(key.split("_")[-1]))
            except ValueError:
                pass
    return sorted(suffixes)


def results_to_dataframe(result: dict) -> pd.DataFrame:
    """Convert a ``run_one_scenario`` result dictionary into chart-ready rows."""
    plant_numbers = _ordered_suffixes(result, "OCC_")
    if not plant_numbers:
        raise ValueError("result does not contain OCC_i values")

    rows = []
    foak_occ = float(result[f"OCC_{plant_numbers[0]}"])
    for plant_number in plant_numbers:
        occ = float(result[f"OCC_{plant_number}"])
        rows.append(
            {
                "Plant number": plant_number,
                "OCC": occ,
                "Net OCC": result.get(f"NETOCC_{plant_number}", np.nan),
                "TCI": result.get(f"TCI_{plant_number}", np.nan),
                "NCI": result.get(f"NCI_{plant_number}", np.nan),
                "Construction duration": result.get(f"duration_{plant_number}", np.nan),
                "Startup duration": result.get(f"STAUP_{plant_number}", np.nan),
                "Preconstruction costs": result.get(f"D10s_{plant_number}", np.nan),
                "Direct costs": result.get(f"D20s_{plant_number}", np.nan),
                "Direct costs: equipment": result.get(f"D20_equip_{plant_number}", np.nan),
                "Direct costs: material": result.get(f"D20_mat_{plant_number}", np.nan),
                "Direct costs: labor": result.get(f"D20_labor_{plant_number}", np.nan),
                "Indirect costs": result.get(f"D30s_{plant_number}", np.nan),
                "Supplementary costs": result.get(f"D50s_{plant_number}", np.nan),
                "Financing costs": result.get(f"D60s_{plant_number}", np.nan),
                "OCC reduction from FOAK": (foak_occ - occ) / foak_occ * 100.0,
            }
        )

    return pd.DataFrame(rows)


def occ_reduction_from_foak_to_noak(result: dict) -> float:
    """Return percent OCC reduction from the FOAK unit to the NOAK unit."""
    if "occ_reduction_from_FOAK_to_NOAK_percent" in result:
        return float(result["occ_reduction_from_FOAK_to_NOAK_percent"])

    noak_unit = int(result.get("Num_orders", max(_ordered_suffixes(result, "OCC_"))))
    foak_occ = float(result["OCC_1"])
    noak_occ = float(result[f"OCC_{noak_unit}"])
    return (foak_occ - noak_occ) / foak_occ * 100.0


def waterfall_to_dataframe(result: dict) -> pd.DataFrame:
    """Return the FOAK-to-NOAK OCC waterfall rows saved by the API."""
    rows = result.get("occ_waterfall")
    if not rows:
        raise ValueError("result does not contain occ_waterfall data")
    return pd.DataFrame(rows)


def plot_dashboard(result: dict, title: Optional[str] = None, figsize=(16, 12)):
    """Create a dashboard-style figure from Cost Reduction Framework output.

    The layout mirrors the capital-cost charts in the Excel dashboard: OCC,
    TCI, construction duration, cost breakdowns, and the percent OCC reduction
    from FOAK to NOAK.
    """
    df = results_to_dataframe(result)
    noak_unit = int(result.get("num_NOAK", result.get("Num_orders", df["Plant number"].max())))
    noak_unit = min(max(noak_unit, int(df["Plant number"].min())), int(df["Plant number"].max()))
    noak_reduction = occ_reduction_from_foak_to_noak(result)

    fig, axes = plt.subplots(3, 2, figsize=figsize, constrained_layout=True)
    fig.suptitle(title or "Cost Reduction Framework Dashboard", fontsize=16, fontweight="bold")

    x = df["Plant number"]

    ax = axes[0, 0]
    ax.bar(x - 0.18, df["OCC"], width=0.36, label="Overnight Capital Cost (OCC)", color=CAPITAL_COLORS["occ"])
    if df["Net OCC"].notna().any():
        ax.bar(x + 0.18, df["Net OCC"], width=0.36, label="Net OCC (after ITC)", color=CAPITAL_COLORS["net_occ"])
    ax.set_title("Overnight Capital Cost")
    ax.set_xlabel("Plant number")
    ax.set_ylabel("$/kWe")
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    ax.bar(x - 0.18, df["TCI"], width=0.36, label="Total Capital Investment (TCI)", color=CAPITAL_COLORS["tci"])
    if df["NCI"].notna().any():
        ax.bar(x + 0.18, df["NCI"], width=0.36, label="Net Capital Investment (NCI)", color=CAPITAL_COLORS["nci"])
    ax.set_title("Capital Investment")
    ax.set_xlabel("Plant number")
    ax.set_ylabel("$/kWe")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    ax.bar(x, df["Construction duration"], label="Construction", color=CAPITAL_COLORS["duration"])
    if df["Startup duration"].notna().any():
        ax.bar(
            x,
            df["Startup duration"],
            bottom=df["Construction duration"],
            label="Startup",
            color=CAPITAL_COLORS["startup"],
        )
    ax.set_title("Total Construction Duration")
    ax.set_xlabel("Plant number")
    ax.set_ylabel("Months")
    ax.legend(fontsize=8)

    ax = axes[1, 1]
    breakdown = [
        ("Preconstruction costs", "preconstruction"),
        ("Direct costs", "equipment"),
        ("Indirect costs", "indirect"),
        ("Supplementary costs", "supplementary"),
        ("Financing costs", "finance"),
    ]
    _stacked_bars(ax, x, df, breakdown)
    ax.set_title("Capital Cost Breakdown")
    ax.set_xlabel("Plant number")
    ax.set_ylabel("$/kWe")
    ax.legend(fontsize=8)

    ax = axes[2, 0]
    direct_breakdown = [
        ("Direct costs: equipment", "equipment"),
        ("Direct costs: material", "material"),
        ("Direct costs: labor", "labor"),
        ("Indirect costs", "indirect"),
        ("Supplementary costs", "supplementary"),
    ]
    _stacked_bars(ax, x, df, direct_breakdown)
    ax.set_title("Detailed Cost Components")
    ax.set_xlabel("Plant number")
    ax.set_ylabel("$/kWe")
    ax.legend(fontsize=8)

    ax = axes[2, 1]
    _plot_occ_waterfall(ax, result, noak_reduction)

    for ax in axes.flat:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelrotation=0)

    return fig


def save_dashboard(result: dict, out_path: str, title: Optional[str] = None, dpi: int = 180) -> str:
    """Save the dashboard figure and return the output path."""
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plot_dashboard(result, title=title)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def save_figures(result: dict, output_dir: str, prefix: str = "cost_reduction_framework") -> Dict[str, str]:
    """Save the dashboard and individual dashboard figures as PNG files."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    saved = {
        "dashboard": save_dashboard(result, out_dir / f"{prefix}_dashboard.png"),
    }
    return saved


def _plot_occ_waterfall(ax, result: dict, noak_reduction: float) -> None:
    waterfall = waterfall_to_dataframe(result)
    labels = [_wrap_label(label) for label in waterfall["label"].tolist()]
    x_pos = np.arange(len(waterfall))

    colors = []
    bottoms = []
    heights = []
    previous = 0.0
    for _, row in waterfall.iterrows():
        if row["kind"] == "total":
            bottoms.append(0.0)
            heights.append(float(row["cumulative_occ"]))
            colors.append("#4c78a8")
            previous = float(row["cumulative_occ"])
        else:
            change = float(row["absolute_change"])
            if change >= 0:
                bottoms.append(previous)
                heights.append(change)
                colors.append("#f58518")
            else:
                bottoms.append(previous + change)
                heights.append(abs(change))
                colors.append("#54a24b")
            previous += change

    ax.bar(x_pos, heights, bottom=bottoms, color=colors, width=0.72)
    for idx in range(len(waterfall) - 1):
        y = float(waterfall.iloc[idx]["cumulative_occ"])
        ax.plot([idx + 0.36, idx + 1 - 0.36], [y, y], color="#777777", linewidth=0.8)

    ax.set_title("% OCC Reduction from FOAK to NOAK")
    ax.set_ylabel("OCC ($/kWe)")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=0, ha="center", fontsize=7)
    ax.grid(True, axis="y", alpha=0.25)
    ax.text(
        0.98,
        0.95,
        f"FOAK to NOAK reduction: {noak_reduction:.1f}%",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        bbox={"facecolor": "white", "edgecolor": "#cccccc", "alpha": 0.9},
    )


def _stacked_bars(ax, x: Iterable[int], df: pd.DataFrame, columns: list[tuple[str, str]]) -> None:
    bottom = np.zeros(len(df))
    for label, color_key in columns:
        values = df[label].astype(float)
        if not values.notna().any():
            continue
        clean_values = values.fillna(0.0).to_numpy()
        ax.bar(x, clean_values, bottom=bottom, label=label, color=CAPITAL_COLORS[color_key])
        bottom += clean_values


def _wrap_label(label: str, width: int = 13) -> str:
    compact = " ".join(str(label).split())
    return "\n".join(textwrap.wrap(compact, width=width))
