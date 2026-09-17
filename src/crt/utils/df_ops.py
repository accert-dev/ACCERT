import numpy as np
import pandas as pd

def _acc_str(x) -> str:
    return str(x).strip()

def _mask_accounts(df: pd.DataFrame, accounts) -> pd.Series:
    """
    Robust account matcher: compares Account values as stripped strings.
    accounts can be a scalar or iterable of scalars.
    """
    if isinstance(accounts, (str, int, float)):
        accounts = [accounts]
    targets = {_acc_str(a) for a in accounts}
    return df["Account"].astype(str).str.strip().isin(targets)

def getv(df: pd.DataFrame, account, col):
    a = _acc_str(account)
    s = df.loc[df["Account"].astype(str).str.strip().eq(a), col]
    if s.empty:
        raise KeyError(
            f"Account '{account}' not found in dataframe (column='{col}'). "
            f"Available sample accounts: {df['Account'].astype(str).str.strip().head(30).tolist()}"
        )
    return s.iloc[0]

def setv(df: pd.DataFrame, account, col, value):
    mask = _mask_accounts(df, account)
    if not mask.any():
        raise KeyError(f"Account '{account}' not found for setv (column='{col}')")
    df.loc[mask, col] = value

def mulv(df: pd.DataFrame, accounts, cols, factor: float):
    mask = _mask_accounts(df, accounts)
    if not mask.any():
        raise KeyError(f"None of accounts {accounts} found for mulv")
    df.loc[mask, cols] = df.loc[mask, cols].to_numpy() * factor

def resetv(df: pd.DataFrame, accounts, cols):
    mask = _mask_accounts(df, accounts)
    if not mask.any():
        raise KeyError(f"None of accounts {accounts} found for resetv")
    df.loc[mask, cols] = np.nan
