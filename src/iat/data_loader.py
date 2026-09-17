from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any
import re

import pandas as pd


COST_CATEGORIES = ["equipment", "material", "labor", "land", "catchall"]

STANDARD_COST_COLUMNS = [
    "Total Cost (USD)",
    "Factory Equipment Cost",
    "Site Labor Hours",
    "Site Labor Cost",
    "Site Material Cost",
]

COUNTRY_ALIASES = {
    "korea": "Korea",
    "kor": "Korea",
    "south korea": "Korea",
    "china": "China",
    "chn": "China",
    "uae": "UAE",
    "united arab emirates": "UAE",
    "poland": "Poland",
    "pol": "Poland",
    "el salvador": "El Salvador",
    "elsalvador": "El Salvador",
    "slv": "El Salvador",
}

_DATA_DIR = Path(__file__).resolve().parent / "data"


def normalize_account(value: Any) -> str:
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text


def normalize_country(value: str) -> str:
    key = str(value).strip().lower()
    if key in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[key]
    text = str(value).strip()
    available = sorted(load_assumptions()["adjustment_factors"])
    if text in available:
        return text
    raise ValueError(
        f"Unsupported country {value!r}; expected one of {', '.join(available)}"
    )


def reactor_family_from_type(reactor_type: str) -> str:
    text = str(reactor_type).strip().lower()
    if "smr" in text:
        return "SMR"
    if "lr" in text or "large" in text or "ap1000" in text:
        return "LR"
    raise ValueError(
        f"Unsupported reactor_type {reactor_type!r}; expected large reactor/LR, SMR, "
        "ACCERT output-LR, or ACCERT output-SMR"
    )


@lru_cache(maxsize=4)
def load_assumptions(path: str | None = None) -> dict[str, Any]:
    data_dir = Path(path) if path else _DATA_DIR
    adjustment_factors = _read_adjustment_factors(data_dir / "adjustment_factors.csv")
    countries = list(adjustment_factors)
    return {
        "adjustment_factors": adjustment_factors,
        "families": {
            "LR": _read_family_records(data_dir / "lr_localization.csv", countries),
            "SMR": _read_family_records(data_dir / "smr_localization.csv", countries),
        },
        "input_is_occ": {
            "LR": True,
            "SMR": True,
            "ACCERT output-LR": False,
            "ACCERT output-SMR": False,
        },
    }


def _read_adjustment_factors(path: Path) -> dict[str, dict[str, float]]:
    df = pd.read_csv(path)
    factors: dict[str, dict[str, float]] = {}
    for _, row in df.iterrows():
        country = str(row["country"]).strip()
        factors[country] = {
            "import_tariff": _num(row.get("import_tariff")),
            "equipment": _num(row.get("equipment")),
            "material": _num(row.get("material")),
            "labor": _num(row.get("labor")),
            "labor_o_and_m": _num(row.get("labor_o_and_m")),
            "land": _num(row.get("land")),
            "catchall": _num(row.get("catchall")),
        }
    return factors


def _read_family_records(path: Path, countries: list[str]) -> list[dict[str, Any]]:
    df = pd.read_csv(path)
    records: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        account = normalize_account(row["account"])
        title = str(row["title"]).strip()
        if not account or not title:
            continue

        localization: dict[str, dict[str, float]] = {}
        for country in countries:
            prefix = _country_column_prefix(country)
            localization[country] = {
                category: _num(row.get(f"{prefix}_localization_{category}"))
                for category in COST_CATEGORIES
            }

        category_shares = {
            category: _num(row.get(f"category_share_{category}"))
            for category in COST_CATEGORIES
        }

        records.append(
            {
                "account": account,
                "title": title,
                "coa_breakdown": _num(row.get("coa_breakdown")),
                "localization": localization,
                "category_shares": category_shares,
            }
        )
    return records


def _country_column_prefix(country: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", country.strip().lower()).strip("_")


def _num(value: Any) -> float:
    if value is None:
        return 0.0
    if pd.isna(value):
        return 0.0
    if isinstance(value, str):
        value = value.strip().replace(",", "")
        if not value:
            return 0.0
    return float(value)
