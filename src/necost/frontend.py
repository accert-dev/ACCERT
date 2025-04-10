import numpy as np
import pandas as pd


def front_end_1(data: pd.DataFrame):
    """Calculate the front-end costs for the first route (natural uranium) of the nuclear fuel cycle.
    This function computes the mass of uranium and the present value of the front-end costs
    based on the input data.
    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing the parameters related to the nuclear fuel cycle.
    Returns
    -------
    m_fabrication : float
        Mass of uranium fabricated (kg-HM).
    m_enrichment : float
        Mass of uranium enriched (kg-HM).
    pv_front_end_u_1 : float
        Present value of the front-end costs.
    """
    m_fabrication = (1 / (1 - data["fab_loss_percent"]))
    m_enrichment = m_fabrication * ((data["nrchmt_fresh"] - data["tails_nrchmt_fresh"]) / (
        data["feed_nrchmt_fresh"] - data["tails_nrchmt_fresh"]))
    # mass flow into conversion plant (kg-HM-UF6/kg-HM)
    m_conversion = m_enrichment * (1 / (1 - data["conv_loss_percent"]))
    # Mass of depleted U to be sent to reconversion
    m_deconversion = data["frac_DU_deconverted"] * (m_enrichment - m_fabrication)
    # potential functions of product, tails, feed: swu_n is the amount of SWU per kg of U
    v_p = ((2 * data["nrchmt_fresh"]) - 1) * np.log(data["nrchmt_fresh"] / (1 - data["nrchmt_fresh"]))
    v_t = ((2 * data["tails_nrchmt_fresh"]) - 1) * np.log(data["tails_nrchmt_fresh"] / (1 - data["tails_nrchmt_fresh"]))
    v_f = ((2 * data["feed_nrchmt_fresh"]) - 1) * np.log(data["feed_nrchmt_fresh"] / (1 - data["feed_nrchmt_fresh"]))
    # if enr_product=enr_feed --> swu_n=0
    swu_n = v_p * m_fabrication + v_t * (m_enrichment - m_fabrication) - v_f * m_enrichment

    # unit costs, or costs per 1 kg of fabricated fuel (in  $/kg-HM)
    pv_ore_u_1 = data["cost_U"] * m_conversion * np.exp(data["discount_rate"] * data["lead_time_purchase"])
    pv_conversion_u_1 = data["cost_conv"] * m_conversion * np.exp(data["discount_rate"] * data["lead_time_conv"])
    pv_enrichment_u_1 = data["cost_SWU"] * swu_n * np.exp(data["discount_rate"] * data["lead_time_nrchmt"])
    # note: it happens at the same time as enrichment
    pv_deconversion_u_1 = (data["cost_deconv"] + data["cost_DU_disposal"]) * m_deconversion * np.exp(
        data["discount_rate"] * data["lead_time_nrchmt"]
    )
    pv_fabrication_u_1 = (data["cost_fuel_fab"] * m_fabrication + data["added_cost_fuel"] * data[
        "extra_fab_material"]) * np.exp(data["discount_rate"] * data["lead_time_fab"])

    pv_front_end_u_1 = pv_fabrication_u_1 + pv_deconversion_u_1 + pv_enrichment_u_1 + pv_conversion_u_1 + pv_ore_u_1

    # Only used in results computation
    fab_frac_u_front_end = pv_fabrication_u_1 / pv_front_end_u_1  # Fractions calculated for later use (maybe)
    deconv_frac_u_front_end = pv_deconversion_u_1 / pv_front_end_u_1
    enr_frac_u_front_end = pv_enrichment_u_1 / pv_front_end_u_1
    conv_frac_u_front_end = pv_conversion_u_1 / pv_front_end_u_1
    ore_frac_u_front_end = pv_ore_u_1 / pv_front_end_u_1

    return m_fabrication, m_enrichment, pv_front_end_u_1


