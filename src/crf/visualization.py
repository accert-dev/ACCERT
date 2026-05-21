"""Visualization helpers for Cost Reduction Framework results."""

from __future__ import annotations

import os
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Dict, Iterable, Optional

os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())

import matplotlib

if "ipykernel" not in sys.modules:
    matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .model.schedule import build_schedule_timeline


CAPITAL_COLORS = {
    "occ": "#1f77b4",
    "net_occ": "#7fb3d5",
    "tci": "#2ca02c",
    "nci": "#98df8a",
    "duration": "#ff8c2a",
    "startup": "#8b63a9",
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
    foak_tci = float(result[f"TCI_{plant_numbers[0]}"]) if f"TCI_{plant_numbers[0]}" in result else np.nan
    for plant_number in plant_numbers:
        occ = float(result[f"OCC_{plant_number}"])
        tci = result.get(f"TCI_{plant_number}", np.nan)
        rows.append(
            {
                "Plant number": plant_number,
                "OCC": occ,
                "Net OCC": result.get(f"NETOCC_{plant_number}", np.nan),
                "TCI": tci,
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
                "TCI reduction from FOAK": (foak_tci - float(tci)) / foak_tci * 100.0 if not pd.isna(foak_tci) and not pd.isna(tci) else np.nan,
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


def tci_reduction_from_foak_to_noak(result: dict) -> float:
    """Return percent TCI reduction from the FOAK unit to the NOAK unit."""
    noak_unit = int(result.get("num_NOAK", max(_ordered_suffixes(result, "TCI_"))))
    foak_tci = float(result["TCI_1"])
    noak_tci = float(result[f"TCI_{noak_unit}"])
    return (foak_tci - noak_tci) / foak_tci * 100.0


def waterfall_to_dataframe(result: dict) -> pd.DataFrame:
    """Return the FOAK-to-NOAK TCI waterfall rows saved by the API."""
    rows = result.get("tci_waterfall") or result.get("occ_waterfall")
    if not rows:
        raise ValueError("result does not contain waterfall data")
    return pd.DataFrame(rows)


def levers_to_dataframe(result: dict) -> pd.DataFrame:
    """Return the plant-by-plant lever table shown in the dashboard."""
    num_orders = int(result["Num_orders"])
    n_itc = int(result["n_ITC"])
    itc = float(result["ITC"])
    interest = float(result["interest rate"])
    design_completion = float(result["Design completion"])
    design_maturity = float(result["Design_Maturity_0"])
    supply_chain = float(result["supply chain exp_0"])
    n_supply_chain = float(result["N supply chain"])
    construction = float(result["Const Proficiency"])
    n_construction = float(result["N const prof"])
    ae = float(result["AE"])
    n_ae = float(result["N AE prof"])
    standardization = float(result["standardization"])

    def ramp(start: float, n_best: float, plant: int) -> float:
        if plant == 1:
            return start
        return min(start + (2.0 / n_best) * (plant - 1), 2.0)

    rows = []
    for plant in range(1, num_orders + 1):
        rows.append(
            {
                "N": plant,
                "Interest Rate": f"{interest:.0f}%",
                "Design Completion": f"{design_completion if plant == 1 else 100:.0f}%",
                "Design Maturity (0-2)": f"{design_maturity if plant == 1 else 2:.0f}",
                "Supplychain Proficiency (0-2)": f"{ramp(supply_chain, n_supply_chain, plant):.2f}",
                "A/E Proficiency (0-2)": f"{ramp(ae, n_ae, plant):.2f}",
                "Construction Proficiency (0-2)": f"{ramp(construction, n_construction, plant):.2f}",
                "Cross Site Standardization": "" if plant == 1 else f"{standardization:.0f}%",
                "Modular Civil Construction": _bool_label(result["modularity"]),
                "Commercial BOP": _bool_label(result["BOP commercial"]),
                "Non-Safety-Related RB": _bool_label(result["RB Safety Related"]),
                "ITC Amount": f"{itc:.0f}%" if plant <= n_itc else "0%",
            }
        )
    return pd.DataFrame(rows)


def plot_dashboard(
    result: dict,
    title: Optional[str] = None,
    figsize: Optional[tuple[float, float]] = None,
    show_levers: bool = True,
):
    """Create a dashboard-style figure from Cost Reduction Framework output.

    The layout mirrors the capital-cost charts in the Excel dashboard: capital
    costs, construction duration, cost breakdowns, build timeline, and the
    percent TCI reduction from FOAK to NOAK.
    """
    df = results_to_dataframe(result)
    noak_unit = int(result.get("num_NOAK", result.get("Num_orders", df["Plant number"].max())))
    noak_unit = min(max(noak_unit, int(df["Plant number"].min())), int(df["Plant number"].max()))
    noak_reduction = tci_reduction_from_foak_to_noak(result)

    if figsize is None:
        figsize = (24, 18) if show_levers else (22, 13)

    fig = plt.figure(figsize=figsize, constrained_layout=True)
    if show_levers:
        gs = fig.add_gridspec(4, 2, height_ratios=[1.35, 1, 1, 1])
        lever_ax = fig.add_subplot(gs[0, :])
        axes = np.array(
            [
                [fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])],
                [fig.add_subplot(gs[2, 0]), fig.add_subplot(gs[2, 1])],
                [fig.add_subplot(gs[3, 0]), fig.add_subplot(gs[3, 1])],
            ]
        )
        _plot_lever_table(lever_ax, result)
    else:
        gs = fig.add_gridspec(3, 2)
        axes = np.array(
            [
                [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])],
                [fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])],
                [fig.add_subplot(gs[2, 0]), fig.add_subplot(gs[2, 1])],
            ]
        )
    fig.suptitle(title or "Cost Reduction Framework Dashboard", fontsize=18, fontweight="bold")

    x = df["Plant number"]

    ax = axes[0, 0]
    ax.bar(x - 0.18, df["TCI"], width=0.36, label="10-60 - Total Capital Investment (TCI)", color=CAPITAL_COLORS["tci"])
    ax.bar(x + 0.18, df["OCC"], width=0.36, label="10-50 - Overnight Capital Cost (OCC)", color=CAPITAL_COLORS["occ"])
    if df["Net OCC"].notna().any():
        ax.plot(x, df["Net OCC"], marker="o", linestyle="--", linewidth=1.2, label="Net OCC (after ITC)", color=CAPITAL_COLORS["net_occ"])
    if df["NCI"].notna().any():
        ax.plot(x, df["NCI"], marker="o", linestyle="--", linewidth=1.2, label="Net Capital Investment (NCI)", color=CAPITAL_COLORS["nci"])
    ax.set_title("Capital Cost: OCC and TCI")
    ax.set_xlabel("Plant number")
    ax.set_ylabel("$/kWe")
    ax.legend(fontsize=10)

    ax = axes[0, 1]
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
    ax.legend(fontsize=10)

    ax = axes[1, 0]
    breakdown = [
        ("Preconstruction costs", "preconstruction", "10 - Preconstruction"),
        ("Direct costs", "equipment", "20 - Direct"),
        ("Indirect costs", "indirect", "30 - Indirect"),
        ("Supplementary costs", "supplementary", "50 - Supplementary"),
        ("Financing costs", "finance", "60 - Financing"),
    ]
    _stacked_bars(ax, x, df, breakdown)
    ax.set_title("10-60 - TCI Breakdown")
    ax.set_xlabel("Plant number")
    ax.set_ylabel("$/kWe")
    ax.legend(fontsize=10)

    ax = axes[1, 1]
    _plot_build_timeline(ax, result, df)

    ax = axes[2, 0]
    direct_breakdown = [
        ("Direct costs: equipment", "equipment", "20 - Direct: Equipment"),
        ("Direct costs: material", "material", "20 - Direct: Material"),
        ("Direct costs: labor", "labor", "20 - Direct: Labor"),
        ("Indirect costs", "indirect", "30 - Indirect"),
        ("Supplementary costs", "supplementary", "50 - Supplementary"),
    ]
    _stacked_bars(ax, x, df, direct_breakdown)
    ax.set_title("10-50 - OCC Components")
    ax.set_xlabel("Plant number")
    ax.set_ylabel("$/kWe")
    ax.legend(fontsize=10)

    ax = axes[2, 1]
    _plot_tci_waterfall(ax, result, noak_reduction)

    for ax in axes.flat:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelrotation=0)

    return fig


