import pandas as pd

COLS = [
  "Account", "Title", "Total Cost (USD)",
  "Factory Equipment Cost", "Site Labor Hours",
  "Site Labor Cost", "Site Material Cost"
]

class InputStore:
    def __init__(self, inputs_xlsx: str):
        self.inputs_xlsx = inputs_xlsx
        self._baseline = {}
        self._spending = None

    def get_baseline(self, reactor_type: str):
        if reactor_type in self._baseline:
            df, power = self._baseline[reactor_type]
            return df.copy(), power

        if reactor_type == "Concept A":
            df = pd.read_excel(self.inputs_xlsx, sheet_name="Concept_A", nrows=69)[COLS].copy()
            power = 1056 * 1000
        elif reactor_type == "Concept B":
            df = pd.read_excel(self.inputs_xlsx, sheet_name="Concept_B", nrows=69)[COLS].copy()
            power = 310.8 * 1000
        else:
            raise ValueError(f"Unknown reactor_type: {reactor_type}")

        self._baseline[reactor_type] = (df, power)
        return df.copy(), power

    def get_spending_curve(self):
        if self._spending is not None:
            return self._spending
        sp = pd.read_excel(self.inputs_xlsx, sheet_name="Ref Spending Curve", nrows=104, usecols="A:D")
        months = sp["Month"].to_numpy(dtype=float)
        cdfs = sp["CDF"].to_numpy(dtype=float)
        self._spending = (months, cdfs)
        return self._spending
