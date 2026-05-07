STATIC_KEYS = [
    "Num_orders", "ITC", "n_ITC", "interest rate", "Design completion", "Design_Maturity_0",
    "supply chain exp_0", "N supply chain", "Const Proficiency", "N const prof", "AE",
    "N AE prof", "standardization", "modularity", "BOP commercial", "RB Safety Related",
]

SUMMARY_KEYS = [
    "cons_duration_cumulative_wz_startup",
    "occLastUnit", "TCILastUnit", "durationsLastUnit",
    "avg_OCC", "avg_TCI", "avg_duration",
]

def build_headers(max_orders: int) -> list[str]:
    return (
        STATIC_KEYS
        + [f"OCC_{i}" for i in range(max_orders)]
        + [f"TCI_{i}" for i in range(max_orders)]
        + [f"duration_{i}" for i in range(max_orders)]
        + SUMMARY_KEYS
    )

def validate_config(config: dict):
    required = {
        "inputs_xlsx", "reactor_type",
        "f_22", "f_2321",
        "land_cost_per_acre_0",
        "startup_0",
        "staggering_ratio",
    }
    missing = required - set(config)
    if missing:
        raise ValueError(f"Missing config keys: {sorted(missing)}")