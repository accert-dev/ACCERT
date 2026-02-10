import numpy as np
import pandas as pd

def getv(df: pd.DataFrame, account, col: str):
    return df.loc[df["Account"].eq(account), col].iloc[0]

def setv(df: pd.DataFrame, account, col: str, value):
    df.loc[df["Account"].eq(account), col] = value

def mulv(df: pd.DataFrame, accounts, cols, factor: float):
    m = df["Account"].isin(accounts)
    df.loc[m, cols] = df.loc[m, cols].to_numpy() * factor

def resetv(df: pd.DataFrame, accounts, cols):
    m = df["Account"].isin(accounts)
    df.loc[m, cols] = np.nan