def save_dashboard(
    result: dict,
    out_path: str,
    title: Optional[str] = None,
    dpi: int = 150,
    show_levers: bool = True,
) -> str:
    """Save the dashboard figure and return the output path."""
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plot_dashboard(result, title=title, show_levers=show_levers)
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


def _plot_lever_table(ax, result: dict) -> None:
    ax.axis("off")
    df = levers_to_dataframe(result)
    display_df = df.copy()
    display_df.columns = [
        "N",
        "Interest\nRate",
        "Design\nCompletion",
        "Design\nMaturity\n(0-2)",
        "Supplychain\nProficiency\n(0-2)",
        "A/E\nProficiency\n(0-2)",
        "Construction\nProficiency\n(0-2)",
        "Cross Site\nStandardization",
        "Modular Civil\nConstruction",
        "Commercial\nBOP",
        "Non-Safety-\nRelated RB",
        "ITC Amount",
    ]

    table = ax.table(
        cellText=display_df.values,
        colLabels=display_df.columns,
        loc="center",
        cellLoc="center",
        colLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1.0, 1.25)

    header_color = "#17647f"
    highlight = "#bfe7f3"
    grid = "#d2d2d2"
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(grid)
        if row == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(color="white", weight="bold")
            cell.set_linewidth(1.0)
        else:
            cell.set_text_props(color="#155d78" if row <= 2 else "#8f8f8f", weight="bold")
            cell.set_facecolor(highlight if row <= 2 else "white")
            cell.set_linewidth(0.7)
            if col == 7 and row == 1:
                cell.set_facecolor("black")
                cell.get_text().set_text("")

    ax.set_title(
        f"Lever Inputs: {int(result['Num_orders'])} firm orders, "
        f"{int(result['n_ITC'])} reactors claiming ITC, ITC {float(result['ITC']):.0f}%",
        loc="left",
        fontsize=13,
        fontweight="bold",
        color=header_color,
        pad=6,
    )


