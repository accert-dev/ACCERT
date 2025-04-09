import numpy as np
import pandas as pd


def levelized_om_cost(
    data: pd.DataFrame,
    t_plant,
    core_power: pd.Series,
    lev_factor,
    e_year,
    l_inp: np.ndarray,
    t_cyc: np.ndarray,
    planned_outage: np.ndarray
):
    """Calculate the levelized O&M cost of the nuclear power plant.
    The O&M cost includes the costs associated with the operation and maintenance of the plant,
    including fixed and variable costs, personnel costs, and other related expenses.
    The function takes into account the number of cycles, cycle time, and other parameters
    related to the nuclear power plant's operation.
    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing the parameters related to the nuclear power plant.
    t_plant : float
        The total operational time of the plant in years.
    core_power : pd.Series
        The core power of the plant in MW.
    lev_factor : float
        The leveling factor for the discount rate.
    e_year : float
        The total energy produced by the plant in a year.
    l_inp : np.ndarray
        Array containing the number of cycles for each batch.
    t_cyc : np.ndarray
        Array containing the cycle time for each batch.
    planned_outage : np.ndarray
        Array containing the planned outage time for each batch.
    Returns
    -------
    levelized_hydride_om: pd.DataFrame
        DataFrame containing the levelized O&M cost of the nuclear power plant.
    """
    o_m_fixed = data["OM_fixed_cost"].mask(data["OM_fixed_cost"] <= 0, 0)

    if ((data["OM_fixed_cost"] <= 0) & (l_inp == 1)).any():
        print("Execution will terminate with an error:")
        print("The values necessary to calculate O&M costs have not been obtained because L was not calculated")
        # TODO: Should we throw an exception here?
        return None

    cf_ro = (planned_outage * 365.25 * data["refuel_outage_cost"]) / t_cyc  # refueling outage unit cost ($/year)
    # Note: forced outages occur only during operation, or t_cyc-planned_outage, not with the reactor down for refueling
    t_fo = data["forced_outage_rate"] * (t_cyc - planned_outage)  # forced outage length/cycle (years)
    cf_fo = (t_fo * 365.25 * (
        data["forced_outage_cost"] + data["cost_replacement"])) / t_cyc  # forced outage unit cost ($/year)
    cf_pers = data["num_personnel"] * data["personnel_cost"]  # personnel unit cost ($/year)

    pv_om = np.where(
        data["OM_fixed_cost"] <= 0,
        cf_ro + cf_fo + cf_pers,
        data["OM_direct_spec"] * (core_power / 1000) * data["therm_efficiency"]/100
    )
    # PV of O&M costs at t = 1 year ($).
    # TODO: Should the `np.arange(...)` start at 1?
    q, _ = np.meshgrid(np.arange(1, t_plant ), range(len(data)))
    epsilon = np.exp((data["escalation_rate_OM"] - data["discount_rate"]).values.reshape(-1, 1) * q)
    pv_om = pv_om * (1 + epsilon.sum(axis=1))
    # Total PV of O & M costs at t = 0 year ($)
    pv_om = pv_om * np.exp(-data["discount_rate"] * 1)
    # levelized O & M cost over life of plant ($/year)
    levelized_om_total = pv_om * lev_factor

    # levelized O & M unit cost over life of plant (mills/kW-hre)
    levelized_hydride_om = levelized_om_total * 1000 / e_year + o_m_fixed
    return levelized_hydride_om


