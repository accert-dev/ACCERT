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
        "iat_family": None,
        "iat_label": None,
        "construction_duration_months": 125.0,
        "labor_hours_20s": 37_288_941.04573331,
    },
}

IAT_TO_CRT_TYPES = {
    "Large Reactor": ("AP1000",),
    "SMR": ("SFR",),
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
    if config["iat_family"] is None:
        raise ValueError(f"No compatible IAT reactor family is defined for {reactor_type}")
    prefix = "ACCERT output-" if csv_mode else ""
    return f"{prefix}{config['iat_family']}"


def compatible_crt_types(iat_reactor_label: str) -> tuple[str, ...]:
    try:
        return IAT_TO_CRT_TYPES[iat_reactor_label]
    except KeyError as exc:
        raise ValueError(f"Unknown IAT reactor type: {iat_reactor_label}") from exc


def iat_api_type_from_label(iat_reactor_label: str, *, csv_mode: bool) -> str:
    if iat_reactor_label == "Large Reactor":
        family = "LR"
    elif iat_reactor_label == "SMR":
        family = "SMR"
    else:
        raise ValueError(f"Unknown IAT reactor type: {iat_reactor_label}")
    prefix = "ACCERT output-" if csv_mode else ""
    return f"{prefix}{family}"