def _plot_build_timeline(ax, result: dict, df: pd.DataFrame) -> None:
    durations = df["Construction duration"].astype(float).to_numpy()
    startup = df["Startup duration"].astype(float).fillna(0.0).to_numpy()
    plants = df["Plant number"].astype(int).to_numpy()
    schedule_config = {
        "staggering_ratio": result.get("staggering_ratio", result.get("Staggering ratio", 0.75)),
        "reactor_type": result.get("reactor_type", ""),
    }
    timeline = build_schedule_timeline(schedule_config, plants, durations, startup)
    timeline_df = pd.DataFrame(timeline)

    start_years = timeline_df["construction_start_month"].to_numpy() / 12.0
    duration_years = timeline_df["construction_duration_months"].to_numpy() / 12.0
    startup_years = timeline_df["startup_duration_months"].to_numpy() / 12.0

    ax.barh(
        plants,
        duration_years,
        left=start_years,
        height=0.64,
        color=CAPITAL_COLORS["duration"],
        edgecolor="black",
        linewidth=0.8,
        label="Construction",
    )
    ax.barh(
        plants,
        startup_years,
        left=start_years + duration_years,
        height=0.64,
        color=CAPITAL_COLORS["startup"],
        edgecolor="black",
        linewidth=0.8,
        label="Startup",
    )

    max_year = float(np.nanmax(start_years + duration_years + startup_years))
    ax.set_title("Sequential Construction Timeline")
    ax.set_xlabel("Time (Years)")
    ax.set_ylabel("Reactor Number")
    ax.set_yticks(plants)
    ax.set_ylim(plants.max() + 0.7, plants.min() - 0.7)
    ax.set_xlim(0, max_year * 1.05)
    ax.set_xticks(np.arange(0, np.ceil(max_year) + 1, 1))
    ax.grid(True, axis="x", alpha=0.35)
    ax.legend(loc="upper right", ncol=2, fontsize=8)