def compute_pv_cap(
    data: pd.DataFrame,
    is_new_plant: bool,
    is_new_fuel: bool,
    add_turb: bool,
    pv_turb_ref,
    m_turb,
    m_sg,
    pv_sg_ref,
    pv_head_ref,
    pv_internals_ref,
    core_power: pd.Series,
):
    """Compute the present value of capital costs for a nuclear power plant.
    The function takes into account the type of plant (new or existing), the type of fuel,
    and the type of turbine used in the plant. It calculates the present value of capital costs
    based on the reference values provided in the data DataFrame.
    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing the parameters related to the nuclear power plant.
    is_new_plant : bool
        Indicates whether the plant is new or an upgrade of an existing plant.
    is_new_fuel : bool
        Indicates whether the fuel is new or existing.
    add_turb : bool
        Indicates whether to add a turbine or not.
    pv_turb_ref : float
        Reference value for the turbine present value.
    m_turb : float
        Turbine scaling factor.
    m_sg : float
        Steam generator scaling factor.
    pv_sg_ref : float
        Reference value for the steam generator present value.
    pv_head_ref : float
        Reference value for the head present value.
    pv_internals_ref : float
        Reference value for the internals present value.
    core_power : pd.Series
        The core power of the plant in MW.
    Returns
    -------
    pv_cap : pd.Series 
        Present value of capital costs for the nuclear power plant.
    """
    # NOTE: This function is partially vectorized.
    if is_new_plant:
        interest_rate_constrct = data["interest_rate_constrct"].values
        constrct_years = data["constrct_years"].values
        capital_cost_vals = data["capital_cost"].values
        ref_therm_pwr = data["ref_therm_pwr"].values
        therm_efficiency = data["therm_efficiency"].values/100
        escalation_cost_pwr = data["escalation_cost_pwr"].values
        apr_r_constr = (1 + interest_rate_constrct / 4) ** 4 - 1

        # To compute the `q_cost_no_interest` outside the loop, we must use this masking
        # technique since `constrct_years` may have different values, leading to different
        # lengths for the `q_cost_no_interest` matrix.
        indices = np.arange(0, np.max(constrct_years+0.25), 0.25)  # Generate an array of indices
        m = np.where(indices < constrct_years[:, np.newaxis]+0.25, indices, np.nan)  # Apply the mask to fill the matrix
        x_constr = -np.pi / 2 + np.pi * (m / constrct_years.reshape(-1, 1))
        s_curve_cum = 0.5 * (np.sin(x_constr) + 1)
        s_curve_diff = np.diff(s_curve_cum)
        q_cost_no_interest = s_curve_diff * capital_cost_vals.reshape(-1, 1)

        # We use a loop here since this part of the code is difficult to vectorize. However, we
        # extract the numpy arrays to minimize the overhead costs of accessing values from Pandas.
        tot_capital_cost = np.empty(len(data))  # --> populated by the loop
        for idx in range(len(interest_rate_constrct)):
            # Select the correct values for the current computation. Values outside the slice are NaN.
            current_q_cost_no_interest = q_cost_no_interest[idx, :(int(constrct_years[idx] / 0.25) )]

            tot_capital_cost[idx] = current_q_cost_no_interest @ np.full(len(current_q_cost_no_interest), (
                1 + apr_r_constr[idx] / 4)) ** (np.arange(constrct_years[idx] * 4, 0, -1) - 0.5)
        # If cap cost exp is 1 ==> ref_therm_pwr cancels out and only core_power is used
        pv_cap = tot_capital_cost * ref_therm_pwr / 1000 * therm_efficiency * (
            core_power / ref_therm_pwr) ** escalation_cost_pwr
    else:  # Or upgrade of an existing plant
        sub_ref_pwr = data["ref_therm_pwr"] if add_turb else 0
        pv_turb_scaled = pv_turb_ref * ((core_power - sub_ref_pwr) / data["ref_therm_pwr"]) ** m_turb

        pv_cap = np.where(
            core_power > data["ref_therm_pwr"],

            # Turbine is treated before: can be added or replaced
            pv_turb_scaled + pv_sg_ref * (core_power / data["ref_therm_pwr"]) ** m_sg + pv_head_ref + pv_internals_ref +
            data["outage_duration_uprates"] * data["cost_replacement"],

            # Again, present value of discarded fuel is a cost that needs to be recovered through COE
            0 if not is_new_fuel else pv_head_ref + pv_internals_ref + data["outage_duration_uprates"] * data[
                "cost_replacement"
            ]
        )

    return pv_cap


