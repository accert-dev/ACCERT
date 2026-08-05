import numpy as np
import math
import inspect
from .Algorithm import Algorithm

### MNyberg TEAm-based Mirror algorithms based on Tokamak/Ste examples
class MirrorFunc(Algorithm):

    # Physical constants
    E_DT = 17.59e6 * 1.60218*10**-19 # J
    E_alpha = 3.52e6 * 1.60218*10**-19 # J
    E_n = E_DT - E_alpha # J
    m_T = 3.01604928 * 1.66053907*10**-27 # kg, triton mass
    m_D = 2.01410177811 * 1.66053907*10**-27 # kg, deuteron mass
    m_6Li = 6.0151228874 * 1.66053907*10**-27 # kg, lithium-6 mass

    # Conversion factors
    Wh_to_BTU = 3.41214 # 1 Wh = 3.41214 BTU

    def __init__(self, ind, alg_name, alg_for, alg_description, alg_formulation, alg_units, variables, constants):
        super().__init__(ind, alg_name, alg_for, alg_description, alg_formulation, alg_units, variables, constants)

    def run(self, inputs: dict) -> float:
        """
        Executes the algorithm specified by the name in the instance variables.
        
        Parameters:
        inputs (dict): Dictionary of input variables required for the algorithm.

        Returns:
        float: Result of the algorithm computation.
        """
        if self.name.startswith("Account_"):
            return self._run_account_algorithm(self.name, inputs)
        return self._run_algorithm(self.name, [inputs[var] for var in self.variables.split(",")])

    def _run_account_algorithm(self, alg_name: str, variables: dict) -> float:
        try:
            algorithm = getattr(self, alg_name)
        except AttributeError:
            raise ValueError(f"Algorithm {alg_name} not found")
        parameters = list(inspect.signature(algorithm).parameters)
        if parameters == ["inputs"]:
            return algorithm(variables)
        return algorithm(*[variables[var] for var in parameters])

    def _run_algorithm(self, alg_name: str, variables: list) -> float:
        """
        Runs the specified algorithm with given variables.
        
        Parameters:
        alg_name (str): The name of the algorithm to run.
        variables (list): List of input variables for the algorithm.

        Returns:
        float: Result of the algorithm computation.
        """
        try:
            algorithm = getattr(self, alg_name)
            return algorithm(*variables)
        except AttributeError:
            raise ValueError(f"Algorithm {alg_name} not found")

    @staticmethod
    def cal_P_f_CC(P_f, P_f_EP):
        return P_f - 2 * P_f_EP

    @staticmethod
    def cal_L_CC(P_f_CC, P_f_L):
        return P_f_CC / P_f_L

    @staticmethod
    def cal_L_CF():
        return 1.0

    @staticmethod
    def cal_L(L_CC, L_EP, L_EC):
        return L_CC + 2 * L_EP + 2 * L_EC

    @staticmethod
    def cal_V_vac(L, a_EC):
        return L * np.pi * a_EC**2

    @staticmethod
    def cal_no_vpumps(V_vac, vpump_cap):
        return V_vac / vpump_cap

    @staticmethod
    def cal_cost_factor(n_unit):
        return 0.80 ** (np.log(n_unit) / np.log(2))

    @staticmethod
    def cal_HF_magnet_cost(n_unit, HF_magnet_number, sc_mat_scale):
        return MirrorFunc.HF_magnet_cost(n_unit, HF_magnet_number, sc_mat_scale)

    @staticmethod
    def cal_LF_magnet_cost(n_unit, LF_magnet_number, sc_mat_scale):
        return MirrorFunc.LF_magnet_cost(n_unit, LF_magnet_number, sc_mat_scale)

    @staticmethod
    def cal_CF_magnet_cost(n_unit, CF_magnet_number, sc_mat_scale):
        return MirrorFunc.CF_magnet_cost(n_unit, CF_magnet_number, sc_mat_scale)

    @staticmethod
    def cal_P_alpha(E_DT, E_alpha, P_f):
        return P_f * E_alpha / E_DT

    @staticmethod
    def cal_P_n(P_f, P_alpha):
        return P_f - P_alpha

    @staticmethod
    def cal_P_ine(P_NBI, eta_NBI, P_ICRH, eta_ICRH, P_ECH, eta_ECH):
        return P_NBI / eta_NBI + P_ICRH / eta_ICRH + P_ECH / eta_ECH

    @staticmethod
    def cal_P_pump(f_pump, M_n, P_n):
        return f_pump * M_n * P_n

    @staticmethod
    def cal_P_sub_cont(f_sub, P_f):
        return f_sub * P_f

    @staticmethod
    def cal_P_cryo(f_cryo, P_f):
        return f_cryo * P_f

    @staticmethod
    def cal_P_other(P_pump, P_sub_cont, P_cryo):
        return P_pump + P_sub_cont + P_cryo

    @staticmethod
    def cal_P_in(P_NBI, P_ICRH, P_ECH):
        return P_NBI + P_ICRH + P_ECH

    @staticmethod
    def cal_P_th(M_n, P_n, P_pump, eta_pump):
        return M_n * P_n + eta_pump * P_pump

    @staticmethod
    def cal_P_the(eta_th, P_th):
        return eta_th * P_th

    @staticmethod
    def cal_P_DEC(P_in, P_alpha):
        return P_in + P_alpha

    @staticmethod
    def cal_P_DECe(eta_DEC, P_DEC):
        return eta_DEC * P_DEC

    @staticmethod
    def cal_P_egross(application, P_DECe, P_the):
        if str(application).lower() == "electricity":
            return P_DECe + P_the
        return P_DECe

    @staticmethod
    def cal_P_enet(P_egross, P_ine, P_other):
        return P_egross - (P_ine + P_other)

    @staticmethod
    def cal_f_aux(P_aux, P_egross):
        return P_aux / P_egross

    @staticmethod
    def cal_Q_sci(P_f, P_in):
        return P_f / P_in

    @staticmethod
    def cal_Q_eng(P_egross, P_ine, P_other):
        return P_egross / (P_ine + P_other)

    @staticmethod
    def cal_f_refrac(Q_eng):
        return 1 / Q_eng

    @staticmethod
    def cal_CF_magnet_number(L_CC, L_CF):
        return L_CC / L_CF

    @staticmethod
    def cal_rho_PbLi(T, f_6Li):
        f_6Li_natural = 0.075
        rho_6Li = 460.0
        rho_7Li = 537.0
        T_K = T + 273.15
        rho_PbLi = 10520.35 - 1.19051 * T_K
        return rho_PbLi * (rho_6Li * f_6Li + rho_7Li * (1 - f_6Li)) / (
            rho_6Li * f_6Li_natural + rho_7Li * (1 - f_6Li_natural)
        )

    @staticmethod
    def cal_P_Li(f_6Li):
        if f_6Li == 0.075:
            return 29.53
        if 0.075 <= f_6Li <= 0.975:
            enrichments = [0.075, 0.80, 0.90, 0.95, 0.975]
            prices = [29.53, 2000.0, 4000.0, 8000.0, 16000.0]
            return float(np.interp(f_6Li, enrichments, prices))
        raise ValueError("Lithium pricing at this enrichment level is not supported")

    @staticmethod
    def cal_P_PbLi(Pb_c_raw, P_Li, f_Li):
        return (1 - f_Li) * Pb_c_raw + f_Li * P_Li

    @staticmethod
    def cal_central_cell_cylindrical_part_cost(
        L_CC,
        a_CC,
        vacuum_gap_CC,
        first_wall_thickness,
        vacuum_vessel_thickness,
        multiplier_thickness,
        blanket_thickness,
        blanket_coolant_fraction,
        blanket_structural_fraction,
        outer_vessel_thickness,
        W_rho,
        W_c_raw,
        W_m,
        SS316_rho,
        SS316_c_raw,
        SS316_m,
        Pb_rho,
        Pb_c_raw,
        Pb_m,
        rho_PbLi,
        P_PbLi,
    ):
        return MirrorFunc._central_cell_cylindrical_cost(
            L_CC,
            a_CC,
            vacuum_gap_CC,
            first_wall_thickness,
            vacuum_vessel_thickness,
            multiplier_thickness,
            blanket_thickness,
            blanket_coolant_fraction,
            blanket_structural_fraction,
            outer_vessel_thickness,
            W_rho,
            W_c_raw,
            W_m,
            SS316_rho,
            SS316_c_raw,
            SS316_m,
            Pb_rho,
            Pb_c_raw,
            Pb_m,
            rho_PbLi,
            P_PbLi,
        )

    @staticmethod
    def cal_end_plug_cylindrical_part_cost(
        L_EP,
        a_CC,
        vacuum_gap_CC,
        first_wall_thickness,
        vacuum_vessel_thickness,
        multiplier_thickness,
        blanket_thickness,
        blanket_coolant_fraction,
        blanket_structural_fraction,
        outer_vessel_thickness,
        W_rho,
        W_c_raw,
        W_m,
        SS316_rho,
        SS316_c_raw,
        SS316_m,
        Pb_rho,
        Pb_c_raw,
        Pb_m,
        rho_PbLi,
        P_PbLi,
    ):
        return MirrorFunc._central_cell_cylindrical_cost(
            L_EP,
            a_CC,
            vacuum_gap_CC,
            first_wall_thickness,
            vacuum_vessel_thickness,
            multiplier_thickness,
            blanket_thickness,
            blanket_coolant_fraction,
            blanket_structural_fraction,
            outer_vessel_thickness,
            W_rho,
            W_c_raw,
            W_m,
            SS316_rho,
            SS316_c_raw,
            SS316_m,
            Pb_rho,
            Pb_c_raw,
            Pb_m,
            rho_PbLi,
            P_PbLi,
        )

    @staticmethod
    def _central_cell_cylindrical_cost(
        length,
        a_CC,
        vacuum_gap_CC,
        first_wall_thickness,
        vacuum_vessel_thickness,
        multiplier_thickness,
        blanket_thickness,
        blanket_coolant_fraction,
        blanket_structural_fraction,
        outer_vessel_thickness,
        W_rho,
        W_c_raw,
        W_m,
        SS316_rho,
        SS316_c_raw,
        SS316_m,
        Pb_rho,
        Pb_c_raw,
        Pb_m,
        rho_PbLi,
        P_PbLi,
    ):
        radius = a_CC + vacuum_gap_CC
        total = 0.0

        r_in = radius
        radius += first_wall_thickness
        total += np.pi * length * (radius**2 - r_in**2) * W_rho * W_c_raw * W_m

        r_in = radius
        radius += vacuum_vessel_thickness
        total += np.pi * length * (radius**2 - r_in**2) * SS316_rho * SS316_c_raw * SS316_m

        r_in = radius
        radius += multiplier_thickness
        total += np.pi * length * (radius**2 - r_in**2) * Pb_rho * Pb_c_raw * Pb_m

        r_in = radius
        radius += blanket_thickness
        blanket_volume = np.pi * length * (radius**2 - r_in**2)
        total += blanket_volume * blanket_coolant_fraction * rho_PbLi * P_PbLi
        total += blanket_volume * blanket_structural_fraction * SS316_rho * SS316_c_raw * SS316_m

        r_in = radius
        radius += outer_vessel_thickness
        total += np.pi * length * (radius**2 - r_in**2) * SS316_rho * SS316_c_raw * SS316_m

        return total / 1e6

    @staticmethod
    def cal_expander_cell_cost_result(
        L_EC,
        a_EC,
        expander_cell_vessel_thickness,
        SS316_rho,
        SS316_c_raw,
        SS316_m,
    ):
        vessel_outer_radius = a_EC + expander_cell_vessel_thickness
        vessel_volume = np.pi * L_EC * (vessel_outer_radius**2 - a_EC**2)
        end_cap_volume = np.pi * expander_cell_vessel_thickness * a_EC**2
        return (vessel_volume + 2 * end_cap_volume) * SS316_rho * SS316_c_raw * SS316_m / 1e6

    @staticmethod
    def cal_HF_magnet_shield_cost(
        a_M,
        a_CC_shield,
        a_0,
        length,
        r_gap,
        r_vv,
        r_magnet,
        r_cryostat,
        f_vol,
        length_cc_cylinder,
        length_ep_cylinder,
        r_out_cc,
        r_out_ep,
        W_rho,
        W_c_raw,
        W_m,
    ):
        r_in = a_M + r_gap + r_vv
        r_out = r_magnet - r_cryostat
        v_inner = np.pi * length * (r_out**2 - r_in**2) * f_vol

        r_in_cc = a_CC_shield + r_gap + r_vv
        v_cc_cylinder = np.pi * length_cc_cylinder * (r_out_cc**2 - r_in_cc**2) * f_vol
        v_cc_triangle = np.pi * length_cc_cylinder / 3 * (r_in_cc - r_in) * (r_in + 2 * r_in_cc) * f_vol

        r_in_ep = a_0 + r_gap + r_vv
        v_ep_cylinder = np.pi * length_ep_cylinder * (r_out_ep**2 - r_in_ep**2) * f_vol
        v_ep_triangle = np.pi * length_ep_cylinder / 3 * (r_in_ep - r_in) * (r_in + 2 * r_in_ep) * f_vol

        v_total_cc_facing = v_inner + v_cc_cylinder + v_cc_triangle + v_ep_cylinder + v_ep_triangle
        v_total_ec_facing = v_inner + v_ep_cylinder + v_ep_triangle
        return (v_total_cc_facing + v_total_ec_facing) * W_rho * W_c_raw * W_m / 1e6
    
    ### Account Methods: ###
    
    @staticmethod
    def Account_C21_1(P_egross):
        # Site Preparation/Yard Work
        return(P_egross * 268/1e3)
    
    @staticmethod
    def Account_C21_2(P_egross):
        # Heat Island Building
        return(P_egross * 186.8/1e3)
    
    @staticmethod
    def Account_C21_3(application, P_egross):
        # Turbine Generator Building
        if application.lower()=='electricity':
            return(P_egross * 54.0/1e3)
        else:
            return(0)

    @staticmethod
    def Account_C21_4(P_egross): 
        # Heat Exchanger Building
        return(37.8/1e3 * P_egross)

    @staticmethod
    #21.05.00,,Power supply & energy storage,Concrete & Steel,9.1,9.7,9.7,6.0,560,2019,1.19,
    def Account_C21_5(P_egross): 
        # Power Supply and Energy Storage
        return(10.8/1e3 * P_egross)
    
    @staticmethod
    #21.06.00,,Reactor auxiliaries,Concrete & Steel,4.5,4.8,4.8,3.0,70,2019,1.19,
    def Account_C21_6(P_egross): 
        # Reactor Auxiliaries
        return(5.4/1e3 * P_egross)

    @staticmethod
    #21.07.00,,Hot cell,Concrete & Steel,65.8,24.2,24.2,60,35000,2013,1.42,
    def Account_C21_7(P_egross): 
        # Hot Cell
        return(93.4/1e3 * P_egross)

    @staticmethod
    #21.08.00,,Reactor services,Steel frame,13.2,4.8,4.8,10,233,2013,1.42,
    def Account_C21_8(P_egross): 
        # Reactor Services
        return(18.7/1e3 * P_egross)

    @staticmethod
    #21.09.00,,Service water,Steel frame,0.2,1.3,4.0,4.0,21,2019,1.19,
    def Account_C21_9(P_egross): 
        # Service Water
        return(0.3/1e3 * P_egross)

    @staticmethod
    #21.10.00,,Fuel storage,Steel frame,0.9,5.0,15.0,2.5,188,2019,1.19,
    def Account_C21_10(P_egross):
        # Fuel Storage
        return(1.1/1e3 * P_egross)

    @staticmethod
    #21.11.00,,Control room,Steel frame,0.7,4.0,12.0,2,96,2019,1.19,
    def Account_C21_11(P_egross):
        # Control Room
        return(0.9/1e3 * P_egross)

    @staticmethod
    #21.12.00,,Onsite AC inputs,Steel frame,0.7,3.6,10.8,1.8,70,2019,1.19,
    def Account_C21_12(P_egross):
        # Onsite AC Power
        return(0.8/1e3 * P_egross)

    @staticmethod
    #21.13.00,,Administration,Steel frame,3.7,20.0,60.0,10,12000,2019,1.19,
    def Account_C21_13(P_egross): 
        # Administration
        return(4.4/1e3 * P_egross)

    @staticmethod
    #21.14.00,,Site services,Steel frame,1.3,7.3,22.0,3.7,593,2019,1.19,
    def Account_C21_14(P_egross): 
        # Site Services
        return(1.6/1e3 * P_egross)

    @staticmethod
    #21.15.00,,Cryogenics,Steel frame,2.0,11.0,33.0,5.5,2003,2019,1.19,
    def Account_C21_15(P_egross):
        # Cyrogenics
        return(2.4/1e3 * P_egross)

    @staticmethod
    #21.16.00,,Security,Steel frame,0.7,4.0,12.0,2,96,2019,1.19,
    def Account_C21_16(P_egross): 
        # Security
        return(0.9/1e3 * P_egross)

    @staticmethod
    #21.17.00,,Ventilation stack,Steel cylinder & concrete foundation,22.7,,,120,,2019,1.19,
    def Account_C21_17(P_egross): 
        # Ventilation Stack
        return(27.0/1e3 * P_egross)


    @staticmethod
    def Account_C22_1_1(central_cell_cylindrical_part_cost, end_plug_cylindrical_part_cost, expander_cell_cost_result):
        # First Wall and Blanket (and vacuum vessel)
        return central_cell_cylindrical_part_cost + 2 * end_plug_cylindrical_part_cost + 2 * expander_cell_cost_result

    @staticmethod
    def Account_C22_1_2(HF_magnet_shield_cost):
        # Magnet Radiation Shield
        # Factor of two for each end plug
        return(2 * HF_magnet_shield_cost)

    @staticmethod
    def Account_C22_1_3_1(HF_magnet_number, HF_magnet_cost):
        # HF Coils - Quantity 4
        # 2 per end cell
        # 2 end cells per tandem
        return(HF_magnet_number * HF_magnet_cost)

    @staticmethod
    def Account_C22_1_3_2(LF_magnet_number, LF_magnet_cost):
        # LF Coils - Quantity 8
        # 4 per end cell
        # 2 end cells per tandem
        return(LF_magnet_number * LF_magnet_cost)

    @staticmethod
    def Account_C22_1_3_3(CF_magnet_number, CF_magnet_cost):
        # CF Coils
        # One coil every L_CF m of Central Cell
        return(CF_magnet_number * CF_magnet_cost)

    @staticmethod
    def Account_C22_1_4_1(P_NBI, cost_factor):
        # NBI
        return(7.0642 * P_NBI * cost_factor)

    @staticmethod
    def Account_C22_1_4_2(P_ICRH, cost_factor):
        # ICRH
        return(4.149 * P_ICRH * cost_factor)

    @staticmethod
    def Account_C22_1_4_3(P_ECH, cost_factor):
        # ECH
        return(8.0 * P_ECH * cost_factor)

    @staticmethod
    def Account_C22_1_5():
        # Primary Structure and Support
        return(0)

    @staticmethod
    def Account_C22_1_6_2():
        # Helium Liquefier-Refrigerators (not for magnets)
        # Presumably for a full vessel cryostat?
        return(0)

    @staticmethod
    def Account_C22_1_6_3(no_vpumps, cost_pump):

        #VACUUM PUMPING 22.1.6.3
        return(no_vpumps * cost_pump / 1e6)
        

    @staticmethod
    def Account_C22_1_6_4():
        # Roughing Pump
        return(120000*2.85/1e6)

    @staticmethod
    def Account_C22_1_7():
        # Power Supplies

        # Not using Woodruff 2024 as that is based on ITER fusion power
        # Heating and magnets are tracked elsewhere
        
        # #Scaled relative to ITER for a 500MW fusion power syste
        # lcredit = 0.5# learning credit.
        # C220107 = 269.6 * PNRL/500*lcredit #cost in kIUA
        # C220107 = C220107*2 #assuming 1kIUA equals $2 M
        
        return(0)

    @staticmethod
    def Account_C22_1_8():
        # Divertor
        return(0)

    @staticmethod
    def Account_C22_1_9(P_DECe, cost_factor):
        # Direct Energy Convertor
        # Not using Woodruff 2024 numbers here, but instead Woodruff 2022
        return(1.7347 * P_DECe * cost_factor)

    @staticmethod
    def Account_C22_1_11(L, N_module, construction_time, cost_factor):
        # Assembly and Installation Costs
        
        #Cost Category 22.1.11 Installation costs
        axis_t = L/(2*np.pi) #[m] distance from r=0 to plasma central axis - effectively major radius
        axis_ir = axis_t

        # Define labor rate
        lr = 1600 / 1e6  # 1600 dollars per day for skilled labor

        # Calculations
        constructionworker = 20 * axis_ir / 4
        C_22_1_11_in = N_module * construction_time * (lr * 20 * 300)
        C_22_1_11_1_in = N_module * ((lr * 200 * constructionworker) + 0)  # 22.1 first wall blanket
        C_22_1_11_2_in = N_module * ((lr * 150 * constructionworker) + 0)  # 22.2 shield
        C_22_1_11_3_in = N_module * ((lr * 100 * constructionworker) + 0)  # coils
        C_22_1_11_4_in = N_module * ((lr *  30 * constructionworker) + 0)  # supplementary heating
        C_22_1_11_5_in = N_module * ((lr *  60 * constructionworker) + 0)  # primary structure
        C_22_1_11_6_in = N_module * ((lr * 200 * constructionworker) + 0)  # vacuum system
        C_22_1_11_7_in = N_module * ((lr * 400 * constructionworker) + 0)  # power supplies
        C_22_1_11_8_in = 0  # guns or divertor
        C_22_1_11_9_in = N_module * ((lr * 200 * constructionworker) + 0)   # direct energy converter
        C_22_1_11_10_in = 0  # ECRH

        # Total cost calculations
        C220111 = (C_22_1_11_in + C_22_1_11_1_in + C_22_1_11_2_in + C_22_1_11_3_in + C_22_1_11_4_in + C_22_1_11_5_in + C_22_1_11_6_in + C_22_1_11_7_in + C_22_1_11_8_in + C_22_1_11_9_in + C_22_1_11_10_in)

        return(C220111 * cost_factor)

    @staticmethod
    def Account_C22_2_1(N_module, P_egross):
        # Primary Coolant
        return(166  * (N_module * P_egross/1000))

    @staticmethod
    def Account_C22_2_2(P_th):
        # Secondary Coolant
        return(40.6 * (P_th/3500)**0.55)

    @staticmethod
    def Account_C22_2_3():
        # Tertiary Coolant
        return(0)

    @staticmethod
    def Account_C22_2(N_module, P_egross, P_th):
        # Main and Secondary Coolant
        return 166 * (N_module * P_egross / 1000) + 40.6 * (P_th / 3500) ** 0.55

    @staticmethod
    def Account_C22_3(N_module, P_th):
        # Auxiliary Cooling Systems
        return(1.10 * 1e-3 * N_module * P_th * 2.02)

    @staticmethod
    def Account_C22_4(P_th):
        # Radioactive Waste Treatment
        return(1.96 * 1e-3 * P_th * 2.02)

    @staticmethod
    def Account_C22_5(cost_factor):
        # Cost Category 22.5 Fuel Handling and Storage

        inflation = 1.43
        C2205010ITER = 20.465 * inflation
        C2205020ITER = 7 * inflation
        C2205030ITER = 22.511 * inflation
        C2205040ITER = 9.76 * inflation
        C2205050ITER = 22.826 * inflation
        C2205060ITER = 47.542 * inflation
        # C22050ITER = C2205010ITER + C2205020ITER + C2205030ITER + C2205040ITER + C2205050ITER + C2205060ITER #ITER inflation cost


        lcredit = 0.8 # learning curve
        ltoak = 10**(np.log10(lcredit) / np.log10(2))


        C220501 = C2205010ITER * ltoak
        C220502 = C2205020ITER * ltoak
        C220503 = C2205030ITER * ltoak
        C220504 = C2205040ITER * ltoak
        C220505 = C2205050ITER * ltoak
        C220506 = C2205060ITER * ltoak
        C220500 = C220501 + C220502 + C220503 + C220504 + C220505 + C220506 #ITER inflation cost
        
        return(C220500 * cost_factor)

    @staticmethod
    def Account_C22_6(P_enet):
        # Cost Category 22.6 Other Reactor Plant Equipment
        return(11.5*(np.max((P_enet,0))/1000)**(0.8))

    @staticmethod
    def Account_C22_7():
        # Cost Category 22.7 Instrumentation and Control
        return(85)

    @staticmethod
    def Account_C23(N_module, P_egross):
        # Turbine Plant Equipment
        return(N_module * P_egross * 0.219 *1.15)

    @staticmethod
    def Account_C24(N_module, P_egross):
        # Electric Plant Equipment
        return(N_module * P_egross * 0.054 * 1.15)

    @staticmethod
    def Account_C25(N_module, P_egross):
        # Miscellaneous Plant Equipment
        return(N_module * P_egross  * 0.038 * 1.15)
    
    @staticmethod
    def Account_C26(N_module, P_enet):
        # Heat Rejection
        return(N_module * P_enet * 0.107 * 1.15 )

    @staticmethod
    def Account_C27():
        # Special Materials
        # Total elsewhere, implement later
        return(0)

    @staticmethod
    def Account_C28():
        # Digital Twin
        return(5)

    @staticmethod
    def Account_C31(P_enet, construction_time):
        # Field Indirect Costs
        if P_enet > 0:
            return (max(P_enet / 150, 0)) ** -0.5 * P_enet * 0.02 * construction_time
        return 0

    @staticmethod
    def Account_C32(P_enet, construction_time):
        # Construction Supervision
        if P_enet > 0:
            return (P_enet / 150) ** -0.5 * P_enet * 0.05 * construction_time
        return 0

    @staticmethod
    def Account_C35(P_enet, construction_time, n_unit):
        # Design Services Offsite
        if P_enet > 0:
            cost_factor = 0.70 ** (np.log(n_unit) / np.log(2))
            return (P_enet / 150) ** -0.5 * P_enet * 0.03 * construction_time * cost_factor
        return 0

    @staticmethod
    def Account_C51():
        # Shipping and Transportation Costs
        return 8

    @staticmethod
    def Account_C52(N_module, P_egross, P_enet):
        # Spare Parts
        return 0.1 * (
            MirrorFunc.Account_C23(N_module, P_egross)
            + MirrorFunc.Account_C24(N_module, P_egross)
            + MirrorFunc.Account_C25(N_module, P_egross)
            + MirrorFunc.Account_C26(N_module, P_enet)
            + MirrorFunc.Account_C27()
            + MirrorFunc.Account_C28()
        )

    @staticmethod
    def Account_C53(include_tax):
        # Taxes
        return 100 if bool(include_tax) else 0

    @staticmethod
    def Account_C54():
        # Insurance
        return 1

    @staticmethod
    def Account_C55(P_enet):
        # Initial Fuel Load
        return P_enet / 150 * 34

    @staticmethod
    def Account_C58(include_decommissioning):
        # Decommissioning Costs
        return 200 if bool(include_decommissioning) else 0

    @staticmethod
    def Account_C61(N_module, P_f, NOAK):
        # Escalation
        learning_credit = 0.0 if bool(NOAK) else 1.0
        return N_module * P_f / 1000 * 115 * learning_credit

    @staticmethod
    def Account_C62():
        # Fees
        return 0

    @staticmethod
    def Account_C69(include_contingency, NOAK):
        # Contingency on Capitalized Financial Costs
        return 0

    @staticmethod
    def Account_OM(P_enet):
        # Annualized O&M Cost
        return 60 * P_enet * 1000 / 1e6

    ### MNyberg's Magnet Methods ###
    
    # Possibly integrate details from this paper: https://ieeexplore.ieee.org/document/10027193
    # Table 2 should give good general information
    # Critical current density from PROCESS
    @staticmethod
    def jcrit_rebco(temperature, b):
        """Critical current density for "REBCO" 2nd generation HTS superconductor
        temperature : input real : superconductor temperature (K)
        b : input real : Magnetic field at superconductor (T)
        jcrit : output real : Critical current density in superconductor (A/m2)

        Will return a negative number if the temperature is greater than Tc0, the
        zero-field critical temperature.
        """
        tc0 = 90.0  # (K)
        birr0 = 132.5  # (T)
        a = 1.82962e8  # scaling constant
        # exponents
        p = 0.5875
        q = 1.7
        alpha = 1.54121
        beta = 1.96679
        oneoveralpha = 1 / alpha

        validity = True

        if (temperature < 4.2) or (temperature > 72.0):
            validity = False
        if temperature < 65:
            if (b < 0.0) or (b > 15.0):
                validity = False
        else:
            if (b < 0.0) or (b > 11.5):
                validity = False

        if not validity:
            print(
                # f"jcrit_rebco: input out of range temperature: {temperature} Field: {b}"
            )

        if temperature < tc0:
            # Normal case
            birr = birr0 * (1 - temperature / tc0) ** alpha
        else:
            # If temp is greater than critical temp, ensure result is real but negative.
            birr = birr0 * (1 - temperature / tc0)

        if b < birr:
            # Normal case
            factor = (b / birr) ** p * (1 - b / birr) ** q
            jcrit = (a / b) * (birr**beta) * factor
        else:
            # Field is too high
            # Ensure result is real but negative, and varies with temperature.
            # tcb = critical temperature at field b
            tcb = tc0 * (1 - (b / birr0) ** oneoveralpha)
            jcrit = -(temperature - tcb)

        return jcrit, validity
    
    @staticmethod
    def HTS_storedEnergy(field, inner_rad, HTS_temp=20):
        radius_in_wham = 6.65 # cm
        radius_out_wham = 31.85 # cm
        B_wham = 17 # T
        cost_wham = 2.3/2 # MUSD
        mew_0=1 # TODO if I value is needed change this to be the real constant value
        width_ratio = 5 # TODO update
        volume_1 = math.pi*(radius_out_wham**2-radius_in_wham**2)

        j_crit_ratio = MirrorFunc.jcrit_rebco(HTS_temp,25*(20/17))[0]/MirrorFunc.jcrit_rebco(15,20)[0]

        # Equation taking into account width and critical current ratios
        I_star = B_wham*2*math.pi/(mew_0*(math.log(radius_out_wham)-math.log(radius_in_wham)))
        outer_rad=math.exp(field*2*math.pi/(mew_0*I_star*width_ratio*j_crit_ratio)+math.log(inner_rad))
        # Old simple equation
        # outer_rad=math.exp((field/(B_wham/(math.log(radius_out_wham)-math.log(radius_in_wham))))+math.log(inner_rad))
        volume_2 = math.pi*(outer_rad**2-inner_rad**2)
        ratioOfVols=volume_2/volume_1

        # From BL paper: https://doi.org/10.1016/j.enpol.2023.113511
        E_ratio=(field/B_wham)**2*ratioOfVols
        cost_ratio=E_ratio**0.6
        return cost_ratio*cost_wham


    @staticmethod
    def HF_magnet_cost(n_unit, HF_magnet_number, sc_mat_scale=1.0):
        # This is the HF cost per magnet [MUSD], not for all four

        cost = 29.10
        cost_factor = (0.70)**(np.log((n_unit - 1) * HF_magnet_number + 1)/np.log(2))
        
        return(cost * cost_factor * sc_mat_scale)

    @staticmethod
    def LF_magnet_cost(n_unit, LF_magnet_number, sc_mat_scale=1.0):
        # This is the LF cost per magnet [MUSD]

        cost = 6.25262
        cost_factor = (0.70)**(np.log((n_unit - 1) * LF_magnet_number + 1)/np.log(2))
        
        return(cost * cost_factor * sc_mat_scale)

    @staticmethod
    def CF_magnet_cost(n_unit, CF_magnet_number, sc_mat_scale=1.0):
        # This is the CF cost per magnet [MUSD]
        
        convert_to_currentDollar = 1.31
        cost = 0.7*3.0*convert_to_currentDollar # Assuming 700k/Tesla in 2016 dollars with 3T LTS
        cost_factor = (0.70)**(np.log((n_unit - 1) * CF_magnet_number + 1)/np.log(2))
        
        return(cost * cost_factor * sc_mat_scale)




    
