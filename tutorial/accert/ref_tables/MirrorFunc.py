import numpy as np
import pandas as pd
import scipy
import json
import math
import pkg_resources
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
        # run the algorithm use self.name not self.alg_name
        return self._run_algorithm(self.name, [inputs[var] for var in self.variables.split(",")])

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
    
    ### Account Methods: ### 
    @staticmethod
    def Account_C20(inputs):
        return(
            MirrorFunc.Account_C21(inputs) +
            MirrorFunc.Account_C22(inputs) +
            MirrorFunc.Account_C23(inputs) +
            MirrorFunc.Account_C24(inputs) +
            MirrorFunc.Account_C25(inputs) +
            MirrorFunc.Account_C26(inputs) +
            MirrorFunc.Account_C27(inputs) +
            MirrorFunc.Account_C28(inputs) +
            MirrorFunc.Account_C29(inputs)
            )
    
    @staticmethod
    def Account_C21(inputs):
        return(
            MirrorFunc.Account_C21_1(inputs) +
            MirrorFunc.Account_C21_2(inputs) +
            MirrorFunc.Account_C21_3(inputs) +
            MirrorFunc.Account_C21_4(inputs) +
            MirrorFunc.Account_C21_5(inputs) +
            MirrorFunc.Account_C21_6(inputs) +
            MirrorFunc.Account_C21_7(inputs) +
            MirrorFunc.Account_C21_8(inputs) +
            MirrorFunc.Account_C21_9(inputs) +
            MirrorFunc.Account_C21_10(inputs) +
            MirrorFunc.Account_C21_11(inputs) +
            MirrorFunc.Account_C21_12(inputs) +
            MirrorFunc.Account_C21_13(inputs) +
            MirrorFunc.Account_C21_14(inputs) +
            MirrorFunc.Account_C21_15(inputs) +
            MirrorFunc.Account_C21_16(inputs) +
            MirrorFunc.Account_C21_17(inputs)
            )
    
    @staticmethod
    def Account_C21_1(inputs):
        # Site Preparation/Yard Work
        return(inputs['Gross Electric Power'] * 268/1e3)
    
    @staticmethod
    def Account_C21_2(inputs):
        # Heat Island Building
        return(inputs['Gross Electric Power'] * 186.8/1e3)
    
    @staticmethod
    def Account_C21_3(inputs):
        # Turbine Generator Building
        if inputs['Application'].lower()=='electricity':
            return(inputs['Gross Electric Power'] * 54.0/1e3)
        else:
            return(0)

    @staticmethod
    def Account_C21_4(inputs): 
        # Heat Exchanger Building
        return(37.8/1e3 * inputs['Gross Electric Power'])

    @staticmethod
    #21.05.00,,Power supply & energy storage,Concrete & Steel,9.1,9.7,9.7,6.0,560,2019,1.19,
    def Account_C21_5(inputs): 
        # Power Supply and Energy Storage
        return(10.8/1e3 * inputs['Gross Electric Power'])
    
    @staticmethod
    #21.06.00,,Reactor auxiliaries,Concrete & Steel,4.5,4.8,4.8,3.0,70,2019,1.19,
    def Account_C21_6(inputs): 
        # Reactor Auxiliaries
        return(5.4/1e3 * inputs['Gross Electric Power'])

    @staticmethod
    #21.07.00,,Hot cell,Concrete & Steel,65.8,24.2,24.2,60,35000,2013,1.42,
    def Account_C21_7(inputs): 
        # Hot Cell
        return(93.4/1e3 * inputs['Gross Electric Power'])

    @staticmethod
    #21.08.00,,Reactor services,Steel frame,13.2,4.8,4.8,10,233,2013,1.42,
    def Account_C21_8(inputs): 
        # Reactor Services
        return(18.7/1e3 * inputs['Gross Electric Power'])

    @staticmethod
    #21.09.00,,Service water,Steel frame,0.2,1.3,4.0,4.0,21,2019,1.19,
    def Account_C21_9(inputs): 
        # Service Water
        return(0.3/1e3 * inputs['Gross Electric Power'])

    @staticmethod
    #21.10.00,,Fuel storage,Steel frame,0.9,5.0,15.0,2.5,188,2019,1.19,
    def Account_C21_10(inputs):
        # Fuel Storage
        return(1.1/1e3 * inputs['Gross Electric Power'])

    @staticmethod
    #21.11.00,,Control room,Steel frame,0.7,4.0,12.0,2,96,2019,1.19,
    def Account_C21_11(inputs):
        # Control Room
        return(0.9/1e3 * inputs['Gross Electric Power'])

    @staticmethod
    #21.12.00,,Onsite AC inputs,Steel frame,0.7,3.6,10.8,1.8,70,2019,1.19,
    def Account_C21_12(inputs):
        # Onsite AC Power
        return(0.8/1e3 * inputs['Gross Electric Power'])

    @staticmethod
    #21.13.00,,Administration,Steel frame,3.7,20.0,60.0,10,12000,2019,1.19,
    def Account_C21_13(inputs): 
        # Administration
        return(4.4/1e3 * inputs['Gross Electric Power'])

    @staticmethod
    #21.14.00,,Site services,Steel frame,1.3,7.3,22.0,3.7,593,2019,1.19,
    def Account_C21_14(inputs): 
        # Site Services
        return(1.6/1e3 * inputs['Gross Electric Power'])

    @staticmethod
    #21.15.00,,Cryogenics,Steel frame,2.0,11.0,33.0,5.5,2003,2019,1.19,
    def Account_C21_15(inputs):
        # Cyrogenics
        return(2.4/1e3 * inputs['Gross Electric Power'])

    @staticmethod
    #21.16.00,,Security,Steel frame,0.7,4.0,12.0,2,96,2019,1.19,
    def Account_C21_16(inputs): 
        # Security
        return(0.9/1e3 * inputs['Gross Electric Power'])

    @staticmethod
    #21.17.00,,Ventilation stack,Steel cylinder & concrete foundation,22.7,,,120,,2019,1.19,
    def Account_C21_17(inputs): 
        # Ventilation Stack
        return(27.0/1e3 * inputs['Gross Electric Power'])


    @staticmethod
    def Account_C22(inputs):
        # Rollup
        return(
            MirrorFunc.Account_C22_1(inputs) +
            MirrorFunc.Account_C22_2(inputs) +
            MirrorFunc.Account_C22_3(inputs) +
            MirrorFunc.Account_C22_4(inputs) +
            MirrorFunc.Account_C22_5(inputs) +
            MirrorFunc.Account_C22_6(inputs) +
            MirrorFunc.Account_C22_7(inputs)
            )


    @staticmethod
    def Account_C22_1(inputs):
        # This is a special case and is NOT calculated using Woodruff's model,
        # However, I maintained the naming convention for convenience
        # Rollup
        return(
            MirrorFunc.Account_C22_1_1(inputs) +
            MirrorFunc.Account_C22_1_2(inputs) +
            MirrorFunc.Account_C22_1_3(inputs) +
            MirrorFunc.Account_C22_1_4(inputs) +
            MirrorFunc.Account_C22_1_5(inputs) +
            MirrorFunc.Account_C22_1_6(inputs) +
            MirrorFunc.Account_C22_1_7(inputs) +
            MirrorFunc.Account_C22_1_8(inputs) +
            MirrorFunc.Account_C22_1_9(inputs) +
            MirrorFunc.Account_C22_1_11(inputs)
            )

    @staticmethod
    def Account_C22_1_1(inputs):
        # First Wall and Blanket (and vacuum vessel)

        L_magnet_to_magnet = inputs['End Plug Length']

        L_cylinder = L_magnet_to_magnet 
        
        expander_cell_cost_result = MirrorFunc.expander_cell_cost(inputs)

        end_plug_cylindrical_part = MirrorFunc.central_cell(inputs, L_cylinder)
        end_plug_cylindrical_part_cost = end_plug_cylindrical_part['cost'].max()

        central_cell_cylindrical_part = MirrorFunc.central_cell(inputs, inputs['Central Cell Length'])
        central_cell_cylindrical_part_cost = central_cell_cylindrical_part['cost'].max()

        total_cost = central_cell_cylindrical_part_cost + 2 * end_plug_cylindrical_part_cost + 2 * expander_cell_cost_result
        
        return(total_cost/1e6)

    @staticmethod
    def Account_C22_1_2(inputs):
        # Magnet Radiation Shield
        # Factor of two for each end plug
        return(2 * MirrorFunc.HF_magnet_shield_cost(inputs) / 1e6)

    @staticmethod
    def Account_C22_1_3(inputs):
        # Coils
        # Rollup
        return(
            MirrorFunc.Account_C22_1_3_1(inputs) +
            MirrorFunc.Account_C22_1_3_2(inputs) +
            MirrorFunc.Account_C22_1_3_3(inputs)
            )

    # @staticmethod
    def Account_C22_1_3_1(inputs):
        # HF Coils - Quantity 4
        # 2 per end cell
        # 2 end cells per tandem
        return(inputs['HF Magnet Number'] * MirrorFunc.HF_magnet_cost(inputs))

    @staticmethod
    def Account_C22_1_3_2(inputs):
        # LF Coils - Quantity 8
        # 4 per end cell
        # 2 end cells per tandem
        return(inputs['LF Magnet Number'] * MirrorFunc.LF_magnet_cost(inputs))

    @staticmethod
    def Account_C22_1_3_3(inputs):
        # CF Coils
        # One coil every L_CF m of Central Cell
        return(inputs['CF Magnet Number'] * MirrorFunc.CF_magnet_cost(inputs))

    @staticmethod
    def Account_C22_1_4(inputs):
        # Supplemenatry Heating
        # Rollup
        return(
            MirrorFunc.Account_C22_1_4_1(inputs) + 
            MirrorFunc.Account_C22_1_4_2(inputs) +
            MirrorFunc.Account_C22_1_4_3(inputs)
            )

    @staticmethod
    def Account_C22_1_4_1(inputs):
        # NBI
        cost_factor = (0.80)**(np.log(inputs['Unit Number'])/np.log(2))
        return(7.0642 * inputs['NBI Power'] * cost_factor)

    @staticmethod
    def Account_C22_1_4_2(inputs):
        # ICRH
        cost_factor = (0.80)**(np.log(inputs['Unit Number'])/np.log(2))
        return(4.149 * inputs['ICRH Power'] * cost_factor)

    @staticmethod
    def Account_C22_1_4_3(inputs):
        # ECH
        cost_factor = (0.80)**(np.log(inputs['Unit Number'])/np.log(2))
        return(8.0 * inputs['ECH Power'] * cost_factor)

    @staticmethod
    def Account_C22_1_5(inputs):
        # Primary Structure and Support
        return(0)

    @staticmethod
    def Account_C22_1_6(inputs):
        # Vacuum Systems
        # Rollup
        return(
            # Account_C22_1_6_1(inputs) + 
            MirrorFunc.Account_C22_1_6_2(inputs) +
            MirrorFunc.Account_C22_1_6_3(inputs) + 
            MirrorFunc.Account_C22_1_6_4(inputs)
            )


    # def Account_C22_1_6_1(inputs):
        # Vacuum Vessel
        # Tracked in radial builds and folded into blanket
        # return(0)


    @staticmethod
    def Account_C22_1_6_2(inputs):
        # Helium Liquefier-Refrigerators (not for magnets)
        # Presumably for a full vessel cryostat?
        return(0)

    @staticmethod
    def Account_C22_1_6_3(inputs):

        #VACUUM PUMPING 22.1.6.3
        #assume 1 second vac rate
        #cost of 1 vacuum pump, scaled from 1985 dollars
        cost_pump = 40000
        #48 pumps needed for 200^3 system
        vpump_cap = 200/48 #m^3 capable of beign pumped by 1 pump
        no_vpumps = inputs['Vacuum Volume']/vpump_cap#Number of vacuum pumps required to pump the full vacuum in 1 second
        return(no_vpumps*cost_pump/1e6)
        

    @staticmethod
    def Account_C22_1_6_4(inputs):
        # Roughing Pump
        return(120000*2.85/1e6)

    @staticmethod
    def Account_C22_1_7(inputs):
        # Power Supplies

        # Not using Woodruff 2024 as that is based on ITER fusion power
        # Heating and magnets are tracked elsewhere
        
        # #Scaled relative to ITER for a 500MW fusion power syste
        # lcredit = 0.5# learning credit.
        # C220107 = 269.6 * PNRL/500*lcredit #cost in kIUA
        # C220107 = C220107*2 #assuming 1kIUA equals $2 M
        
        return(0)

    @staticmethod
    def Account_C22_1_8(inputs):
        # Divertor
        return(0)

    @staticmethod
    def Account_C22_1_9(inputs):
        # Direct Energy Convertor
        # Not using Woodruff 2024 numbers here, but instead Woodruff 2022
        cost_factor = (0.80)**(np.log(inputs['Unit Number'])/np.log(2))
        return(1.7347 * inputs['DEC Electrical Power'] * cost_factor)

    @staticmethod
    def Account_C22_1_11(inputs):
        # Assembly and Installation Costs
        
        #Cost Category 22.1.11 Installation costs
        axis_t = inputs['Overall Length']/(2*np.pi) #[m] distance from r=0 to plasma central axis - effectively major radius
        axis_ir = axis_t

        # Define labor rate
        lr = 1600 / 1e6  # 1600 dollars per day for skilled labor

        # Calculations
        constructionworker = 20 * axis_ir / 4
        C_22_1_11_in = inputs['Number of Modules'] * inputs['Construction Time'] * (lr * 20 * 300)
        C_22_1_11_1_in = inputs['Number of Modules'] * ((lr * 200 * constructionworker) + 0)  # 22.1 first wall blanket
        C_22_1_11_2_in = inputs['Number of Modules'] * ((lr * 150 * constructionworker) + 0)  # 22.2 shield
        C_22_1_11_3_in = inputs['Number of Modules'] * ((lr * 100 * constructionworker) + 0)  # coils
        C_22_1_11_4_in = inputs['Number of Modules'] * ((lr *  30 * constructionworker) + 0)  # supplementary heating
        C_22_1_11_5_in = inputs['Number of Modules'] * ((lr *  60 * constructionworker) + 0)  # primary structure
        C_22_1_11_6_in = inputs['Number of Modules'] * ((lr * 200 * constructionworker) + 0)  # vacuum system
        C_22_1_11_7_in = inputs['Number of Modules'] * ((lr * 400 * constructionworker) + 0)  # power supplies
        C_22_1_11_8_in = 0  # guns or divertor
        C_22_1_11_9_in = inputs['Number of Modules'] * ((lr * 200 * constructionworker) + 0)   # direct energy converter
        C_22_1_11_10_in = 0  # ECRH

        # Total cost calculations
        C220111 = (C_22_1_11_in + C_22_1_11_1_in + C_22_1_11_2_in + C_22_1_11_3_in + C_22_1_11_4_in + C_22_1_11_5_in + C_22_1_11_6_in + C_22_1_11_7_in + C_22_1_11_8_in + C_22_1_11_9_in + C_22_1_11_10_in)

        cost_factor = (0.80)**(np.log(inputs['Unit Number'])/np.log(2))
        
        return(C220111 * cost_factor)

    @staticmethod
    def Account_C22_2(inputs):
        # Main and Secondary Coolant
        return(
            MirrorFunc.Account_C22_2_1(inputs) +
            MirrorFunc.Account_C22_2_2(inputs) +
            MirrorFunc.Account_C22_2_3(inputs)
            )

    @staticmethod
    def Account_C22_2_1(inputs):
        # Primary Coolant
        return(166  * (inputs['Number of Modules'] * inputs['Gross Electric Power']/1000))

    @staticmethod
    def Account_C22_2_2(inputs):
        # Secondary Coolant
        return(40.6 * (inputs['Thermal Power']/3500)**0.55)

    @staticmethod
    def Account_C22_2_3(inputs):
        # Tertiary Coolant
        return(0)

    @staticmethod
    def Account_C22_3(inputs):
        # Auxiliary Cooling Systems
        return(1.10 * 1e-3 * inputs['Number of Modules'] * inputs['Thermal Power'] * 2.02)

    @staticmethod
    def Account_C22_4(inputs):
        # Radioactive Waste Treatment
        return(1.96 * 1e-3 * inputs['Thermal Power'] * 2.02)

    @staticmethod
    def Account_C22_5(inputs):
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
        
        cost_factor = (0.80)**(np.log(inputs['Unit Number'])/np.log(2))
        
        return(C220500 * cost_factor)

    @staticmethod
    def Account_C22_6(inputs):
        # Cost Category 22.6 Other Reactor Plant Equipment
        return(11.5*(np.max((inputs['Net Electric Power'],0))/1000)**(0.8))

    @staticmethod
    def Account_C22_7(inputs):
        # Cost Category 22.7 Instrumentation and Control
        return(85)

    @staticmethod
    def Account_C23(inputs):
        # Turbine Plant Equipment
        return(inputs['Number of Modules'] * inputs['Gross Electric Power'] * 0.219 *1.15)

    @staticmethod
    def Account_C24(inputs):
        # Electric Plant Equipment
        return(inputs['Number of Modules'] * inputs['Gross Electric Power'] * 0.054 * 1.15)

    @staticmethod
    def Account_C25(inputs):
        # Miscellaneous Plant Equipment
        return(inputs['Number of Modules'] * inputs['Gross Electric Power']  * 0.038 * 1.15)
    
    @staticmethod
    def Account_C26(inputs):
        # Heat Rejection
        return(inputs['Number of Modules'] * inputs['Net Electric Power'] * 0.107 * 1.15 )

    @staticmethod
    def Account_C27(inputs):
        # Special Materials
        # Total elsewhere, implement later
        return(0)

    @staticmethod
    def Account_C28(inputs):
        # Digital Twin
        return(5)

    @staticmethod
    def Account_C29(inputs):
        # Contingency on Direct Capital Costs
        
        # I may have to change the way that I do sums as this must be done separately?
        # C21 = sum(C21.1 + C21.2 + ...)

        # Rollup
        
        if not(inputs['NOAK']) and inputs['Contingency']:
            return(0.1 * (
                MirrorFunc.Account_C21(inputs) + 
                MirrorFunc.Account_C22(inputs) + 
                MirrorFunc.Account_C23(inputs) + 
                MirrorFunc.Account_C24(inputs) + 
                MirrorFunc.Account_C25(inputs) + 
                MirrorFunc.Account_C26(inputs) + 
                MirrorFunc.Account_C27(inputs) +
                MirrorFunc.Account_C28(inputs)))
        else:
            return(0)


    ### Other Methods: ###
    @staticmethod
    def PbLi_density(f_6Li=0.075, T=300):
        """
        Returns PbLi density [kg/m^3]. Assumes the PbLi is a eutectic, which has
        roughly 83% Pb and 17% Li.

        Parameters
        ----------
        f_6Li : float, optional
            Fraction of 6Li to all Li, aka enrichment. The default is 0.075.
        T : float, optional
            Temperature. Units are °C. The default is 300.

        Returns
        -------
        Density of PbLi at selected parameters.

        """
        
        f_6Li_natural = 0.075
        rho_6Li = 0.460e3 # kg/m^3
        rho_7Li = 0.537e3 # kg/m^3

        T_K = T + 273.15 # K

        # Use equation for density as function of temperature from below, Table 1
        # Note this is valid only from 508 K to 880 K (234.85 °C to 606.85 °C)
        # https://pubs.aip.org/aip/jcp/article-abstract/27/5/1033/204623/Bulk-Density-of-Separated-Lithium-Isotopes?redirectedFrom=PDF
        rho_PbLi = 10520.35 - 1.19051 * T_K
        
        
        # Correct calculated density for enrichment
        rho_PbLi = rho_PbLi * (rho_6Li * f_6Li + rho_7Li * (1-f_6Li)) / (rho_6Li * f_6Li_natural + rho_7Li * (1-f_6Li_natural))
        
        return(rho_PbLi)
    
    @staticmethod
    def Li_price(f_6Li=0.075):
        """
        Return Li price (USD/kg) for enrichment levels above 90% 6Li

        Parameters
        ----------
        f_6Li : TYPE, optional
            DESCRIPTION. The default is 0.075.

        Returns
        -------
        None.

        """
        
        # https://www.dailymetalprice.com/lithium.html
        # From 2024-04-01
        P_6Li075 = 15.152 # USD/kg
        
        if f_6Li == 0.075:
            return(P_6Li075)
        
        elif f_6Li >= 0.90:
            # From Woodruff for 90% 6Li
            P_6Li90 = 70 # USD/kg
            
            # El-Guebaly 2011 (AIRES-AT UK Study)
            # P_6Li90 = 2400.0 #USD/kg
            
            
            f = [0.90, 0.99, 0.999, 0.9999, 0.99999]
            Cf = [1, 2, 4, 8, 16]
            
            f_interp = scipy.interpolate.interp1d(f, Cf)
            return(f_interp(f_6Li) * P_6Li90)
        
        else:
            print('Lithium pricing at this enrichment level not supported')
            return()

    @staticmethod
    def PbLi_price(f_6Li, P_Pb):
        
        # Assuming eutectic fractions
        f_Li = 0.17
        f_Pb = 1 - f_Li

        P_Li = MirrorFunc.Li_price(f_6Li)
        
        P_PbLi = f_Pb * P_Pb + f_Li * P_Li # USD/kg
        
        return(P_PbLi)
    @staticmethod
    def V_cylindrical_shell(r_in, r_out, L):
        """
        Return volume of a cylindrical shell

        Parameters
        ----------
        r_in : float, inner radius
        r_out : float, outer radius
        L : float, length

        Returns
        -------
        Volume (float).

        """
        return(np.pi * L * (r_out**2 - r_in**2))

    @staticmethod
    def V_inverse_triangular_washer(z, r_in, r_out):
        """
        Return volume of cylindrical inverse triangular washer.
        From the ASCII art below you can see how this is used for magnet shielding.
        
                    ^ z
                    |
                    |               z
        |\            |            /|
        | \           |           / |
        |  \          |          /  |
        |   \         |         /   |   
        |    \        |        /    |
        |     \       |       /     |
        ------------------------------------> r
                            r_in  r_out 

        Parameters
        ----------
        z : float, z extent of triangle
        r_in : float, inner radius of triangle
        r_out : float, outer radius of triangle

        Returns
        -------
        Volume (float).

        """
        
        
        # https://www.wolframalpha.com/input?i=integral+of+2+pi+r+%28+z*r+%2F+%28b-a%29++-+z*a+%2F+%28b-a%29+%29+dr+from+a+to+b
        
        return(np.pi * z / 3 * (r_out - r_in) * (r_in + 2 * r_out))
    @staticmethod
    def generate_inputs(
            
        application='heat',
    
        P_f=1, P_f_L=1, P_f_EP=1,
        P_NBI=1, P_ECH=1, P_ICRH=1,
        M_n=1.1, 
        
        N_module=1, 
        
        f_pump=0.03, f_sub=0.04, f_cryo=0.01,   
        
        # Obsolete but kept for backwards compatibility
        P_pump=1, P_sub_cont=1, P_cryo=1, 
        P_pfcool=0, P_thcool=0, P_coils=0, P_aux=1,
        
        eta_th=0.50, eta_DEC=0.90, eta_pump=0.98, 
        eta_NBI=0.50, eta_ECH=0.50, eta_ICRH=0.50,
        
        verbose=False, exact=False, 
        NOAK=False, n_unit=False,
        construction_time=6,
        lifetime=30, replacement=10, availability=0.90, 
        discount=0.0245,
        LSA=2, 
        cost_file='woodruff-data.csv', method='new',
        include_decommissioning=False, include_tax=False,
        include_licensing=False, include_contingency=False,
        
        hf_magnet_length=1,
        hf_magnet_shielding_thickness=1,
        
        a_EC=1,
        expander_cell_vessel_thickness=0.01,
        expander_cell_vessel_material='SS316',
        
        vacuum_gap_CC=0.01,
        first_wall_material='W',
        first_wall_thickness=0.01,
        vacuum_vessel_material='SS316',
        vacuum_vessel_thickness=0.01,
        multiplier_material='Pb',
        multiplier_thickness=0.01,
        blanket_coolant_material='Natural PbLi',
        blanket_thickness=1.00,
        blanket_coolant_fraction=0.90,
        blanket_structural_material='SS316',
        blanket_structural_fraction=0.10,
        outer_vessel_thickness=0.01,
        
        L_EP=1,
        L_EC=1,  
        a_CC=1,
        a_EP=1,
    
        save=True,
        load=False,
        filename=None,
        run_name=None
    
        ):
        
        """
        Return a dict containing all inputs for a techno-economic analysis.
        
        Parameters
        ----------
        application : str, optional
            The application, either 'electricity' or 'heat'. 
            This changes the power balance and some reporting. The default 
            is 'heat'.
        P_f : float
            The total fusion power in MW.  The length of the central cell 
            is scaled to achieve this value. This is not the net electrical power!
        P_f_L : float
            The central cell linear fusion power in MW/m. 
        P_f_EP : float
            The fusion power in each of two end plugs in MW.  
        P_NBI : float 
            The applied NBI power in MW.  
        P_ECH : float
            The applied ECH power in MW.  
        P_ICRH : float
            The applied ICRH power in MW.  
        M_n : float
            The neutron power multiplication factor from the blanket.  
            The default is 1.1.
        N_module : int
            The number of modules (fusion machines) per facility.  
            This is deprecated. The default is 1. 
        f_pump : float
            The pumping power fraction (of M_n * P_fusion).  The default is 0.03.
        f_sub : float
            The subsystem power fraction (of fusion power).  The default is 0.04.
        f_cryo : float
            The cryogenic power fraction (of fusion power).  The default is 0.01.
        P_pump : float
            The pumping power in MW.  This is deprecated.
        P_sub_cont : float
            The subsystem and control power in MW.  This is deprecated.
        P_cryo: float
            The cryo power in MW.  The default is 0.5 MW.  This is deprecated.
        P_pfcool : float
            The PF cooling power in MW.  The default is 0.  This is deprecated. 
        P_thcool : float
            The thermal cooling power in MW.  The default is 0.  This is deprecated.
        P_coils : float
            The magnetic coil power in MW.  The default is 0.
        P_aux : float
            The auxiliary power in MW.  The default is 9.4. 
            
        eta_th : float
            The thermal conversion efficiency.  
        eta_DEC : float
            The DEC conversion efficiency.  The default is 0.90.
        eta_pump : float
            The pumping efficiency.  The default is 0.98.
        eta_NBI : float
            The NBI electrical efficiency.  
        eta_ECH : float
            The ECH electrical efficiency.  
        eta_ICRH : float
            The ICRH electrical efficiency.  
        
        LSA : int
            The level of safey assurance.  The default is 2.  This is deprecated.
            
        construction_time : int
            The construction time in years.  The default is 6.
        NOAK : bool
            Whether this is an NOAK device.  The default is False.  
            This will probably be deprecated soon.
        n_unit : int or bool
            The number of the tandem unit, in terms of first of a kind (1), 
            second of a kind (2), etc.  When this is False, the FOAK cost is used.
            The default is False.
        lifetime : int 
            The lifetime of the tandem in years.  This is used for LCOE and LCOH 
            calcualtions.  The default is 30.
        replacement : int 
            The replacement interval of the magnets in years.  The default is 10.
        availability : float
            The facility availability. The range is between 0 and 1, inclusive.
            The default is 0.90.
        cost_file : str
            The filename of the cost file.  The default is 'woodruff-data.csv'.
        method : str
            The power balance method.  The default is 'new'.  
            This will be deprecated soon.
        include_tax : bool
            Whether to include tax.  The default is False.
        include_decommissioning : bool
            Whether to include decommissioning.  The default is False.
        include_licensing : bool
            Whether to include licensing.  The default is False.
        include_contingency : bool
            Whether to include continency.  The default is False.
        verbose : bool
            Whether to print a lot.  The default is False.
        vacuum_gap_CC : float
            The vacuum gap in the central cell, in meters.  The default is 0.01.
        first_wall_material : str
            The first wall material.  The default is 'W'.
        first_wall_thickness : float
            The first wall thickness, in meters.  The default is 0.01.
        vacuum_vessel_material : str
            The vacuum vessel material.  The default is 'SS316'.
        vacuum_vessel_thickness : float
            The vacuum vessel thickness, in meters.  The default is 0.01
        multiplier_material : str
            The muliplier material.  The default is 'Pb'
        multiplier_thickness : float
            The multiplier thickness, in meters.  The default is 0.01.
        blanket_coolant_material : str
            The blanket coolant material.  The default is 'Natural PbLi'.
        blanket_thickness : float
            The blanket thickness, in meters.  The default is 1.00.
        blanket_coolant_fraction : float
            The blanket coolant fraction, from 0 to 1.  The default is 0.90.
        blanket_structural_material : str
            The blanket structural material.  The default is 'SS316'.
        blanket_structural_fraction : float
            The blanket structural fraction, from 0 to 1.  The default is 0.10.
        outer_vessel_thickness : float
            The outer vessel thickness, in meters.  The default is 0.01.
        contours : bool
            Whether to plot contours of discount rates and build time. 
            The default is False.
        tornadoes : bool
            Whether to plot tornado plots.  These take a while to make.  
            The default is False.
    
        hf_magnet_length : float
            The axial length of the HF magnet, in meters.  The default is 1.0.
        hf_magnet_shielding_thickness : 
            The default is 1.0,
        
        a_EC : float
            The expander cell radius, in meters.  The default is 1.0.
        expander_cell_vessel_thickness : float
            The expander cell vessel thickness, in meters.  The default is 0.01.
        expander_cell_vessel_material : str
            The expander cell vessel material.  The default is 'SS316'.
        

        
        L_EP : float
            The length of each end plug, in meters.  The default is 1.
        L_EC : float
            The length of each expander cell, in meters, measured from the 
            centers of the HF coils.  The default is 1.  
        a_CC : float
            The central cell plasma radius, in meters.  The default is 15.
        a_EP : float
            The end plug plasma radius, in meters.  The default is 1.



        
        save : bool
            Whether to save the results.  The default is True.
        load : bool
            Whether to load results.  The default is False.
        filename : str
            The filename loading.  The default is None.
        run_name : str
            A run name for saving results.  The default is None.
        
        
        """
                    
        if load:
            with open(filename) as file:
                inputs = json.load(file)
                
        else:
            
            # Fusion Power in Central Cell    
            P_f_CC = P_f - 2 * P_f_EP
            
            # Central Cell Length
            L_CC = P_f_CC/P_f_L
            
            # Central Field Coil Spacing
            L_CF = 1.0
        
            # Overall Device Length
            L = L_CC + 2 * L_EP + 2 * L_EC
            
            # Vacuum Volume - Not precise, but also not important
            # Should be updated
            V_vac = L * np.pi * a_EC**2
        
        
            # Power Balance
            P_alpha = P_f * MirrorFunc.E_alpha / MirrorFunc.E_DT  # MW, alpha power
            P_n = P_f - P_alpha # MW, neutron power
                
            # Input electrical power
            P_ine = P_NBI/eta_NBI + P_ICRH/eta_ICRH + P_ECH/eta_ECH

            # Balance of Plant
            P_pump = f_pump * M_n * P_n
            P_sub_cont = f_sub * P_f
            P_cryo = f_cryo * P_f
            P_other = P_pump + P_sub_cont + P_cryo

            # Total heating input power applied to plasma
            P_in = P_NBI + P_ICRH + P_ECH

            # Heat in blanket including neutron multiplication
            # P_thermal_only = M_n * P_n
            
            # Thermal power
            # No P_in term as that goes to DEC
            P_th = M_n * P_n +  eta_pump * P_pump 
            
            # Thermal electric power
            P_the = eta_th * P_th
            
            # DEC receives all charged particle exhaust, so is the sum of 
            # both the input power and alpha power
            P_DEC = P_in + P_alpha
            
            # DEC electrical power
            P_DECe = eta_DEC * P_DEC
            
            # Gross electrical power
            # Differs for application
            if application.lower()=='electricity':
                # Electrical application uses thermal power to create electricity
                P_egross = P_DECe + P_the
            elif application.lower()=='heat':
                # Heat application only uses DEC to create electricity
                P_egross = P_DECe

            # Net electrical power
            P_enet = P_egross - (P_ine + P_other)
                
            f_aux =  P_aux / P_egross
            # P_loss = P_th - P_the - P_DECe
            # P_sub = f_sub * P_the
            
            # Scientific Q
            Q_sci = P_f / P_in
            
            # Engineering Q
            Q_eng = P_egross / (P_ine + P_other)

            # Recirculating power
            f_refrac = 1 / Q_eng
            if run_name==None:
                run_name = '{:.1f}-MW'.format(float(P_f))
            

            cost_file_full = pkg_resources.resource_filename('TEAm_public', cost_file)
                
            inputs = {
                
                # Application (heat or electricity)
                'Application':application,
                'Method':method,
                
                # Power Balance
                'Fusion Power': P_f, 
                'Alpha Power': P_alpha, 
                'Neutron Power': P_n, 
                'Neutron Energy Multiplication': M_n, 
                # 'Thermal Only Power': P_thermal_only,
                'Thermal Power': P_th, 
                'Thermal Conversion Efficiency': eta_th, 
                
                # DEC
                'DEC Efficiency': eta_DEC, 
                'DEC Electrical Power': P_DECe, 
                'DEC Input Power': P_DEC, 
                
                # Balance
                'Thermal Electric Power': P_the, 
                'Gross Electric Power': P_egross, 
                'Net Electric Power': P_enet,
                
                # Other Power
                'Other Power': P_other,
                'Pumping Power Fraction': f_pump, 
                'Pumping Power': P_pump, 
                'Subsystem and Control Power': P_sub_cont, 
                'Auxiliary Power Fraction': f_aux, 
                'Auxiliary Power': P_aux, 
                
                # Input Power
                'Applied Heating Power': P_in, 
                'Applied Heating Power Electrical Use': P_ine,
                'NBI Power': P_NBI,
                'ICRH Power': P_ICRH,
                'ECH Power': P_ECH,
                'NBI Electrical Efficiency': eta_NBI,
                'ICRH Electrical Efficiency': eta_ICRH,
                'ECH Electrical Efficiency': eta_ECH,
                
                # Q
                'Scientific Q': Q_sci, 
                'Engineering Q': Q_eng, 
                'Recirculating Power Fraction': f_refrac, 

                # Don't use this - it is probably not implemented well here
                'Number of Modules': N_module,
                
                # Time Intervals
                'Construction Time':construction_time,
                'Lifetime':lifetime,
                'Replacement Time':replacement,
                'Level of Safety Assurance':LSA,
                
                # Geometry
                'Overall Length':L,
                'Central Cell Length':L_CC,
                'End Plug Length':L_EP,
                'Expander Length':L_EC,
                'Vacuum Volume':V_vac,
                
                # Number of Magnets
                'HF Magnet Number':4, # Always 4 for a tandem
                'LF Magnet Number':2, # Set to what you need!
                'CF Magnet Spacing':L_CF,
                'CF Magnet Number':L_CC/L_CF, # Calcuated
                
                'HF Magnet Length':hf_magnet_length,
                'HF Magnet Shielding Thickness':hf_magnet_shielding_thickness,
                
                'End Plug Plasma Radius':a_EP,
                
                'Expander Cell Length':L_EC,
                'Expander Cell Radius':a_EC,
                'Expander Cell Vessel Thickness':expander_cell_vessel_thickness,
                'Expander Cell Vessel Material':expander_cell_vessel_material,
                
                'Central Cell Plasma Radius':a_CC,
                'Central Cell Vacuum Gap':vacuum_gap_CC,
                'First Wall Material':first_wall_material,
                'First Wall Thickness':first_wall_thickness,
                'Vacuum Vessel Material':vacuum_vessel_material,
                'Vacuum Vessel Thickness':vacuum_vessel_thickness,
                'Multiplier Material':multiplier_material,
                'Multiplier Thicnkess':multiplier_thickness,
                'Blanket Coolant Material':blanket_coolant_material,
                'Blanket Thickness':blanket_thickness,
                'Blanket Coolant Fraction':blanket_coolant_fraction,
                'Blanket Structural Material':blanket_structural_material,
                'Blanket Structrual Fraction':blanket_structural_fraction,
                'Outer Vessel Thickness':outer_vessel_thickness,
        
                # Economic Factors
                'Availability':availability,
                'Discount':discount,
                'NOAK': NOAK,
                'Unit Number':n_unit,
                # 'Cost File':cost_file,
                'Cost File':cost_file_full,
                'Licensing':include_licensing,
                'Tax':include_tax,
                'Decommissioning':include_decommissioning,
                'Contingency':include_contingency,

                # File Prefix
                'Run Name':run_name
                
                }
            
            if save:
                # import csv
                
                filename = 'inputs-'+inputs['Run Name']+'.json'    

        
                with open(filename, 'w') as file:
                    json.dump(inputs, file)

        if verbose:
            
            format_string = '{:35s} {:8.2f}'
            
            print('{:35s} {:8s}'.format('Parameter', 'Value'))
            
            for key in inputs:
                print(format_string.format(key, inputs[key]))
            
        return(inputs)
    @staticmethod
    def create_radial_build(name, material, thickness, f_vol=1.00):
            
        new_data = pd.DataFrame(data={
            'name':[name], 
            'material':[material], 
            'r_in':[0.0], 
            'r_out':[thickness],
            'f_vol':[f_vol]})
        
        return(new_data)
    @staticmethod
    def add_new_layer(data, name, material, thickness, f_vol=1.00):
        
        # Inner radius is outer radius from last row
        r_in = data['r_out'].values[-1]

        new_data = pd.DataFrame(data={
            'name':[name], 
            'material':[material], 
            'r_in':[r_in], 
            'r_out':[r_in+thickness],
            'f_vol':[f_vol]})
        
        return(pd.concat([data, new_data], ignore_index=True))
    @staticmethod
    def add_fractional_layer(data, name, material, f_vol=1.00):
        
        # Inner radius is inner radius from last row
        r_in = data['r_in'].values[-1]
        r_out = data['r_out'].values[-1]

        new_data = pd.DataFrame(data={
            'name':[name], 
            'material':[material], 
            'r_in':[r_in], 
            'r_out':[r_out],
            'f_vol':[f_vol]})
        
        return(pd.concat([data, new_data], ignore_index=True))
    @staticmethod
    def build_central_cell(inputs):

        radial_build = MirrorFunc.create_radial_build('Plasma', 'DT', inputs['Central Cell Plasma Radius'])
        radial_build = MirrorFunc.add_new_layer(radial_build, 'Gap', 'vacuum', inputs['Central Cell Vacuum Gap'])
        radial_build = MirrorFunc.add_new_layer(radial_build, 'First Wall', inputs['First Wall Material'], inputs['First Wall Thickness'])
        radial_build = MirrorFunc.add_new_layer(radial_build, 'Vacuum Vessel', inputs['Vacuum Vessel Material'], inputs['Vacuum Vessel Thickness'])
        radial_build = MirrorFunc.add_new_layer(radial_build, 'Multiplier', inputs['Multiplier Material'], inputs['Multiplier Thicnkess'])
        radial_build = MirrorFunc.add_new_layer(radial_build, 'Blanket Coolant', inputs['Blanket Coolant Material'], inputs['Blanket Thickness'], inputs['Blanket Coolant Fraction'])
        radial_build = MirrorFunc.add_fractional_layer(radial_build, 'Blanket Structure', inputs['Blanket Structural Material'], inputs['Blanket Structrual Fraction'])
        radial_build = MirrorFunc.add_new_layer(radial_build, 'Outer Vessel', inputs['Vacuum Vessel Material'], inputs['Outer Vessel Thickness'])

        return(radial_build)  

    @staticmethod
    def central_cell_cost(inputs, L=1.0):
        return(MirrorFunc.central_cell(inputs, L=L)['cost'].max())

    @staticmethod
    def central_cell(inputs, L=1.0):
        
        filename = inputs['Cost File']
        
        cost_data = pd.read_csv(filename, index_col=0)
        
        radial_build = MirrorFunc.build_central_cell(inputs)
        

        
        T = 300 # °C, mean coolant temperture
        
        radial_build['volume'] = np.pi * L * (radial_build['r_out']**2 - radial_build['r_in']**2) * radial_build['f_vol']
        
        # print(radial_build.to_string())

        # print(radial_build)
        
        # Iterate over layer in radial build and calculate volume and cost
        for i in range(len(radial_build)):
    
            material = radial_build['material'][i]
            # print(material)
            
            '''
            PbLi is a special case as the enrichment and temperature affect
            the density and cost. Here the code expects a percent enrichment as
            shown here:
                'Natural PbLi' meaning '7.5% PbLi'
                '93% PbLi' or similar
            '''
            if 'PbLi' in material:
                
                if 'Natural' in material:
                    f_6Li = 0.075
                elif '% ' in material:
                    f_6Li = float(material.split('% ')[0])/100
                else:
                    print('Unable to parse coolant', material)

                radial_build.loc[i, 'density'] = MirrorFunc.PbLi_density(f_6Li=f_6Li, T=T)
                radial_build.loc[i, 'price'] = MirrorFunc.PbLi_price(f_6Li, cost_data.loc['Pb']['price'])
                radial_build.loc[i, 'manufacturing_factor'] = 1.0


            else:
    
                radial_build.loc[i, 'density'] = cost_data.loc[material]['density']
                radial_build.loc[i, 'price'] = cost_data.loc[material]['price']
                radial_build.loc[i, 'manufacturing_factor'] = cost_data.loc[material]['manufacturing_factor']

                
            
            radial_build.loc[i, 'mass'] = radial_build['volume'][i] * radial_build['density'][i] 
            radial_build.loc[i, 'cost'] = radial_build['price'][i] * radial_build['mass'][i] * radial_build['manufacturing_factor'][i]
        
        # Add totals to last row
        radial_build = pd.concat([radial_build, pd.DataFrame(data={
            'name':['Total'],
            'cost':[radial_build['cost'].sum()],
            'mass':[radial_build['mass'].sum()]})], ignore_index=True)
        
        radial_build['cost_percent'] = 100 * radial_build['cost'] / radial_build['cost'].max()
        # print()
        # print('Radial build for L =', L)
        # print(radial_build.to_string())
        
        return(radial_build)

        # Return total cost only
        # return(radial_build['cost'].max())

    @staticmethod
    def expander_cell_cost(inputs):
        """
        Each expander cell is made up of:
            A cylindrical vessel
            A DEC convertor
            

        Returns
        -------
        None.
        
        """
        
        # print('Expander Cell')
        
        L = inputs['Expander Cell Length']
        radius = inputs['Expander Cell Radius']
        thickness = inputs['Expander Cell Vessel Thickness']
        vv_material = inputs['Expander Cell Vessel Material']
        
        filename = inputs['Cost File']
        
        cost_data = pd.read_csv(filename, index_col=0)
        
        # Cylindrical shell
        
        radial_build = MirrorFunc.create_radial_build('Gap', 'vacuum', radius)
        radial_build = MirrorFunc.add_new_layer(radial_build, 'Vacuum Vessel', vv_material, thickness)
        
        radial_build['volume'] = np.pi * L * (radial_build['r_out']**2 - radial_build['r_in']**2) * radial_build['f_vol']

        for i in range(len(radial_build)):
    
            material = radial_build['material'][i]
            radial_build.loc[i, 'density'] = cost_data.loc[material]['density']
            radial_build.loc[i, 'price'] = cost_data.loc[material]['price']
            radial_build.loc[i, 'manufacturing_factor'] = cost_data.loc[material]['manufacturing_factor']
            radial_build.loc[i, 'mass'] = radial_build['volume'][i] * radial_build['density'][i] 
            radial_build.loc[i, 'cost'] = radial_build['price'][i] * radial_build['mass'][i] * radial_build['manufacturing_factor'][i]
        
        # Add totals to last row
        radial_build = pd.concat([radial_build, pd.DataFrame(data={
            'name':['Total'],
            'cost':[radial_build['cost'].sum()],
            'mass':[radial_build['mass'].sum()]})])
        
        radial_build['cost_percent'] = 100 * radial_build['cost'] / radial_build['cost'].max()
        
        # print(radial_build.to_string())

        # End cap
        V_end_cap = np.pi * thickness * radius**2
        M_end_cap = V_end_cap * cost_data.loc[vv_material]['density']
        C_end_cap = M_end_cap * cost_data.loc[vv_material]['price'] * cost_data.loc[vv_material]['manufacturing_factor']

        # print('End Cap: $', C_end_cap)  
        # print('Cylindrical Part: $', radial_build['cost'].max())
        
        total = 2*C_end_cap + radial_build['cost'].max()
        
        # print('Total: $', total)
        
        return(total)

    @staticmethod
    def HF_magnet_shield_cost(inputs, verbose=False):
        """
        The HF coils have annular shield with a U-shaped cross section:
        
                +----+--------+----+
                |    |xxxxxxxx|    |
                |    |xxxxxxxx|    |
                |    |xxxxxxxx|    |
                |    |xxxxxxxx|    |
                |    |xxxxxxxx|    |
                +----+--------+----+
                \   |        |   /
                \  |        |  /
                    \ |        | /
                    \|        |/ 
                    +--------+
                    
                
                - - - - - - - - - - - Center Line    
                
                
                    +--------+
                    /|        |\
                    / |        | \
                /  |        |  \
                /   |        |   \
                +----+--------+----+
                |    |xxxxxxxx|    |
                |    |xxxxxxxx|    |
                |    |xxxxxxxx|    |
                |    |xxxxxxxx|    |
                |    |xxxxxxxx|    |
                +----+--------+----+    
        

        """
        
        # Shielding thickness should be on the same order as the bore radius (~30 cm - 1m)
        # It's a reasonable assumption to say that all axial widths/layers will be the same


        filename = inputs['Cost File']
        cost_data = pd.read_csv(filename, index_col=0)    

        # Eventually these will be arguments
        material = 'W'
        a_M = 0.15 # From Frank
        a_CC = 0.54 # From Frank
        a_0 = 0.7 

        # Radially Inner Cylinder
        # length = 4.5 # End plug length from Frank
        length = 0.5 # Is this the required shielding thickness?
        a_M = 0.15 
        r_gap = 0.1 # General advice via Hitarth: lower inner radius -> thicker shielding
        r_vv = 0.01 # Reduced from 0.1 to 0.01
        
        # r_magnet = 1.0 # original
        r_magnet = 1.5 # From Frank and confirmed (1.45) in magnet cost guesses
        r_cryostat = 1.0
        
        f_vol = 0.90
        
        
        r_in = a_M + r_gap + r_vv
        r_out = r_magnet - r_cryostat
        
        V_radially_inner_cylinder = MirrorFunc.V_cylindrical_shell(r_in, r_out, length) * f_vol

        # Central Cell Cylinder
        # length_cc_cylinder = 50.0
        length_cc_cylinder = 0.5
        r_in_cc = a_CC + r_gap + r_vv
        # r_out_cc = 1.0
        r_out_cc = r_in_cc+0.5

        V_cc_cylinder = MirrorFunc.V_cylindrical_shell(r_in_cc, r_out_cc, length_cc_cylinder) * f_vol
        
        # Central Cell Triangular Washer
        V_cc_triangle = MirrorFunc.V_inverse_triangular_washer(length_cc_cylinder, r_in, r_in_cc) * f_vol
        
        # End Plug Cylinder
        length_ep_cylinder = 0.5 # From Frank
        r_in_ep = a_0 + r_gap + r_vv
        r_out_ep = r_in_ep + 0.5

        V_ep_cylinder = MirrorFunc.V_cylindrical_shell(r_in_ep, r_out_ep, length_ep_cylinder) * f_vol
        
        # End Cell Triangular Washer
        V_ep_triangle = MirrorFunc.V_inverse_triangular_washer(length_ep_cylinder, r_in, r_in_ep) * f_vol

        # For central cell facing magnet, add up all five regions
        V_total_cc_facing = V_radially_inner_cylinder + V_cc_cylinder + V_cc_triangle + V_ep_cylinder + V_ep_triangle

        # For expander cell facing magnet, only add up three regions
        # No neutrons come from the expander cell
        V_total_ec_facing = V_radially_inner_cylinder +  V_ep_cylinder + V_ep_triangle

        # Summary information
        V_total = V_total_cc_facing + V_total_ec_facing
        mass = cost_data.loc[material]['density'] * V_total
        cost = cost_data.loc[material]['price'] * cost_data.loc[material]['manufacturing_factor'] * mass

        return(cost)
    

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
    def HF_magnet_cost(inputs, HF_field=25.0, inner_rad=50):
        # This is the HF cost per magnet [MUSD], not for all four

        # cost = 29.10 # Assuming ARPA number for WHAM magnet cost, 5x width, using PROCESS J_crit
        cost = MirrorFunc.HTS_storedEnergy(HF_field, inner_rad)
        cost_factor = (0.70)**(np.log((inputs['Unit Number']-1)*inputs['HF Magnet Number'] + 1)/np.log(2))
        
        return(cost * cost_factor)

    @staticmethod
    def LF_magnet_cost(inputs, LF_field=10.0, inner_rad=50):
        # This is the LF cost per magnet [MUSD]

        cost = MirrorFunc.HTS_storedEnergy(LF_field, inner_rad)
        cost_factor = (0.70)**(np.log((inputs['Unit Number']-1)*inputs['LF Magnet Number'] + 1)/np.log(2))
        
        return(cost * cost_factor)

    @staticmethod
    def CF_magnet_cost(inputs, CF_field=3.0):
        # This is the CF cost per magnet [MUSD]
        
        convert_to_currentDollar = 1.31
        cost = 0.7*CF_field*convert_to_currentDollar # Assuming 700k/Tesla in 2016 dollars with 3T LTS
        cost_factor = (0.70)**(np.log((inputs['Unit Number']-1)*inputs['CF Magnet Number'] + 1)/np.log(2))
        
        return(cost * cost_factor)




    