def capital_cost(
    data: pd.DataFrame,
    is_new_plant: bool,
    is_new_fuel: bool,
    add_turb: bool,
    pv_turb_ref,
    m_turb,
    m_sg,
    pv_sg_ref,
    pv_head_ref,
    pv_internals_ref,
    assembly_ref,
    core_power: pd.Series,
    nrods_core: pd.Series,
    lev_factor: pd.Series,
    e_year: pd.Series,
    levelized_fcc: pd.Series,
    levelized_hydride_om: pd.Series,
    m_enrichment: pd.Series,
    m_fabrication: pd.Series,
    t_cyc: np.ndarray
):
    """Calculate the levelized capital cost of the nuclear power plant.
    The capital cost includes the costs associated with the construction and commissioning
    of the plant, including the costs of the reactor, turbine, and other components.
    The function takes into account the type of plant (new or existing), the type of fuel,
    and the type of turbine used in the plant. It calculates the levelized capital cost
    based on the reference values provided in the data DataFrame.
    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing the parameters related to the nuclear power plant.
    is_new_plant : bool
        Indicates whether the plant is new or an upgrade of an existing plant.
    is_new_fuel : bool
        Indicates whether the fuel is new or existing.
    add_turb : bool
        Indicates whether to add a turbine or not.
    pv_turb_ref : float
        Reference value for the turbine present value.
    m_turb : float
        Turbine scaling factor.
    m_sg : float
        Steam generator scaling factor.
    pv_sg_ref : float
        Reference value for the steam generator present value.
    pv_head_ref : float
        Reference value for the head present value.
    pv_internals_ref : float
        Reference value for the internals present value.
    assembly_ref : float
        Reference value for the assembly present value.
    core_power : pd.Series
        The core power of the plant in MW.
    nrods_core : pd.Series
        The number of rods in the core.
    lev_factor : pd.Series
        The leveling factor for the discount rate.
    e_year : pd.Series
        The total energy produced by the plant in a year.
    levelized_fcc : pd.Series
        The levelized front-end cost of the nuclear power plant.
    levelized_hydride_om : pd.Series
        The levelized O&M cost of the nuclear power plant.
    m_enrichment : pd.Series
        The mass of enrichment used in the plant.
    m_fabrication : pd.Series
        The mass of fabrication used in the plant.
    t_cyc : np.ndarray
        Array containing the cycle time for each batch.
    Returns
    -------
    levelized_hydride_cap: pd.Series
        The levelized capital cost of the nuclear power plant.
    levelized_hydride_cost: pd.Series
        The total levelized cost of the nuclear power plant.
    """
    # NOTE: This function call is not vectorized
    pv_cap = compute_pv_cap(
        data,
        is_new_plant,
        is_new_fuel,
        add_turb,
        pv_turb_ref,
        m_turb,
        m_sg,
        pv_sg_ref,
        pv_head_ref,
        pv_internals_ref,
        core_power
    )

    levelized_cap_annual = pv_cap * lev_factor  # ($/year)
    levelized_hydride_cap = levelized_cap_annual * 1000 / e_year  # (mills/kW-hre)

    # --------------------------------  waste costs
    # Total PV of waste disposal ($)
    pv_disposal = (data["waste_disposal_fee"] / 1000) * e_year / lev_factor

    # --------------------------------  totals
    # Tot. level. COE (mills/kW-hre)
    levelized_hydride_cost = levelized_fcc + levelized_hydride_om + levelized_hydride_cap

    # --------------------------------  other data
    # uranium consumption (kg-HM/GW-hre)
    uranium_consumption_hydride = (data["HM_mass_direct_spec"] * (1 / data["num_batches"])) * (1 / t_cyc) * (
        1 / e_year) * (1 / (1 - data["fab_loss_percent"])) * m_enrichment / m_fabrication * (
                                      1 / (1 - data["conv_loss_percent"])) * 1e6
    # assemblies disposed (assemblies/GW-hre)
    assembly_disposal_hydride = (nrods_core * (1 / data["num_batches"])) * (1 / t_cyc) * (
        1 / e_year) * (1 / assembly_ref) * 1e6

    return levelized_hydride_cap, levelized_hydride_cost