def _plot_tci_waterfall(ax, result: dict, noak_reduction: float) -> None:
    waterfall = waterfall_to_dataframe(result)
    labels = [_wrap_label(label) for label in waterfall["label"].tolist()]
    x_pos = np.arange(len(waterfall))
    cumulative_col = "cumulative_tci" if "cumulative_tci" in waterfall.columns else "cumulative_occ"
    metric = "TCI" if cumulative_col == "cumulative_tci" else "OCC"
    foak_value = float(waterfall.iloc[0][cumulative_col])

    colors = []
    bottoms = []
    heights = []
    pct_labels = []
    for _, row in waterfall.iterrows():
        if row["kind"] == "total":
            bottoms.append(0.0)
            total = float(row[cumulative_col])
            heights.append(total)
            if row.name == 0:
                pct_labels.append("100%")
            else:
                pct_labels.append(f"{noak_reduction:.1f}% lower")
            colors.append("#4c78a8")
        else:
            current = float(row[cumulative_col])
            change = float(row["absolute_change"])
            previous = current - change
            change_pct = change / foak_value * 100.0 if foak_value else 0.0
            if change >= 0:
                bottoms.append(previous)
                heights.append(change)
                colors.append("#f58518")
            else:
                bottoms.append(current)
                heights.append(abs(change))
                colors.append("#54a24b")
            pct_labels.append(f"{change_pct:+.1f}%")

    ax.bar(x_pos, heights, bottom=bottoms, color=colors, width=0.72)
    for idx in range(len(waterfall) - 1):
        y = float(waterfall.iloc[idx][cumulative_col])
        ax.plot([idx + 0.36, idx + 1 - 0.36], [y, y], color="#777777", linewidth=0.8)

    y_span = max([bottom + height for bottom, height in zip(bottoms, heights)] + [foak_value]) * 0.08
    for idx, (bottom, height, label) in enumerate(zip(bottoms, heights, pct_labels)):
        if not height:
            continue
        y = bottom + height / 2
        va = "center"
        color = "white"
        if height < y_span * 0.55:
            y = bottom + height + y_span * 0.12
            va = "bottom"
            color = "#1f2933"
        ax.text(
            idx,
            y,
            label,
            ha="center",
            va=va,
            fontsize=9,
            fontweight="bold",
            color=color,
            rotation=90 if len(label) > 7 else 0,
        )

    ax.set_title(f"% {metric} Reduction from FOAK to NOAK")
    ax.set_ylabel(f"{metric} ($/kWe)")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=0, ha="center", fontsize=9)
    ax.grid(True, axis="y", alpha=0.25)
    ax.set_ylim(0, max([bottom + height for bottom, height in zip(bottoms, heights)] + [foak_value]) * 1.14)
    ax.text(
        0.98,
        0.95,
        f"FOAK to NOAK {metric} reduction: {noak_reduction:.1f}%",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=11,
        bbox={"facecolor": "white", "edgecolor": "#cccccc", "alpha": 0.9},
    )


def _stacked_bars(ax, x: Iterable[int], df: pd.DataFrame, columns: list[tuple[str, str]]) -> None:
    bottom = np.zeros(len(df))
    for item in columns:
        if len(item) == 2:
            label, color_key = item
            display_label = label
        else:
            label, color_key, display_label = item
        values = df[label].astype(float)
        if not values.notna().any():
            continue
        clean_values = values.fillna(0.0).to_numpy()
        ax.bar(x, clean_values, bottom=bottom, label=display_label, color=CAPITAL_COLORS[color_key])
        bottom += clean_values


def _wrap_label(label: str, width: int = 16) -> str:
    compact = " ".join(str(label).split())
    return "\n".join(textwrap.wrap(compact, width=width))


def _bool_label(value) -> str:
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "non_nuclear", "modularized"}:
            return "TRUE"
        if normalized in {"0", "false", "no", "nuclear", "stick_built"}:
            return "FALSE"
    return "TRUE" if bool(value) else "FALSE"
