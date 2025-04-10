import numpy as np
import pandas as pd

from .backend import backend
from .costs import capital_cost, levelized_om_cost
from .frontend import front_end_1, front_end_2, scale_up
from .function1 import function_1
from .monte_carlo_sampler import generate_monte_carlo_samples


class NECost:
    def __init__(
        self,
        data: pd.DataFrame,
        is_new_plant: bool,
        is_new_fuel: bool,
        add_turb: bool,
        om_frac: float,
        t_plant: int,
        fuel_diam_ref: float,
        assembly_ref: int,
        ref_burnup: float,
        fuel_density_ref: float,
        weight_hm_ref: float,
        l_h_ref: float,
        batches_ref: float,
        pv_sg_ref: float,
        m_sg: float,
        pv_head_ref: float,
        pv_internals_ref: float,
        pv_turb_ref: float,
        m_turb: float
    ):
        self.data = data

        self.is_new_plant = is_new_plant
        self.is_new_fuel = is_new_fuel
        self.add_turb = add_turb
        self.om_frac = om_frac
        self.t_plant = t_plant
        self.fuel_diam_ref = fuel_diam_ref
        self.assembly_ref = assembly_ref
        self.ref_burnup = ref_burnup
        self.fuel_density_ref = fuel_density_ref
        self.weight_hm_ref = weight_hm_ref
        self.l_h_ref = l_h_ref
        self.batches_ref = batches_ref
        self.pv_sg_ref = pv_sg_ref
        self.m_sg = m_sg
        self.pv_head_ref = pv_head_ref
        self.pv_internals_ref = pv_internals_ref
        self.pv_turb_ref = pv_turb_ref
        self.m_turb = m_turb
        self.number_rods_ref = assembly_ref * 264

        # Modifications to the values in the Monte Carlo samples
        self.core_power = self.data["core_pwr_func_ref"] * self.data["ref_therm_pwr"]
        self.nrods_core = self.data["num_ass"] * self.data["num_pins"]
        self.data["HM_mass_direct_spec"] *= 1e6
        self.data["outage_ref"] /= 365.25
        self.data["outage_refuel"] /= 365.25
        self.data["outage_cooldown_heatup"] /= 365.25
        self.data["forced_outage_rate_ref"] /= 100
        self.data["forced_outage_rate"] /= 100
        self.data["refuel_outage_cost"] *= self.om_frac
        self.data["forced_outage_cost"] *= self.om_frac
        self.data["num_personnel"] *= self.om_frac
        self.data["nrchmt_fresh"] /= 100
        self.data["feed_nrchmt_fresh"] /= 100
        self.data["tails_nrchmt_fresh"] /= 100
        self.data["fab_loss_percent"] /= 100
        self.data["conv_loss_percent"] /= 100
        self.data["rprocsng_loss_percent"] /= 100
        self.data["nrchmt_lvl_product_rec"] /= 100
        self.data["nrchmt_lvl_tails_rec"] /= 100
        self.data["nrchmt_lvl_feed_rec"] /= 100
        self.data["outage_duration_uprates"] *= 30.48

    def run(self):
        self.data["HM_mass_direct_spec"].mask(
            cond=self.data["HM_mass_direct_spec"] <= 0,
            other=self.nrods_core * self.data["ass_length"] * np.pi * (self.data["fuel_D"] / 2) ** 2 * (
                self.data["fuel_density"] * self.data["HM_weight_percent"]),
            inplace=True
        )
        # reference core specific power W/gHM.
        mass_hm_core_ref = self.number_rods_ref * self.l_h_ref * np.pi * (
            self.fuel_diam_ref / 2) ** 2 * (self.fuel_density_ref * self.weight_hm_ref)
        q_sp_ref = self.data["ref_therm_pwr"] / mass_hm_core_ref
        q_sp = self.core_power / self.data["HM_mass_direct_spec"]  # based on whole core -  W/gHM.
        efpy_ref = (self.ref_burnup * (1000 / 365.25)) / q_sp_ref  # for reference core [y]
        efpy = (self.data["max_burnup"] * (1000 / 365.25)) / q_sp  # EFPY at total discharge burnup [years]

        # --------------------------------  Interest rate-related parameters
        lev_factor = self.data["discount_rate"] / (1 - np.exp(-self.data["discount_rate"] * self.t_plant))
        e_year = self.core_power * self.data["therm_efficiency"]/100 * (self.data["L_direct_spec"] / 1000) * 8766

        l_inp, n_cycl, t_cyc, planned_outage = function_1(self.data, self.batches_ref, self.t_plant, efpy, efpy_ref)
        m_fabrication, m_enrichment, pv_front_end_u_1 = front_end_1(self.data)
        pv_front_end_r_1 = front_end_2(self.data)
        levelized_front_end = scale_up(
            self.data,
            self.t_plant,
            lev_factor,
            e_year,
            pv_front_end_u_1,
            pv_front_end_r_1,
            n_cycl,
            t_cyc
        )
        levelized_back_end = backend(self.data, self.t_plant, lev_factor, e_year, n_cycl, t_cyc)
        levelized_fcc = levelized_front_end + levelized_back_end
        levelized_hydride_om = levelized_om_cost(
            self.data,
            self.t_plant,
            self.core_power,
            lev_factor,
            e_year,
            l_inp,
            t_cyc,
            planned_outage
        )
        # --------------------------------  capital costs
        levelized_hydride_cap, levelized_hydride_cost = capital_cost(
            self.data,
            self.is_new_plant,
            self.is_new_fuel,
            self.add_turb,
            self.pv_turb_ref,
            self.m_turb,
            self.m_sg,
            self.pv_sg_ref,
            self.pv_head_ref,
            self.pv_internals_ref,
            self.assembly_ref,
            self.core_power,
            self.nrods_core,
            lev_factor,
            e_year,
            levelized_fcc,
            levelized_hydride_om,
            m_enrichment,
            m_fabrication,
            t_cyc
        )

        return pd.DataFrame(
            {
                "Capital": levelized_hydride_cap,
                "LCOE": levelized_hydride_cost,
                "O&M": levelized_hydride_om,
                "FCC": levelized_fcc,
                "HM_mass_direct_spec": self.data['HM_mass_direct_spec'] / 1e6,
                "t_cyc": t_cyc * 365.25 / 30.48,
                "L_direct_spec": self.data['L_direct_spec'] * 100
            }
        )
