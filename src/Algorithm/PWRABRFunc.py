import numpy as np
from .Algorithm import Algorithm


ALGORITHM_ALIASES = {
    'dome_inside_diameter ': 'dome_inside_diameter',
    'building_internal _surface': 'building_internal_surface',
    'volume_of_the_structures ': 'volume_of_the_structures',
}


class PWRABRFunc(Algorithm):
    """Python implementations of the ACCERT reference algorithms."""

    def __init__(self, ind, alg_name, alg_for, alg_description, alg_formulation, alg_units, variables, constants):
        super().__init__(ind, alg_name, alg_for, alg_description, alg_formulation, alg_units, variables, constants)

    def run(self, inputs: dict) -> float:
        values = [inputs[var.strip()] for var in self.variables.split(",") if var.strip()]
        return self._run_algorithm(self.name, values)

    def _run_algorithm(self, alg_name: str, values: list) -> float:
        method = ALGORITHM_ALIASES.get(alg_name, alg_name.strip())
        try:
            algorithm = getattr(self, method)
        except AttributeError as exc:
            raise ValueError(f"Algorithm {alg_name} not found") from exc
        return algorithm(*values)

    @staticmethod
    def sum_multi_accounts(*values):
        return sum(values)

    @staticmethod
    def sum_multi_weights(*values):
        return sum(values)

    @staticmethod
    def sum_multi_pumps(*values):
        return sum(values)

    @staticmethod
    def ptn_account(*values):
        v_1, v_2 = values
        return v_1*v_2

    @staticmethod
    def unit_weights(*values):
        v_1, v_2 = values
        return v_1*0.14+v_2*0.31

    @staticmethod
    def pump(*values):
        v_1, v_2, v_3, v_4 = values
        return v_1*np.power((v_2/v_3),v_4)

    @staticmethod
    def containment(*values):
        v_1, = values
        return v_1/1000000

    @staticmethod
    def MWth_scale(*values):
        v_1, v_2, v_3 = values
        return v_1*np.power((v_2/3431),v_3)

    @staticmethod
    def unit_volume(*values):
        v_1, v_2 = values
        return v_1*v_2/1000000

    @staticmethod
    def dev_factor_ref(*values):
        v_1, v_2, v_3 = values
        return v_1*v_2/v_3

    @staticmethod
    def tur_exp_n(*values):
        v_1, = values
        return (-0.0032) *v_1+ 1.2497

    @staticmethod
    def esc_1987(*values):
        v_1, v_2 = values
        return v_1*v_2

    @staticmethod
    def cost_by_weight(*values):
        v_1, v_2 = values
        return v_1*v_2

    @staticmethod
    def default_0(*values):
        return 0

    @staticmethod
    def rpv_mass(*values):
        v_1, v_2 = values
        return v_1+v_2

    @staticmethod
    def unit_facility(*values):
        v_1, v_2 = values
        return v_1*v_2

    @staticmethod
    def MWe_scale(*values):
        v_1, v_2, v_3 = values
        return v_1*np.power((v_2/1144),v_3)

    @staticmethod
    def unit_weights_plate(*values):
        v_1, v_2 = values
        return v_1*0.075+v_2*0.31

    @staticmethod
    def esc_1978(*values):
        v_1, v_2 = values
        return v_1*v_2

    @staticmethod
    def total_weight_prn(*values):
        v_1, v_2, v_3, v_4 = values
        return v_1*(v_2*0.075+v_3*0.31)*v_4

    @staticmethod
    def unit_weights_factor(*values):
        v_1, v_2, v_3 = values
        return (v_1*0.075+v_2*0.31)*v_3

    @staticmethod
    def factor_sum(*values):
        v_1, v_2, v_3, v_4 = values
        return v_1 * v_2 * (v_3 + v_4)

    @staticmethod
    def complex(*values):
        v_1, = values
        return v_1

    @staticmethod
    def MWth_lmfbrscale(*values):
        v_1, v_2, v_3 = values
        return v_1*np.power((v_2/2287),v_3)

    @staticmethod
    def MWreth_scale(*values):
        v_1, v_2, v_3 = values
        return v_1*np.power((v_2/3800),v_3)

    @staticmethod
    def Sgsum(*values):
        v_1, v_2, v_3 = values
        return v_1*v_2*v_3

    @staticmethod
    def containmentsum(*values):
        raise NotImplementedError("Algorithm containmentsum is not implemented")

    @staticmethod
    def inside_rad(*values):
        v_1, v_2 = values
        return v_1-v_2

    @staticmethod
    def round_surface(*values):
        v_1, = values
        return np.pi*np.power(v_1,2)

    @staticmethod
    def basemat_volume(*values):
        v_1, v_2 = values
        return v_1*v_2

    @staticmethod
    def wall_height(*values):
        v_1, v_2 = values
        return v_1-v_2

    @staticmethod
    def walls_surface(*values):
        v_1, v_2, v_3 = values
        return v_1*2*np.pi*(v_2+v_3)

    @staticmethod
    def wall_volume(*values):
        v_1, v_2, v_3 = values
        return v_1*np.pi*(np.power(v_2,2)-np.power(v_3,2))

    @staticmethod
    def dome_inside_diameter(*values):
        v_1, v_2 = values
        return v_1-v_2

    @staticmethod
    def roof_surface(*values):
        v_1, v_2 = values
        return 0.5*4*np.pi*(np.power(v_1,2)+np.power(v_2,2))

    @staticmethod
    def roof_volume(*values):
        v_1, v_2 = values
        return 0.5*4/3*np.pi*(np.power(v_1,3)-np.power(v_2,3))

    @staticmethod
    def tot_internal_volume(*values):
        v_1, v_2, v_3 = values
        return (np.pi*np.power(v_1,2)*v_2)+(0.5*(4/3)*np.pi*np.power(v_3,3))

    @staticmethod
    def building_internal_volume(*values):
        v_1, v_2 = values
        return v_1*(1-v_2)

    @staticmethod
    def building_internal_surface(*values):
        v_1, v_2 = values
        return 2*v_1/v_2

    @staticmethod
    def volume_of_the_structures(*values):
        v_1, v_2, v_3, v_4 = values
        return v_1+v_2+v_3+v_4

    @staticmethod
    def Inside_liner_surface(*values):
        v_1, v_2, v_3 = values
        return (np.power(v_1,2)*np.pi)+(v_2*2*np.pi*v_1)+(0.5*4*np.pi*np.power(v_3,2))

    @staticmethod
    def liner_Surface(*values):
        v_1, v_2 = values
        return v_1*v_2

    @staticmethod
    def painted_surface(*values):
        v_1, v_2, v_3, v_4 = values
        return v_1+(v_2*2*np.pi*v_3)+(0.5*4*np.pi*np.power(v_3,2))+v_4

    @staticmethod
    def Inflation_rate(*values):
        v_1, = values
        return (1.03 ** (1996 - 1987)) * v_1

    @staticmethod
    def unitcost_v_eedb_to_accert(*values):
        v_1, v_2 = values
        return v_1*v_2

    @staticmethod
    def unitcost_s_eedb_to_accert(*values):
        v_1, v_2 = values
        return v_1*v_2

    @staticmethod
    def tol_contaiment_ce_cost(*values):
        v_1, v_2 = values
        return v_1*v_2

    @staticmethod
    def sum_ce(*values):
        return sum(values)

    @staticmethod
    def Yardwork_cost(*values):
        v_1, = values
        return 81.5*v_1

    @staticmethod
    def Reactor_containment_mat_cost(*values):
        v_1, = values
        return 130.8*v_1

    @staticmethod
    def Reactor_containment_lab_cost(*values):
        v_1, = values
        return 915.6*v_1

    @staticmethod
    def Building_and_utilities_mat_cost(*values):
        v_1, = values
        return 6458.3*v_1

    @staticmethod
    def Building_and_utilities_lab_cost(*values):
        v_1, v_2 = values
        return 9843*v_1+10000*v_2

    @staticmethod
    def Reactor_startup_facility_cost(*values):
        v_1, = values
        return 7600*v_1+1100

    @staticmethod
    def Outer_vessel_mat_cost(*values):
        v_1, = values
        return 310000*v_1

    @staticmethod
    def Outer_vessel_lab_cost(*values):
        v_1, = values
        return 14080*v_1

    @staticmethod
    def Inner_vessel_cost(*values):
        v_1, = values
        return 310000*v_1

    @staticmethod
    def Reactivity_control_system_cost(*values):
        v_1, v_2, v_3 = values
        return 950*v_1+610000*(v_2+v_3)

    @staticmethod
    def Reflector_cost(*values):
        v_1, v_2, v_3 = values
        return 310000*v_1+120000*v_2+1000000*v_3

    @staticmethod
    def Shield_cost(*values):
        v_1, = values
        return 949.9*v_1

    @staticmethod
    def Moderator_cost(*values):
        v_1, = values
        return 310000*v_1

    @staticmethod
    def cooling_heat_pipes_cost(*values):
        v_1, v_2 = values
        return 10000*v_1*(1-v_2)

    @staticmethod
    def heat_exchangers_mat_cost(*values):
        v_1, = values
        return 50000*v_1

    @staticmethod
    def heat_exchangers_lab_cost(*values):
        v_1, = values
        return 530000*v_1

    @staticmethod
    def heat_exchangers_fac_cost(*values):
        v_1, v_2 = values
        return 120000*v_1*v_2

    @staticmethod
    def instrumentation_contorl_cost(*values):
        v_1, = values
        return 2000*v_1+6500000

    @staticmethod
    def turb_and_elec_sys_cost(*values):
        v_1, v_2 = values
        return 282553*v_1+213800000*(pow(v_2/1144, 0.4) + pow(v_1/3431, 0.8))
