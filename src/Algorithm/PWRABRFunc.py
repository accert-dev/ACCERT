import numpy as np
from .Algorithm import Algorithm


ALGORITHM_METADATA = {
    'sum_multi_accounts': {'ind': 1, 'alg_name': 'sum_multi_accounts', 'alg_for': 'c', 'alg_description': 'sum of multiple accounts', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'sum(account_1,account_2...account_n)', 'alg_units': 'million', 'variables': 'account1, account2.accountn', 'constants': None},
    'sum_multi_weights': {'ind': 2, 'alg_name': 'sum_multi_weights', 'alg_for': 'v', 'alg_description': 'sum of multiple weights ', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'sum(Weight_1+Weight_2...Weight_n)', 'alg_units': 'ton', 'variables': 'weight1,weight2weight3,weit4,weight5', 'constants': None},
    'sum_multi_pumps': {'ind': 3, 'alg_name': 'sum_multi_pumps', 'alg_for': 'c', 'alg_description': 'sum cost of multiple pumps', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'sum(Pump_1+Pump_2+Pump_n)', 'alg_units': 'million', 'variables': 'pump1,pump2,pump3,pump4,pump5', 'constants': None},
    'ptn_account': {'ind': 4, 'alg_name': 'ptn_account', 'alg_for': 'c', 'alg_description': 'portion of account cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'account_cost*portion', 'alg_units': 'million', 'variables': 'c_ref,prn_fac', 'constants': None},
    'unit_weights': {'ind': 5, 'alg_name': 'unit_weights', 'alg_for': 'c', 'alg_description': 'unit cost of weight', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'weight_of_carbon_steel*0.14+weight_of_stainless_steel*0.31', 'alg_units': 'million', 'variables': 'Csweight, Ssweight', 'constants': '0.140000, 0.310000'},
    'pump': {'ind': 6, 'alg_name': 'pump', 'alg_for': 'v', 'alg_description': 'cost per pump based on ref', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'ref_cost_of_pump*(CH_of_pump/CH_of_ref)^scale_of_power', 'alg_units': 'million', 'variables': 'c_pump_ref,CH,CH_ref,scale', 'constants': None},
    'containment': {'ind': 7, 'alg_name': 'containment', 'alg_for': 'c', 'alg_description': 'containment calculation', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'containment structure + equipment + others', 'alg_units': 'million', 'variables': 'NOT YET', 'constants': None},
    'MWth_scale': {'ind': 8, 'alg_name': 'MWth_scale', 'alg_for': 'c', 'alg_description': 'thermal power scale from pwr12be', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'cost_of_ref*(thermal_power/thermal_power_of_ref)^thermal_power_scale', 'alg_units': 'million', 'variables': 'c_ref,mwth,scale', 'constants': '3431'},
    'unit_volume': {'ind': 9, 'alg_name': 'unit_volume', 'alg_for': 'c', 'alg_description': 'cost by unit volume', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'dollar_cost_per_unit_vol*vol/1000000', 'alg_units': 'million', 'variables': 'V1_unit_vol, V2_vol', 'constants': None},
    'dev_factor_ref': {'ind': 10, 'alg_name': 'dev_factor_ref', 'alg_for': 'c', 'alg_description': 'factor of the reference', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'cost_of_ref*scale/factor', 'alg_units': 'million', 'variables': 'c_ref,scale,n', 'constants': None},
    'tur_exp_n': {'ind': 11, 'alg_name': 'tur_exp_n', 'alg_for': 'v', 'alg_description': 'scaling exponent law ', 'alg_python': 'PWRABRFunc', 'alg_formulation': '(-0.0032) *v_1+ 1.2497', 'alg_units': '1', 'variables': 'p_in', 'constants': None},
    'esc_1987': {'ind': 12, 'alg_name': 'esc_1987', 'alg_for': 'c', 'alg_description': 'escalate from 1987', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'escalator*cost_in_1987', 'alg_units': 'million', 'variables': 'escalate_1987,refCost', 'constants': None},
    'cost_by_weight': {'ind': 13, 'alg_name': 'cost_by_weight', 'alg_for': 'c', 'alg_description': 'per-unit mass costs', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'tol_weight*coat_per_unit', 'alg_units': 'million', 'variables': 'tolweight, unitcost', 'constants': None},
    'default_0': {'ind': 14, 'alg_name': 'default_0', 'alg_for': 'c', 'alg_description': 'default as 0', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'set the total cost to 0', 'alg_units': 'million', 'variables': None, 'constants': '0'},
    'rpv_mass': {'ind': 15, 'alg_name': 'rpv_mass', 'alg_for': 'v', 'alg_description': 'mass of RPV', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'weight_of_carbon_steel+weight_of_stainless_steel', 'alg_units': 'ton', 'variables': 'c_221.12_cs_weight,c_221.12_ss_weight', 'constants': None},
    'unit_facility': {'ind': 16, 'alg_name': 'unit_facility', 'alg_for': 'c', 'alg_description': 'per-unit facility costs', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'no_of_facility*cost_per_facility', 'alg_units': 'million', 'variables': 'no_of_unit, unitcost', 'constants': None},
    'MWe_scale': {'ind': 17, 'alg_name': 'MWe_scale', 'alg_for': 'c', 'alg_description': 'electric power scale from pwr12be', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'cost_of_ref*(electric_power/electric_power_of_ref)^electric_power_scale', 'alg_units': 'million', 'variables': 'c_ref,mwe,scale', 'constants': '1144'},
    'unit_weights_plate': {'ind': 18, 'alg_name': 'unit_weights_plate', 'alg_for': 'c', 'alg_description': 'unit cost of weight with plate installation', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'weight_of_carbon_steel_plate_install*0.075+weight_of_stainless_steel*0.31', 'alg_units': 'million', 'variables': 'Csweight_plate, Ssweight', 'constants': '0.075000, 0.310000'},
    'esc_1978': {'ind': 19, 'alg_name': 'esc_1978', 'alg_for': 'c', 'alg_description': 'escalate from 1978', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'escalator*cost_in_1978', 'alg_units': 'million', 'variables': 'escalate_1978,refCost', 'constants': None},
    'total_weight_prn': {'ind': 20, 'alg_name': 'total_weight_prn', 'alg_for': 'c', 'alg_description': 'unit cost of total weight by portion', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'tol_weight*(portion_of_carbon_steel*0.075+portion_of_stainless_steel*0.31)*no_of_facility', 'alg_units': 'million', 'variables': 'V1_totweight, V2_csprn,V3_ssprn,V4_no_of_facility', 'constants': '0.075000, 0.310000'},
    'unit_weights_factor': {'ind': 21, 'alg_name': 'unit_weights_factor', 'alg_for': 'c', 'alg_description': 'unit cost of weight with factor', 'alg_python': 'PWRABRFunc', 'alg_formulation': '(weight_of_carbon_steel_plate_install*0.075+weight_of_stainless_steel*0.31)*factor', 'alg_units': 'million', 'variables': 'Csweight, Ssweight,factor', 'constants': '0.075000, 0.310000'},
    'factor_sum': {'ind': 22, 'alg_name': 'factor_sum', 'alg_for': 'c', 'alg_description': 'sum of multiple accounts with factor', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'factor*prn*sum(account_2..account_n)', 'alg_units': 'million', 'variables': 'factor1, portion,account2.accountn', 'constants': None},
    'complex': {'ind': 23, 'alg_name': 'complex', 'alg_for': 'c', 'alg_description': 'complex algorithm', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'simple cost', 'alg_units': 'million', 'variables': 'cost', 'constants': None},
    'MWth_lmfbrscale': {'ind': 24, 'alg_name': 'MWth_lmfbrscale', 'alg_for': 'c', 'alg_description': 'thermal power scale from lmfbr', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'cost_of_ref*(thermal_power/thermal_power_of_LMFBR)^thermal_power_scale', 'alg_units': 'million', 'variables': 'c_ref,mwth,scale', 'constants': '2287'},
    'MWreth_scale': {'ind': 25, 'alg_name': 'MWreth_scale', 'alg_for': 'c', 'alg_description': 'rejected thermal power scale from pwr12be', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'cost_of_ref*(rejected_hermal_power/rejected_thermal_power_of_LMFBR)^thermal_power_scale', 'alg_units': 'million', 'variables': 'c_ref,mwreth,scale', 'constants': '3800'},
    'Sgsum': {'ind': 26, 'alg_name': 'Sgsum', 'alg_for': 'c', 'alg_description': 'sum the SG cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'weight*unitcost*unit', 'alg_units': 'million', 'variables': 'sg_weight, c_unit, no_unit ', 'constants': None},
    'containmentsum': {'ind': 27, 'alg_name': 'containmentsum', 'alg_for': 'c', 'alg_description': 'NOT YET', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'NOT implemented YET', 'alg_units': 'million', 'variables': 'NOT YET', 'constants': None},
    'inside_rad': {'ind': 28, 'alg_name': 'inside_rad', 'alg_for': 'v', 'alg_description': 'calculate inside radius', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'radius_out-thickness', 'alg_units': 'm', 'variables': 'r_out, t', 'constants': None},
    'round_surface': {'ind': 29, 'alg_name': 'round_surface', 'alg_for': 'v', 'alg_description': 'calculate surface base on radius', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'radius', 'alg_units': 'm^2', 'variables': 'r', 'constants': 'PI'},
    'basemat_volume': {'ind': 30, 'alg_name': 'basemat_volume', 'alg_for': 'v', 'alg_description': 'calculate basemat volume base on surface', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'basemat_surface*thickness', 'alg_units': 'm^3', 'variables': 'S,t', 'constants': None},
    'wall_height': {'ind': 31, 'alg_name': 'wall_height', 'alg_for': 'v', 'alg_description': 'calculate wall height base on total height', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'total_height-roof_rad', 'alg_units': 'm', 'variables': None, 'constants': None},
    'walls_surface': {'ind': 32, 'alg_name': 'walls_surface', 'alg_for': 'v', 'alg_description': 'calculate Walls surface', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'Cont_H_wall_m*2*PI()*(Cont_rad_out_m+Cont_rad_in_m)', 'alg_units': 'm^2', 'variables': None, 'constants': None},
    'wall_volume': {'ind': 33, 'alg_name': 'wall_volume', 'alg_for': 'v', 'alg_description': 'calculate Walls volume', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'Cont_H_wall_m*PI()*(Cont_rad_out_m^2-Cont_rad_in_m^2)', 'alg_units': 'm^3', 'variables': None, 'constants': None},
    'dome_inside_diameter ': {'ind': 34, 'alg_name': 'dome_inside_diameter ', 'alg_for': 'v', 'alg_description': 'calculate Dome inside diameter ', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'Cont_rad_out_m-B10', 'alg_units': 'm', 'variables': None, 'constants': None},
    'roof_surface': {'ind': 35, 'alg_name': 'roof_surface', 'alg_for': 'v', 'alg_description': 'calculate Roof surface', 'alg_python': 'PWRABRFunc', 'alg_formulation': '0.5*4*PI()*(Cont_rad_out_m^2+Dome_rad_in_m^2)', 'alg_units': 'm^2', 'variables': None, 'constants': None},
    'roof_volume': {'ind': 36, 'alg_name': 'roof_volume', 'alg_for': 'v', 'alg_description': 'calculate Roof volume', 'alg_python': 'PWRABRFunc', 'alg_formulation': '0.5*4/3*PI()*(Cont_rad_out_m^3-Dome_rad_in_m^3)', 'alg_units': 'm^3', 'variables': None, 'constants': None},
    'tot_internal_volume': {'ind': 37, 'alg_name': 'tot_internal_volume', 'alg_for': 'v', 'alg_description': 'calculate Tot internal Volume', 'alg_python': 'PWRABRFunc', 'alg_formulation': '(PI()*Cont_rad_in_m^2*Cont_H_wall_m)+(0.5*(4/3)*PI()*Dome_rad_in_m^3)', 'alg_units': 'm^3', 'variables': None, 'constants': None},
    'building_internal_volume': {'ind': 38, 'alg_name': 'building_internal_volume', 'alg_for': 'v', 'alg_description': 'calculate Building internal volume', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'Intern_tot_v_m3*(1-Void_fraction)', 'alg_units': 'm^3', 'variables': None, 'constants': None},
    'building_internal _surface': {'ind': 39, 'alg_name': 'building_internal _surface', 'alg_for': 'v', 'alg_description': 'calculate Building internal surface', 'alg_python': 'PWRABRFunc', 'alg_formulation': '2*Internal_v_m3/B11', 'alg_units': 'm^2', 'variables': None, 'constants': None},
    'volume_of_the_structures ': {'ind': 40, 'alg_name': 'volume_of_the_structures ', 'alg_for': 'v', 'alg_description': 'calculate volume of the structures ', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'Basemat_v_m3+Walls_v_m3+Dome_v_m3+Internal_v_m3', 'alg_units': 'm^3', 'variables': None, 'constants': None},
    'Inside_liner_surface': {'ind': 41, 'alg_name': 'Inside_liner_surface', 'alg_for': 'v', 'alg_description': 'calculate Inside liner surface', 'alg_python': 'PWRABRFunc', 'alg_formulation': '(Cont_rad_in_m^2*PI())+(Cont_H_wall_m*2*PI()*Cont_rad_in_m)+(0.5*4*PI()*Dome_rad_in_m^2)', 'alg_units': 'm^2', 'variables': None, 'constants': None},
    'liner_Surface': {'ind': 42, 'alg_name': 'liner_Surface', 'alg_for': 'v', 'alg_description': 'calculate Liner Surface', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'Inside_liner_s*liner_fraction', 'alg_units': 'm^2', 'variables': None, 'constants': None},
    'painted_surface': {'ind': 43, 'alg_name': 'painted_surface', 'alg_for': 'v', 'alg_description': 'calculate painted surface', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'Inside_liner_s+(Cont_H_wall_m*2*PI()*Cont_rad_out_m)+(0.5*4*PI()*Cont_rad_out_m^2)+Internal_s_m2', 'alg_units': 'm^2', 'variables': None, 'constants': None},
    'Inflation_rate': {'ind': 44, 'alg_name': 'Inflation_rate', 'alg_for': 'v', 'alg_description': 'calculate Inflation rate', 'alg_python': 'PWRABRFunc', 'alg_formulation': '1.03^(1996-1987)*CPI', 'alg_units': '1', 'variables': None, 'constants': None},
    'unitcost_v_eedb_to_accert': {'ind': 45, 'alg_name': 'unitcost_v_eedb_to_accert', 'alg_for': 'v', 'alg_description': 'unit cost volume from EEDB with inflation', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'unitcost_EEDB_v*infl', 'alg_units': 'dollar/m^3', 'variables': None, 'constants': None},
    'unitcost_s_eedb_to_accert': {'ind': 46, 'alg_name': 'unitcost_s_eedb_to_accert', 'alg_for': 'v', 'alg_description': 'unit cost surface from EEDB with inflation', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'unitcost_EEDB_s*infl', 'alg_units': 'dollar/m^2', 'variables': None, 'constants': None},
    'tol_contaiment_ce_cost': {'ind': 47, 'alg_name': 'tol_contaiment_ce_cost', 'alg_for': 'v', 'alg_description': 'total cost for each part of cotiament', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'unitcost*number_of stucture_unit', 'alg_units': 'dollar', 'variables': None, 'constants': None},
    'sum_ce': {'ind': 48, 'alg_name': 'sum_ce', 'alg_for': 'v', 'alg_description': 'sum of multiple costelement', 'alg_python': 'PWRABRFunc', 'alg_formulation': 'sum(cost_element_1,cost_element2,cost_element_n)', 'alg_units': 'dollar', 'variables': None, 'constants': None},
    'Yardwork_cost': {'ind': 49, 'alg_name': 'Yardwork_cost', 'alg_for': 'c', 'alg_description': 'the cost of the land 2017', 'alg_python': 'PWRABRFunc', 'alg_formulation': '81.5*land_surface_area', 'alg_units': 'dollar', 'variables': 'land_surface_area', 'constants': '81.5'},
    'Reactor_containment_mat_cost': {'ind': 50, 'alg_name': 'Reactor_containment_mat_cost', 'alg_for': 'c', 'alg_description': 'Reactor_containment_mat_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '130.8*containment_subVolume', 'alg_units': 'dollar', 'variables': 'containment_subVolume', 'constants': '130.8'},
    'Reactor_containment_lab_cost': {'ind': 51, 'alg_name': 'Reactor_containment_lab_cost', 'alg_for': 'c', 'alg_description': 'Reactor_containment_lab_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '915.6*Containment_hole_volume', 'alg_units': 'dollar', 'variables': 'Containment_hole_volume', 'constants': '915.6'},
    'Building_and_utilities_mat_cost': {'ind': 52, 'alg_name': 'Building_and_utilities_mat_cost', 'alg_for': 'c', 'alg_description': 'Building_and_utilities_mat_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '6458.3*Turbine_building_surface_area', 'alg_units': 'dollar', 'variables': 'Turbine_building_surface_area', 'constants': '6458.3'},
    'Building_and_utilities_lab_cost': {'ind': 53, 'alg_name': 'Building_and_utilities_lab_cost', 'alg_for': 'c', 'alg_description': 'Building_and_utilities_lab_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '9843*Distance_to_utilities+10000*Number_of_shipping_containers', 'alg_units': 'dollar', 'variables': 'Distance_to_utilities, Number_of_shipping_containers', 'constants': '9843, 10000'},
    'Reactor_startup_facility_cost': {'ind': 54, 'alg_name': 'Reactor_startup_facility_cost', 'alg_for': 'c', 'alg_description': 'Reactor_startup_facility_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '7600*Battery_capacity_required+1100', 'alg_units': 'dollar', 'variables': 'Battery_capacity_required', 'constants': '7600, 1100'},
    'Outer_vessel_mat_cost': {'ind': 55, 'alg_name': 'Outer_vessel_mat_cost', 'alg_for': 'c', 'alg_description': 'Outer_vessel_mat_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '310000*primary_outer_vessel_SS_mass', 'alg_units': 'dollar', 'variables': 'primary_outer_vessel_SS_mass', 'constants': '310000'},
    'Outer_vessel_lab_cost': {'ind': 56, 'alg_name': 'Outer_vessel_lab_cost', 'alg_for': 'c', 'alg_description': 'Outer_vessel_lab_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '14080*primary_outer_vessel_SS_mass', 'alg_units': 'dollar', 'variables': 'primary_outer_vessel_SS_mass', 'constants': '14080'},
    'Inner_vessel_cost': {'ind': 57, 'alg_name': 'Inner_vessel_cost', 'alg_for': 'c', 'alg_description': 'Inner_vessel_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '310000*primary_inner_vessel_SS_mass', 'alg_units': 'dollar', 'variables': 'primary_inner_vessel_SS_mass', 'constants': '310000'},
    'Reactivity_control_system_cost': {'ind': 58, 'alg_name': 'Reactivity_control_system_cost', 'alg_for': 'c', 'alg_description': 'Reactivity_control_system_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '950*B4C_total_neutron_poison_mass_Kg+610000*(Number_of_control_rod_drums+number_of_emergency_control_rods)', 'alg_units': 'dollar', 'variables': 'B4C_total_neutron_poison_mass_Kg, Number_of_control_rod_drums, number_of_emergency_control_rods', 'constants': '950, 610000'},
    'Reflector_cost': {'ind': 59, 'alg_name': 'Reflector_cost', 'alg_for': 'c', 'alg_description': 'Reflector_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '310000*stainless_steel_316_reflector_mass+120000*Al2O3_reflector_mass+1000000*BeO_reflector_mass', 'alg_units': 'dollar', 'variables': 'stainless_steel_316_reflector_mass, Al2O3_reflector_mass, BeO_reflector_mass', 'constants': '310000, 120000, 1000000'},
    'Shield_cost': {'ind': 60, 'alg_name': 'Shield_cost', 'alg_for': 'c', 'alg_description': 'Shield_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '949.9*shield_B4C_mass', 'alg_units': 'dollar', 'variables': 'shield_B4C_mass', 'constants': '949.9'},
    'Moderator_cost': {'ind': 61, 'alg_name': 'Moderator_cost', 'alg_for': 'c', 'alg_description': 'Moderator_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '310000*moderator_ZrH_mass', 'alg_units': 'dollar', 'variables': 'moderator_ZrH_mass', 'constants': '310000'},
    'cooling_heat_pipes_cost': {'ind': 62, 'alg_name': 'cooling_heat_pipes_cost', 'alg_for': 'c', 'alg_description': 'cooling_heat_pipes_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '10000*number_of_core_cooling_heat_pipes*(1-mass_production_cost_reduction_factor)', 'alg_units': 'dollar', 'variables': 'number_of_core_cooling_heat_pipes, mass_production_cost_reduction_factor', 'constants': '10000'},
    'heat_exchangers_mat_cost': {'ind': 63, 'alg_name': 'heat_exchangers_mat_cost', 'alg_for': 'c', 'alg_description': 'heat_exchangers_mat_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '50000*number_of_heat_exchangers', 'alg_units': 'dollar', 'variables': 'number_of_heat_exchangers', 'constants': '50000'},
    'heat_exchangers_lab_cost': {'ind': 64, 'alg_name': 'heat_exchangers_lab_cost', 'alg_for': 'c', 'alg_description': 'heat_exchangers_lab_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '530000*number_of_heat_exchangers', 'alg_units': 'dollar', 'variables': 'number_of_heat_exchangers', 'constants': '530000'},
    'heat_exchangers_fac_cost': {'ind': 65, 'alg_name': 'heat_exchangers_fac_cost', 'alg_for': 'c', 'alg_description': 'heat_exchangers_fac_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '120000*number_of_heat_exchangers*heat_exchangers_mass', 'alg_units': 'dollar', 'variables': 'number_of_heat_exchangers, heat_exchangers_mass', 'constants': '120000'},
    'instrumentation_contorl_cost': {'ind': 66, 'alg_name': 'instrumentation_contorl_cost', 'alg_for': 'c', 'alg_description': 'instrumentation_contorl_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '2000*number_of_IO_sensors+6500000', 'alg_units': 'dollar', 'variables': 'number_of_IO_sensors', 'constants': '2000'},
    'turb_and_elec_sys_cost': {'ind': 67, 'alg_name': 'turb_and_elec_sys_cost', 'alg_for': 'c', 'alg_description': 'turb_and_elec_sys_cost', 'alg_python': 'PWRABRFunc', 'alg_formulation': '282553*mwth+ 213800000*(pow(mwe/1144, 0.4) + pow(mwth/3431, 0.8))', 'alg_units': 'dollar', 'variables': 'mwth, mwe', 'constants': '282553, 1144, 0.4, 3431, 0.8'},
}

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
