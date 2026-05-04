from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


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
}


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
    if text in {"Korea", "China", "UAE"}:
        return text
    raise ValueError(f"Unsupported country {value!r}; expected Korea, China, or UAE")


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
    assumptions_path = Path(path) if path else Path(__file__).resolve().parent / "data" / "iat_assumptions.json"
    with assumptions_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
