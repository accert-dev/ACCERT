import numpy as np
import pandas as pd


def backend(data: pd.DataFrame, t_plant, lev_factor, e_year, n_cycl: np.ndarray, t_cyc: np.ndarray):
    """
    Calculate the levelized back-end cost of the nuclear power plant.
    The back-end cost includes the costs associated with spent nuclear fuel (SNF) management,
    including storage, conditioning, and disposal.
    The function takes into account the number of cycles, cycle time, and other parameters
    related to the nuclear power plant's operation.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing the parameters related to the nuclear power plant.
    t_plant : float
        The total operational time of the plant in years.
    lev_factor : float
        The leveling factor for the discount rate.
    e_year : float
        The total energy produced by the plant in a year.
    n_cycl : np.ndarray
        Array containing the number of cycles for each batch.
    t_cyc : np.ndarray
        Array containing the cycle time for each batch.
    Returns
    -------
    levelized_back_end: pd.DataFrame
        DataFrame containing the levelized back-end cost of the nuclear power plant.
    """

    # Always 1 kg of product
    pv_sf_storage = data["cost_offsite_storage"] * 1 / np.exp(data["discount_rate"] * t_cyc)
    # Conditioning always necessary before off-site transportation
    pv_snf_conditioning = data["cost_SNF_cond"] * 1 / np.exp(data["discount_rate"] * t_cyc)

    # case 1 # do nothing
    pv_back_end_additional_1 = 0
    # case 2 # direct geologic disposal !!!!!!!!! adjust the time of discounting
    pv_back_end_additional_2 = data["cost_geologic_disposal"] * 1 * np.exp(
        data["discount_rate"] * data["lead_time_FP_disposal"]
    )
    # case 3 # geologic disposal after dry storage
    pv_back_end_additional_3 = (data["cost_dry_storage"] * 1 * np.exp(
        data["discount_rate"] * data["lead_time_dry_storage"]
    ) + data["cost_geologic_disposal"] * 1 * np.exp(data["discount_rate"] * data["lead_time_FP_disposal"])) * 1
    # case 4 # 1 mills/ kWh (added after the discounting
    pv_back_end_additional_4 = 0
    # case 5 #  reprocessing + refabrication within the island
    pv_reprocessing_r2 = data["cost_ec_rprocsng"] * 1 * np.exp(data["discount_rate"] * data["lead_time_rprocsng"])
    pv_fp_conditioning_r_2 = data["cost_FP_cond"] * data["frac_FP_discharged"] * np.exp(
        data["discount_rate"] * data["lead_time_FP_cond"]
    )
    pv_fp_geol_disposal_r_2 = data["cost_FP_geologic"] * data["frac_FP_discharged"] * np.exp(
        data["discount_rate"] * data["lead_time_FP_disposal"]
    )
    pv_back_end_additional_5 = pv_reprocessing_r2 + pv_fp_conditioning_r_2 + pv_fp_geol_disposal_r_2

    reproc_frac_5 = pv_reprocessing_r2 / pv_back_end_additional_5
    fp_cond_frac_5 = pv_fp_conditioning_r_2 / pv_back_end_additional_5
    fp_disp_frac_5 = pv_fp_geol_disposal_r_2 / pv_back_end_additional_5

    pv_back_end_additional = pv_back_end_additional_1 * data["frac_back_end_1"] + pv_back_end_additional_2 * data[
        "frac_back_end_2"] + pv_back_end_additional_3 * data["frac_back_end_3"] + pv_back_end_additional_4 * data[
                                 "frac_back_end_4"] + pv_back_end_additional_5 * data["frac_back_end_5"]

    pv_back_end_tot = pv_sf_storage + pv_snf_conditioning + pv_back_end_additional

    sf_storage_frac_back_end = pv_sf_storage / pv_back_end_tot
    sf_condit_frac_back_end = pv_snf_conditioning / pv_back_end_tot
    direct_disp_frac_back_end = pv_back_end_additional_2 * data["frac_back_end_2"] / pv_back_end_tot
    reproc_5_frac_back_end = reproc_frac_5 * pv_back_end_additional_5 * data["frac_back_end_5"] / pv_back_end_tot
    fp_cond_5_frac_back_end = fp_cond_frac_5 * pv_back_end_additional_5 * data["frac_back_end_5"] / pv_back_end_tot
    fp_disp_5_frac_back_end = fp_disp_frac_5 * pv_back_end_additional_5 * data["frac_back_end_5"] / pv_back_end_tot

    pv_back_end = pv_back_end_tot * (data["HM_mass_direct_spec"] / 1000 / data["num_batches"])

    # Most create a copy of the values. Otherwise, `pv_back_end_o` will also be updated below.
    pv_back_end_o = pv_back_end.copy(deep=True)
    # TODO: Should the `np.arange(...)` start at 1?
    # k = n_cycl - 1
    indices = np.arange(1, np.max(n_cycl))  # Generate an array of indices from 0 to MAX(n_cycl - 2)
    m = np.where(indices < n_cycl[:, np.newaxis], indices, -np.inf)  # Apply the mask to fill the matrix.
    # We used -np.inf to define `matrix` above so that those values become zero after exponentiating,
    # and so the sum will not be affected by those values. If we used 0 instead of -inf, those values
    # would become 1 after exponentiation, which would be added in the sum.
    pv_back_end *= 1 + np.exp(
        (data["escalation_rate_back"] - data["discount_rate"]).values.reshape(-1, 1) * m * t_cyc.reshape(-1, 1)
    ).sum(axis=1)
    # as above, but this is the residual of the last cycle, in percent over the cycle (~ 15 #) # Not realistic
    # because of transportation costs (James of Exelon): only the fraction of t_cyc utilized is a cost,
    # while the rest is sold.
    pv_back_end += (pv_back_end_o * np.exp(
        (data["escalation_rate_back"] - data["discount_rate"]) * n_cycl * t_cyc
    )) * (t_plant - (n_cycl * t_cyc)) / t_cyc
    # adds the 1 mills/kWh or not depending if it has been requested
    # (on what fraction??, in this case total electricity produced, not core discharged)
    levelized_back_end = np.where(
        data["frac_back_end_4"] == 0,
        pv_back_end * lev_factor * 1000 / e_year,
        pv_back_end * lev_factor * 1000 / e_year + data["waste_disposal_fee"]
    )

    return levelized_back_end
