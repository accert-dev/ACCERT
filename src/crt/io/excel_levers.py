import pandas as pd

REQUIRED_COLS = {
  "Levers", "Min", "Low", "Median", "High", "Max",
  "Distribution", "Type", "Set", "Probabilities"
}

def read_levers_sheet(levers_xlsx: str, sheet_name="Levers") -> pd.DataFrame:
    df = pd.read_excel(levers_xlsx, sheet_name=sheet_name)

    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Levers sheet missing columns: {sorted(missing)}")

    return df

def read_baseline_levers(levers_xlsx: str, sheet_name="baseline levers") -> pd.DataFrame:
    """
    Returns the baseline levers sheet as a dataframe with columns: Levers, Baseline
    Keep it as df for now (you can convert to dict later).
    """
    df = pd.read_excel(levers_xlsx, sheet_name=sheet_name)
    if "Levers" not in df.columns or "Baseline" not in df.columns:
        raise ValueError("Baseline levers sheet must have columns: 'Levers' and 'Baseline'")
    return df
