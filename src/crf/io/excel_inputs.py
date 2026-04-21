from pathlib import Path
import pandas as pd

COLS = [
  "Account", "Title", "Total Cost (USD)",
  "Factory Equipment Cost", "Site Labor Hours",
  "Site Labor Cost", "Site Material Cost"
]

class InputStore:
    """
    Minimal store:
      - baseline csv per reactor_type
      - one spending curve csv shared
    """
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = Path(__file__).resolve().parents[1] / "data"
        else:
            self.data_dir = Path(data_dir)
        self._baseline = {}
        self._spending = None

    def get_baseline(self, reactor_type: str):
        
        if reactor_type in self._baseline:
            df, power = self._baseline[reactor_type]
            return df.copy(), power
        if reactor_type == "HTGR":
            # path = f"{self.data_dir}/HTGR_baseline.csv"
            path = self.data_dir / "HTGR_baseline.csv"
            power = 1056 * 1000
        elif reactor_type == "SFR":
            path = self.data_dir / "SFR_baseline.csv"
            power = 310.8 * 1000
        else:
            raise ValueError(f"Unknown reactor_type: {reactor_type}")
        # print current running path for debugging
        print(f"Loading baseline from: {path}")
        df = pd.read_csv(path)
        missing = set(COLS) - set(df.columns)
        if missing:
            raise ValueError(f"{path} missing columns: {sorted(missing)}")

        df = df[COLS].copy()
        self._baseline[reactor_type] = (df, power)
        return df.copy(), power

    def get_spending_curve(self,reactor_type: str):

        if self._spending is not None:
            return self._spending
        if reactor_type == "HTGR":
            sp_path = self.data_dir / "HTGR_spending_curve.csv"
        elif reactor_type == "SFR":
            sp_path = self.data_dir / "SFR_spending_curve.csv"
        else:
            raise ValueError(f"Unknown reactor_type: {reactor_type}")
        sp = pd.read_csv(sp_path)
        if "Month" not in sp.columns or "CDF" not in sp.columns:
            raise ValueError(f"{sp_path} must contain Month and CDF")
        months = sp["Month"].to_numpy(dtype=float)
        cdfs = sp["CDF"].to_numpy(dtype=float)
        self._spending = (months, cdfs)
        return self._spending

