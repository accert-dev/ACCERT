"""Shared reactor definitions used by CRT and the connected IAT workflow."""

from __future__ import annotations


REACTOR_CONFIGS = {
    "AP1000": {
        "power_mwe": 2234.0,
        "iat_family": "LR",
        "iat_label": "Large Reactor",
        "construction_duration_months": 76.0,
        "labor_hours_20s": 51_112_635.470753975,
    },
    "SFR": {
        "power_mwe": 310.8,
        "iat_family": "SMR",
        "iat_label": "SMR",
        "construction_duration_months": 80.0,
        "labor_hours_20s": 10_402_590.638988608,
    },
    "HTGR": {
        "power_mwe": 1056.0,
        "iat_family": "LR",
        "iat_label": "Large Reactor",
        "construction_duration_months": 125.0,
        "labor_hours_20s": 37_288_941.04573331,
    },
}


def reactor_power_mwe(reactor_type: str) -> float:
    try:
        return float(REACTOR_CONFIGS[reactor_type]["power_mwe"])
    except KeyError as exc:
        raise ValueError(f"Unknown reactor type: {reactor_type}") from exc


def iat_api_reactor_type(reactor_type: str, *, csv_mode: bool) -> str:
    config = REACTOR_CONFIGS.get(reactor_type)
    if config is None:
        raise ValueError(f"Unknown reactor type: {reactor_type}")
    prefix = "ACCERT output-" if csv_mode else ""
    return f"{prefix}{config['iat_family']}"