def front_end_2(data: pd.DataFrame):
    """Calculate the front-end costs for the second route (reprocessed uranium) of the nuclear fuel cycle.
    This function computes the mass of uranium and the present value of the front-end costs
    based on the input data.
    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing the parameters related to the nuclear fuel cycle.
    Returns
    -------
    pv_front_end_r_1 : float
        Present value of the front-end costs.
    """

    fab_loss_percent = data["fab_loss_percent"]

    # ----------   Front end 2: Reprocessing route (for 1 kg of fabricated fuel) from previous island
    # includes losses: all to get 1 kg exactly of fabricated reprocessed fuel
    m_pu_fabrication_r = data["Pu_new"] / (1 - fab_loss_percent)  # in kg
    m_ma_fabrication_r = data["MA_new"] / (1 - fab_loss_percent)
    m_nu_fabrication_r = data["frac_NU_new"] / (1 - fab_loss_percent)
    m_du_fabrication_r = data["frac_DU_new"] / (1 - fab_loss_percent)
    m_th_fabrication_r = data["frac_Th_new"] / (1 - fab_loss_percent)
    m_ru_fabrication_r = (1 - data["Pu_new"] - data["MA_new"] - data["frac_NU_new"] - data["frac_DU_new"] - data[
        "frac_Th_new"]) / (1 - fab_loss_percent)
    m_fabrication_r = m_pu_fabrication_r + m_ma_fabrication_r + m_nu_fabrication_r + m_du_fabrication_r + m_th_fabrication_r + m_ru_fabrication_r

    m_reprocessed_r = pd.Series(np.zeros(len(data)))

    # Pu primary fissile
    m_reprocessed_r.mask(
        cond=data["primary_fissile_reprcsd"] == 1,
        other=m_pu_fabrication_r / data["Pu_content_previous"] / (1 - data["rprocsng_loss_percent"]),
        inplace=True
    )

    # U Primary fissile
    # TODO: Can we optimize memory complexity here?
    m_ru_required_from_reproc = m_ru_fabrication_r * (
        (data["nrchmt_lvl_product_rec"] - data["nrchmt_lvl_tails_rec"]) / (
        data["nrchmt_lvl_feed_rec"] - data["nrchmt_lvl_tails_rec"]))
    m_conversion_r = np.where(
        data["primary_fissile_reprcsd"] == 2, m_ru_required_from_reproc * (1 / (1 - data["conv_loss_percent"])), 0
    )
    m_reprocessed_r.mask(
        cond=data["primary_fissile_reprcsd"] == 2,
        other=m_ru_required_from_reproc / data["U_content_previous"] / (1 - data["rprocsng_loss_percent"]),
        inplace=True
    )
    m_deconversion_r = np.where(
        data["primary_fissile_reprcsd"] == 2,
        data["frac_DU_deconverted"] * (m_ru_required_from_reproc - m_ru_fabrication_r),
        0
    )
    v_p_r = ((2 * data["nrchmt_lvl_product_rec"]) - 1) * np.log(
        data["nrchmt_lvl_product_rec"] / (1 - data["nrchmt_lvl_product_rec"])
    )  # potential functions of product, tails, feed: swu_n is the amount of SWU per kg of U
    v_t_r = ((2 * data["nrchmt_lvl_tails_rec"]) - 1) * np.log(
        data["nrchmt_lvl_tails_rec"] / (1 - data["nrchmt_lvl_tails_rec"])
    )
    v_f_r = ((2 * data["nrchmt_lvl_feed_rec"]) - 1) * np.log(
        data["nrchmt_lvl_feed_rec"] / (1 - data["nrchmt_lvl_feed_rec"])
    )
    # if enr_product=enr_feed --> swu_n=0
    swu_r = np.where(
        data["primary_fissile_reprcsd"] == 2, v_p_r * m_ru_fabrication_r + v_t_r * (
            m_ru_required_from_reproc - m_ru_fabrication_r) - v_f_r * m_ru_required_from_reproc, 0
    )

    # MA Primary fissile
    m_reprocessed_r.mask(
        cond=data["primary_fissile_reprcsd"] == 3,
        other=m_ma_fabrication_r / data["MA_content_previous"] / (1 - data["rprocsng_loss_percent"]),
        inplace=True
    )

    # TRU Primary fissile
    m_reprocessed_r.mask(
        cond=data["primary_fissile_reprcsd"] == 4,
        other=(m_ma_fabrication_r + m_pu_fabrication_r) / (
            data["MA_content_previous"] + data["Pu_content_previous"]) / (
                  1 - data["rprocsng_loss_percent"]),
        inplace=True
    )

    m_fp_reprocessed_r = data["FP_content_previous"] * m_reprocessed_r * (1 - data["rprocsng_loss_percent"])
    pv_reprocessing_r_1 = data["cost_rprocsng"] * m_reprocessed_r * np.exp(
        data["discount_rate"] * data["lead_time_rprocsng"]
    )
    pv_enrichment_r_1 = data["cost_nrchmt_rec"] * swu_r * np.exp(
        data["discount_rate"] * data["lead_time_nrchmt_rec"]
    )
    pv_conversion_r_1 = data["cost_conv_rec"] * m_conversion_r * np.exp(
        data["discount_rate"] * data["lead_time_conv_rec"]
    )
    pv_deconversion_r_1 = (data["cost_deconv"] + data["cost_DU_disposal"]) * m_deconversion_r * np.exp(
        data["discount_rate"] * data["lead_time_nrchmt_rec"]
    )
    pv_nu_r_1 = data["cost_U"] * data["frac_NU_new"] * np.exp(data["discount_rate"] * data["lead_time_refab"])
    pv_th_r_1 = data["cost_Th"] * data["frac_Th_new"] * np.exp(data["discount_rate"] * data["lead_time_refab"])
    pv_fabrication_r_1 = data["cost_MOX_fab"] * m_fabrication_r * np.exp(
        data["discount_rate"] * data["lead_time_refab"]
    )
    pv_fp_conditioning_r_1 = data["cost_FP_cond"] * m_fp_reprocessed_r * np.exp(
        data["discount_rate"] * data["lead_time_FP_cond"]
    )
    pv_fp_geol_disposal_r_1 = data["cost_FP_geologic"] * m_fp_reprocessed_r * np.exp(
        data["discount_rate"] * data["lead_time_FP_disposal"]
    )
    pv_ru_geol_disposal_r_1 = data["cost_RU_disposal"] * m_reprocessed_r * data["frac_RU_discarded"] * np.exp(
        data["discount_rate"] * data["lead_time_FP_disposal"]
    )

    pv_front_end_r_1 = pv_reprocessing_r_1 + pv_enrichment_r_1 + pv_conversion_r_1 + pv_deconversion_r_1 + pv_nu_r_1 + pv_th_r_1 + pv_fabrication_r_1 + pv_fp_conditioning_r_1 + pv_fp_geol_disposal_r_1 + pv_ru_geol_disposal_r_1

    # Below are generated only for future use
    reproc_frac_r_front_end = pv_reprocessing_r_1 / pv_front_end_r_1
    enrichment_frac_r_front_end = pv_enrichment_r_1 / pv_front_end_r_1
    conversion_frac_r_front_end = pv_conversion_r_1 / pv_front_end_r_1
    deconversion_frac_r_front_end = pv_deconversion_r_1 / pv_front_end_r_1
    nu_frac_r_front_end = pv_nu_r_1 / pv_front_end_r_1
    th_frac_r_front_end = pv_th_r_1 / pv_front_end_r_1
    fab_frac_r_front_end = pv_fabrication_r_1 / pv_front_end_r_1
    fp_cond_frac_r_front_end = pv_fp_conditioning_r_1 / pv_front_end_r_1
    fp_disp_frac_r_front_end = pv_fp_geol_disposal_r_1 / pv_front_end_r_1
    ru_disp_frac_r_front_end = pv_ru_geol_disposal_r_1 / pv_front_end_r_1

    return pv_front_end_r_1


