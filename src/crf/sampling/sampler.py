# src/crf/sampling/sampler.py
import numpy as np
import scipy.stats as stats

def trunc_normal(min_, low_, med_, high_, max_, n):
    std = (high_ - low_) / 4
    mean = med_
    a, b = (min_ - mean) / std, (max_ - mean) / std
    return stats.truncnorm.rvs(a=a, b=b, loc=mean, scale=std, size=n)

def truncate_shift_lognormal(min_, low_, med_, high_, max_, n):
    std = (np.log(high_) - np.log(low_)) / 4
    mean = np.log(med_)
    a, b = (np.log(min_) - mean) / std, (np.log(max_) - mean) / std
    x = stats.truncnorm.rvs(a=a, b=b, loc=mean, scale=std, size=n)
    return np.exp(x)

def sample_levers(n_samples: int, levers_df, seed: int | None = None) -> np.ndarray:
    if seed is not None:
        np.random.seed(seed)

    n_var = levers_df.shape[0]
    out = np.empty((n_var, n_samples), dtype=float)

    dist = levers_df["Distribution"]
    min_ = levers_df["Min"]; max_ = levers_df["Max"]; med_ = levers_df["Median"]
    low_ = levers_df["Low"]; high_ = levers_df["High"]
    set_ = levers_df["Set"]; p_ = levers_df["Probabilities"]
    typ = levers_df["Type"]

    for i in range(n_var):
        d = str(dist.iloc[i]).lower()

        if d in ["normal", "gaussian"]:
            out[i, :] = trunc_normal(min_.iloc[i], low_.iloc[i], med_.iloc[i], high_.iloc[i], max_.iloc[i], n_samples)
            if str(typ.iloc[i]).lower() in ["discrete", "integer"]:
                out[i, :] = np.round(out[i, :])

        elif d in ["lognormal"]:
            out[i, :] = truncate_shift_lognormal(min_.iloc[i], low_.iloc[i], med_.iloc[i], high_.iloc[i], max_.iloc[i], n_samples)
            if str(typ.iloc[i]).lower() in ["discrete", "integer"]:
                out[i, :] = np.round(out[i, :])

        elif d in ["triangular"]:
            out[i, :] = np.random.triangular(left=min_.iloc[i], mode=med_.iloc[i], right=max_.iloc[i], size=n_samples)
            if str(typ.iloc[i]).lower() in ["discrete", "integer"]:
                out[i, :] = np.round(out[i, :])

        elif d in ["uniform"]:
            out[i, :] = np.random.uniform(left=min_.iloc[i], right=max_.iloc[i], size=n_samples)
            if str(typ.iloc[i]).lower() in ["discrete", "integer"]:
                out[i, :] = np.round(out[i, :])

        elif d in ["binary", "boolean", "set"]:
            choices = eval("[" + str(set_.iloc[i]) + "]")
            probs = eval("[" + str(p_.iloc[i]) + "]")
            out[i, :] = np.random.choice(choices, size=n_samples, p=probs)

        else:
            raise ValueError(f"Invalid Distribution='{dist.iloc[i]}' at row {i}")

    return out
