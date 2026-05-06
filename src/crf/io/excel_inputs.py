from pathlib import Path
import pandas as pd

COLS = [
  "Account", "Title", "Total Cost (USD)",
  "Factory Equipment Cost", "Site Labor Hours",
  "Site Labor Cost", "Site Material Cost"
]

NUMERIC_COLS = [col for col in COLS if col not in {"Account", "Title"}]

ADJUSTED_COLUMN_MAP = {
    "Total Cost (USD)": "Adjusted Total Cost",
    "Factory Equipment Cost": "Adjusted Factory Equipment Cost",
    "Site Labor Cost": "Adjusted Site Labor Cost",
    "Site Material Cost": "Adjusted Site Material Cost",
}


def _normalize_account(value) -> str:
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text

class InputStore:
    """
    Minimal store:
      - baseline csv per reactor_type
      - one spending curve csv shared
    """
    def __init__(self, data_dir: str = None, baseline_csv: str = None):
        if data_dir is None:
            self.data_dir = Path(__file__).resolve().parents[1] / "data"
        else:
            self.data_dir = Path(data_dir)
        self.baseline_csv = Path(baseline_csv) if baseline_csv else None
        self._baseline = {}
        self._spending = None

    def get_baseline(self, reactor_type: str):
        cache_key = (reactor_type, str(self.baseline_csv) if self.baseline_csv else "")
        if cache_key in self._baseline:
            df, power = self._baseline[cache_key]
            return df.copy(), power
        if reactor_type == "HTGR":
            path = self.data_dir / "HTGR_baseline.csv"
            power = 1056 * 1000
        elif reactor_type == "SFR":
            path = self.data_dir / "SFR_baseline.csv"
            power = 310.8 * 1000
        elif reactor_type == "AP1000":
            path = self.data_dir / "AP1000_baseline.csv"
            power = 2234 * 1000
        else:
            raise ValueError(f"Unknown reactor_type: {reactor_type}")
        if self.baseline_csv is not None:
            path = self.baseline_csv
        df = pd.read_csv(path)
        missing = set(COLS) - set(df.columns)
        if missing:
            raise ValueError(f"{path} missing columns: {sorted(missing)}")

        df = _coerce_adjusted_baseline_columns(df)
        df = df[COLS].copy()
        df["Account"] = df["Account"].map(_normalize_account)
        for col in NUMERIC_COLS:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "", regex=False), errors="coerce")
        self._baseline[cache_key] = (df, power)
        return df.copy(), power

    def get_spending_curve(self,reactor_type: str):

        if self._spending is not None:
            return self._spending
        if reactor_type == "HTGR":
            sp_path = self.data_dir / "HTGR_spending_curve.csv"
        elif reactor_type == "SFR":
            sp_path = self.data_dir / "SFR_spending_curve.csv"
        elif reactor_type == "AP1000":
            sp_path = self.data_dir / "AP1000_spending_curve.csv"
        else:
            raise ValueError(f"Unknown reactor_type: {reactor_type}")
        sp = pd.read_csv(sp_path)
        if "Month" not in sp.columns or "CDF" not in sp.columns:
            raise ValueError(f"{sp_path} must contain Month and CDF")
        months = sp["Month"].to_numpy(dtype=float)
        cdfs = sp["CDF"].to_numpy(dtype=float)
        self._spending = (months, cdfs)
        return self._spending


def _coerce_adjusted_baseline_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Use IAT adjusted costs when an IAT output CSV is passed as a CRF baseline."""
    out = df.copy()
    for target_col, adjusted_col in ADJUSTED_COLUMN_MAP.items():
        if adjusted_col in out.columns:
            out[target_col] = out[adjusted_col]
    return out
