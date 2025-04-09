import numpy as np
import pandas as pd


def generate_monte_carlo_samples(
    params_data: pd.DataFrame,
    sampling_amount: int,
    discount_rate: int,
    seed: int = None
) -> pd.DataFrame:
    """
    Generates a Monte Carlo simulation of the input parameters.

    Parameters
    ----------
    params_data : pd.DataFrame
        The input parameters (usually read from a `.csv` file) in the form of a Pandas DataFrame.
    sampling_amount : int
        The number of samples to generate from the Monte Carlo simulation.
    discount_rate : int
        The discount rate for the fuel cycle.
    seed: int, optional
        A see for the numpy random number generator to produce predictable values.

    Returns
    -------
        A Pandas Dataframe containing the results for the monte carlo simulation of each input parameter.
    """

    if seed is not None:
        np.random.seed(seed)

    monte_carlo_results = np.empty((params_data.shape[1], sampling_amount))

    for idx, (value_name, values) in enumerate(params_data.items()):
        # Discount rate or interest rate lines (no Monte Carlo sampling).
        if value_name in ["discount_rate", "interest_rate_constrct"]:
            monte_carlo_results[idx, :] = discount_rate / 100

        # No distribution: Uses the provided "nominal" value for all entries.
        elif values["distribution"] == 0:
            monte_carlo_results[idx, :] = values["nominal"]

        # Triangular distribution.
        # https://en.wikipedia.org/wiki/Triangular_distribution#Generating_triangular-distributed_random_variates
        elif values["distribution"] == 1:
            low, mode, high = values["low"], values["nominal"], values["high"]
            u = np.random.rand(sampling_amount)
            # The left area of the triangular distribution
            area1 = low + np.sqrt(u * (high - low) * (mode - low))
            # The right area of the triangular distribution
            area2 = high - np.sqrt((1 - u) * (high - low) * (high - mode))
            monte_carlo_results[idx, :] = np.where(u < (mode - low) / (high - low), area1, area2)

        # Uniform distribution.
        elif values["distribution"] == 2:
            u = np.random.rand(sampling_amount)
            monte_carlo_results[idx] = values["low"] + (values["high"] - values["low"]) * u

    return pd.DataFrame(monte_carlo_results.T, columns=params_data.columns)