def scale_up(
    data: pd.DataFrame, t_plant, lev_factor, e_year, pv_front_end_u_1: pd.Series,
    pv_front_end_r_1: pd.Series, n_cycl: np.ndarray, t_cyc: np.ndarray
):
    """Scale up the front-end costs of the nuclear fuel cycle to the total operational time of the plant.
    This function computes the levelized front-end costs based on the input data and parameters.
    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing the parameters related to the nuclear fuel cycle.
    t_plant : float
        The total operational time of the plant in years.
    lev_factor : float
        The leveling factor for the discount rate.
    e_year : float
        The total energy produced by the plant in a year.
    pv_front_end_u_1 : pd.Series
        Present value of the front-end costs for the first route (natural uranium).
    pv_front_end_r_1 : pd.Series
        Present value of the front-end costs for the second route (reprocessed uranium).
    n_cycl : np.ndarray
        Array containing the number of cycles for each batch.
    t_cyc : np.ndarray
        Array containing the cycle time for each batch.
    Returns
    -------
    levelized_front_end : pd.Series
        Series containing the levelized front-end costs.
    """

    # ----------------- Scale up from 1 kg to total dollars per batch (mass_hm_core in gHM, so /1000 to get kgHM)
    # only front-end route 1 and 2 - route 3 (same island recycling is counted in the back-end
    pv_front_end_tot = pv_front_end_u_1 * data["frac_core_loaded_nat"] + pv_front_end_r_1 * data[
        "frac_core_loaded_reprcsd"]
    pv_front_end = pv_front_end_tot * (data["HM_mass_direct_spec"] / 1000 / data["num_batches"])
    #  present value of the entire front end fuel cycle costs for all batches throughout the core lifetime
    pv_front_end_o = pv_front_end.copy(deep=True)

    # TODO: Should the `np.arange(...)` start at 1?
    # k = n_cycl - 1
    indices = np.arange(1,np.max(n_cycl))  # Generate an array of indices from 0 to N-1
    m = np.where(indices < n_cycl[:, np.newaxis], indices, 0)  # Apply the mask to fill the matrix
    # We used -np.inf to define `matrix` above so that those values become zero after exponentiating,
    # and so the sum will not be affected by those values. If we used 0 instead of -inf, those values
    # would become 1 after exponentiation, which would be added in the sum.
    pv_front_end *= (1 + np.exp(
        (data["escalation_rate_front"] - data["discount_rate"]).values.reshape(-1, 1) * m * t_cyc.reshape(-1, 1)
    ).sum(axis=1))
    # as above, but this is the residual of the last cycle, in percent over the cycle (~ 15 #)
    # Not realistic because of transportation costs (James of Exelon): only the fraction of t_cyc
    # utilized is a cost, while the rest is sold.
    pv_front_end += (pv_front_end_o * np.exp(
        (data["escalation_rate_front"] - data["discount_rate"]) * n_cycl * t_cyc
    )) * (t_plant - (n_cycl * t_cyc)) / t_cyc

    levelized_front_end = pv_front_end * lev_factor * 1000 / e_year
    fcc_front_end_u_frac = pv_front_end_u_1 * data["frac_core_loaded_nat"] / pv_front_end_tot
    fcc_front_end_r_frac = pv_front_end_r_1 * data["frac_core_loaded_reprcsd"] / pv_front_end_tot

    return levelized_front_end
