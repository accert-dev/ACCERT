import numpy as np

try:
    from .Algorithm import Algorithm
except Exception:
    class Algorithm:
        def __init__(self, ind=None, alg_name=None, alg_for=None, alg_description=None, alg_formulation=None, alg_units=None, variables=None, constants=None):
            self.ind = ind
            self.name = alg_name
            self.alg_for = alg_for
            self.alg_description = alg_description
            self.alg_formulation = alg_formulation
            self.alg_units = alg_units
            self.variables = variables or ""
            self.constants = constants


class LPSRDirectCostFunc(Algorithm):
    """ACCERT-style algorithms for the LPSR direct-cost table.

    Cost elements use category_scale(ref, scale, optional multipliers).
    Scale variables use named scale-law or direct-formula methods grouped by scale basis.
    """

    def __init__(self, ind=None, alg_name=None, alg_for=None, alg_description=None, alg_formulation=None, alg_units=None, variables=None, constants=None):
        super().__init__(ind, alg_name, alg_for, alg_description, alg_formulation, alg_units, variables, constants)

    def run(self, inputs: dict) -> float:
        values = [inputs[var.strip()] for var in self.variables.split(",") if var.strip()]
        return self._run_algorithm(self.name, values)

    def _run_algorithm(self, alg_name: str, values: list) -> float:
        method = alg_name.strip()
        try:
            algorithm = getattr(self, method)
        except AttributeError as exc:
            raise ValueError(f"Algorithm {alg_name} not found in LPSRDirectCostFunc") from exc
        return algorithm(*values)

    @staticmethod
    def category_scale(*values):
        result = 1.0
        for value in values:
            result *= value
        return result

    @staticmethod
    def _scale_law(*values):
        x_unit_value, eedb_base_unit_value, exp = values
        if eedb_base_unit_value == 0:
            return 0.0
        return np.power(x_unit_value / eedb_base_unit_value, exp)

    @staticmethod
    def _formula_scale(*values):
        uc_coef, x_unit_value, ref_cost = values
        if ref_cost == 0:
            return 0.0
        return uc_coef * x_unit_value / ref_cost

    @staticmethod
    def cal_sup_str_S(*values):
        D, H = values
        return np.pi * np.power(D, 2) / 2 + np.pi * D * H

    @staticmethod
    def formula_scale_flow_rate(*values):
        return LPSRDirectCostFunc._formula_scale(*values)

    @staticmethod
    def formula_scale_fuel_cask_capacity(*values):
        return LPSRDirectCostFunc._formula_scale(*values)

    @staticmethod
    def formula_scale_fuel_crane_capacity(*values):
        return LPSRDirectCostFunc._formula_scale(*values)

    @staticmethod
    def formula_scale_ht_surface_S(*values):
        return LPSRDirectCostFunc._formula_scale(*values)

    @staticmethod
    def formula_scale_pressurizer_mass(*values):
        return LPSRDirectCostFunc._formula_scale(*values)

    @staticmethod
    def formula_scale_surface_S(*values):
        return LPSRDirectCostFunc._formula_scale(*values)

    @staticmethod
    def formula_scale_surface_S_9_71886e_06(*values):
        return LPSRDirectCostFunc._formula_scale(*values)

    @staticmethod
    def formula_scale_vessel_mass(*values):
        return LPSRDirectCostFunc._formula_scale(*values)

    @staticmethod
    def scale_law_admin_bldg(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_bldg_V(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_containment(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_control_dg_bldg(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_elec_P(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_electrical_bldg(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_flow_rate(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_fuel_storage(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_heat_rejection(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_piping_mass(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_plant_power(*values):
        return LPSRDirectCostFunc._scale_law(*values)


    @staticmethod
    def scale_law_power(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_primary_aux_bldg(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_reactor_bldg(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_reactor_equipment(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_site_S(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_turbine_bldg(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_turbine_equipment(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_V_of_212_213_215_216_217(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_waste_bldg(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_wastewater_bldg(*values):
        return LPSRDirectCostFunc._scale_law(*values)

    @staticmethod
    def scale_law_yardwork(*values):
        return LPSRDirectCostFunc._scale_law(*values)


    @staticmethod
    def sum_all(*values):
        return sum(values)

