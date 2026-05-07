import pandas as pd
# --- Unique internal IDs (these are the keys everywhere else) ---
LEVER_IDS = [
    "num_orders",
    "itc_percent",
    "n_itc",
    "interest_percent",
    "design_completion_percent",
    "design_maturity",
    "proc_exp",
    "N_proc",
    "ce_exp",
    "N_cons",
    "ae_exp",
    "N_AE",
    "standardization_percent",
    "modularity_code",
    "bop_grade_code",
    "rb_grade_code",
]

# --- Map Excel lever names to internal IDs ---
EXCEL_NAME_TO_ID_ORDERED = [
    ("Number of firm orders", "num_orders"),
    ("ITC amount", "itc_percent"),
    ("Number of plants claiming ITC", "n_itc"),
    ("Interest rate", "interest_percent"),
    ("Design completion", "design_completion_percent"),
    ("Design maturity (technology maturity)", "design_maturity"),
    ("Supply chain proficiency", "proc_exp"),
    ("Number of plants to achieve best proficiency", "N_proc"),   # first occurrence
    ("Construction proficiency", "ce_exp"),
    ("Number of plants to achieve best proficiency", "N_cons"),   # second occurrence
    ("A/E proficiency", "ae_exp"),
    ("Number of plants to achieve best proficiency", "N_AE"),     # third occurrence
    ("Cross-site standardization", "standardization_percent"),
    ("Modular civil construction", "modularity_code"),
    ("Commercial BOP", "bop_grade_code"),
    ("Non-safety-related RB", "rb_grade_code"),
]

STATIC_KEYS = [
    "Num_orders", "num_NOAK", "ITC", "n_ITC", "interest rate", "Design completion", "Design_Maturity_0",
    "supply chain exp_0", "N supply chain", "Const Proficiency", "N const prof", "AE",
    "N AE prof", "standardization", "modularity", "BOP commercial", "RB Safety Related",
]


def _normalize_excel_name(s: str) -> str:
    # make matching robust to extra spaces
    return " ".join(str(s).strip().split())


def attach_internal_ids(levers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a 'lever_id' column to the Levers dataframe using ordered matching.
    This is required because Excel contains repeated lever names.
    """
    df = levers_df.copy()
    df["Levers_norm"] = df["Levers"].apply(_normalize_excel_name)

    ordered = [( _normalize_excel_name(n), i ) for n, i in EXCEL_NAME_TO_ID_ORDERED]

    ids = []
    cursor = 0
    for row_name in df["Levers_norm"].tolist():
        if cursor >= len(ordered):
            raise ValueError("Levers sheet has more rows than expected mapping.")

        expected_name, lever_id = ordered[cursor]
        if row_name != expected_name:
            raise ValueError(
                f"Levers sheet row mismatch at position {cursor}:\n"
                f"  expected: '{expected_name}'\n"
                f"  found:    '{row_name}'\n"
                f"Fix the Excel row order OR update EXCEL_NAME_TO_ID_ORDERED."
            )
        ids.append(lever_id)
        cursor += 1

    df["lever_id"] = ids
    df.drop(columns=["Levers_norm"], inplace=True)

    # final validation
    if df["lever_id"].tolist() != LEVER_IDS:
        raise ValueError("Internal lever_id order does not match LEVER_IDS. Check mapping.")
    return df


def sample_column_to_levers(samples_matrix, levers_df_with_ids: pd.DataFrame, sample_idx: int) -> dict:
    """
    samples_matrix shape: (n_levers, n_samples)
    returns levers_raw dict keyed by internal lever ids.
    """
    vec = samples_matrix[:, sample_idx]
    ids = levers_df_with_ids["lever_id"].tolist()
    return {ids[i]: vec[i] for i in range(len(ids))}


def static_row_from_levers(levers_raw: dict) -> dict:
    """
    Convert internal lever dict into your legacy CSV static columns.
    """
    return {
        "Num_orders": levers_raw["num_orders"],
        "num_NOAK": levers_raw.get("num_NOAK", levers_raw["num_orders"]),
        "ITC": levers_raw["itc_percent"],
        "n_ITC": levers_raw["n_itc"],
        "interest rate": levers_raw["interest_percent"],
        "Design completion": levers_raw["design_completion_percent"],
        "Design_Maturity_0": levers_raw["design_maturity"],
        "supply chain exp_0": levers_raw["proc_exp"],
        "N supply chain": levers_raw["N_proc"],
        "Const Proficiency": levers_raw["ce_exp"],
        "N const prof": levers_raw["N_cons"],
        "AE": levers_raw["ae_exp"],
        "N AE prof": levers_raw["N_AE"],
        "standardization": levers_raw["standardization_percent"],
        "modularity": levers_raw["modularity_code"],
        "BOP commercial": levers_raw["bop_grade_code"],
        "RB Safety Related": levers_raw["rb_grade_code"],
    }
