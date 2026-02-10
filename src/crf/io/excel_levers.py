import pandas as pd

REQUIRED_COLS = {
  "Distribution", "Min", "Max", "Median", "Low", "High",
  "Set", "Probabilities", "Type"
}

def read_lever_sheet(levers_xlsx: str, sheet_name="Levers") -> pd.DataFrame:
    df = pd.read_excel(levers_xlsx, sheet_name=sheet_name)
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Levers sheet missing columns: {sorted(missing)}")
    return df
