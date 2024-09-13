ChildExactlyOne = [ accert ]
accert{
    Description = "[optional] for accert calculations"
    MinOccurs = 0
    MaxOccurs = 1
    InputTmpl = "accert"
    ref_model{
        Description = "[required] User input reference model"
        MinOccurs = 1
        MaxOccurs = 1
        InputTmpl = "ref_model"
        ValType = String
        ValEnums = [ "PWR12-BE" "ABR1000" "LFR", "heatpipe"]
        }            

    power{
        Description = "[required] User input power"
        MinOccurs = 1
        MaxOccurs = NoLimit
        InputTmpl = "power"
        id{
            MinOccurs = 1
            MaxOccurs = 1
            ValType = String
            ValEnums = [ Thermal Electric]
        }
        value{
            Description = "[required] variable value "
            MinOccurs = 1
            MaxOccurs = 1
            ValType = Real
            MinValExc = 0
            MaxValExc = NoLimit
        }
        unit{
            Description = "[required] variable unit "
            MinOccurs = 1
            MaxOccurs = 1
            ValType = String
            ValEnums = [ W kW MW]
        }
    }
    var{
        Description = "changed variable value"
        MinOccurs = 0
        MaxOccurs = NoLimit
        InputTmpl = "var"
        id{
            MinOccurs = 1
            MaxOccurs = 1
            ValType = String
            ValEnums = ['number_of_IO_sensors', 'heat_exchangers_mass', 'number_of_heat_exchangers', 'number_of_core_cooling_heat_pipes', 'mass_production_cost_reduction_factor', 'moderator_ZrH_mass', 'shield_B4C_mass', 'BeO_reflector_mass', 'Al2O3_reflector_mass', 'stainless_steel_316_reflector_mass', 'number_of_emergency_control_rods', 'Number_of_control_rod_drums', 'B4C_total_neutron_poison_mass_Kg', 'primary_inner_vessel_SS_mass', 'primary_outer_vessel_SS_mass', 'Battery_capacity_required', 'Number_of_shipping_containers' ,'Distance_to_utilities','Turbine_building_surface_area', 'Containment_hole_volume', 'containment_subVolume', 'land_surface_area' ,'c_213_fac' 'c_213_lab' 'c_213_mat' 'c_220A.2121_ss_weight' 'c_220A.2122_ss_weight' 'c_220A.222_ss_weight' 'c_222_fac' 'c_222_lab' 'c_222_mat' 'c_222.11_fac' 'c_222.11_lab' 'c_222.11_mat' 'c_222.12_fac' 'c_222.12_lab' 'c_222.12_mat' 'c_222.13_fac' 'c_222.14_fac' 'c_222.14_lab' 'c_222.14_mat' 'c_231_fac' 'c_231_lab' 'c_231_mat' 'c_233_fac' 'c_233_lab' 'c_233_mat' 'c_241_fac' 'c_241_lab' 'c_241_mat' 'c_242_fac' 'c_242_lab' 'c_242_mat' 'c_245_fac' 'c_245_lab' 'c_245_mat' 'c_246_fac' 'c_246_lab' 'c_246_mat' 'c_262_fac' 'c_262_lab' 'c_262_mat' 'c_cr_per_unit_fac' 'c_crd_per_unit_fac' 'c_pump_ap1000' 'c_pump_per_unit_fac' 'c_turbine' 'c_zero' 'CH_abr1000' 'CH_AP1000' 'escalate_1987' 'mwe' 'mwreth' 'mwth' 'no_of_cr' 'no_of_crd' 'no_of_rcpump' 'prn_235_of_231_fac' 'prn_235_of_231_lab' 'prn_235_of_231_mat' 'prn_fac_231_lab' 'prn_fac_231_mat' 'r_222.13_lab' 'r_222.13_mat' 'r_78_220A224_fac' 'r_78_226.4_fac' 'ref_211_fac' 'ref_211_lab' 'ref_211_mat' 'ref_224_fac' 'ref_224_lab' 'ref_224_mat' 'ref_227_fac' 'ref_227_lab' 'ref_227_mat' 'ref_252_fac' 'ref_252_lab' 'ref_252_mat' 'scale_0.4' 'scale_0.52' 'scale_0.8' 'scale_1.0' 'scale_tur_231_fac' 'CPI' 'Void_fraction' 'liner_fraction' 'Cont_H_tot_m' 'Cont_rad_out_m' 'Cont_shell_t_m' 'Cont_H_wall_m' 'Basemat_t_m' 'Dome_t_m' 'Intern_wall_t' 'React_cav_A_m2' 'Cont_rad_in_m' 'Basemat_s_m2' 'Basemat_v_m3' 'Walls_s_m2' 'Walls_v_m3' 'Dome_rad_in_m' 'Dome_s_m2' 'Dome_v_m3' 'Intern_tot_v_m3' 'Internal_v_m3' 'Internal_s_m2' 'Struct_v_m3' 'Inside_liner_s' 'Liner_s_m2' 'Surf_paint_m2' 'infl' 'Unit_EEDB_Labor_Cadweld_Substr' 'Unit_EEDB_Labor_Cadweld_Superstr' 'Unit_EEDB_Labor_Cadweld_Dome' 'Unit_EEDB_Labor_Cadweld_Interior' 'Unit_EEDB_Labor_Concrete_Substr' 'Unit_EEDB_Labor_Concrete_Superstr' 'Unit_EEDB_Labor_Concrete_Dome' 'Unit_EEDB_Labor_Concrete_Interior' 'Unit_EEDB_Labor_Constr_joints_Substr' 'Unit_EEDB_Labor_Constr_joints_Superstr' 'Unit_EEDB_Labor_Constr_joints_Dome' 'Unit_EEDB_Labor_Constr_joints_Interior' 'Unit_EEDB_Labor_Embedded_steel_Substr' 'Unit_EEDB_Labor_Embedded_steel_Superstr' 'Unit_EEDB_Labor_Embedded_steel_Dome' 'Unit_EEDB_Labor_Embedded_steel_Interior' 'Unit_EEDB_Labor_Formwork_Substr' 'Unit_EEDB_Labor_Formwork_Superstr' 'Unit_EEDB_Labor_Formwork_Dome' 'Unit_EEDB_Labor_Formwork_Interior' 'Unit_EEDB_Labor_Maj_supp_embedments_Interior' 'Unit_EEDB_Labor_Reinforc_steel_Substr' 'Unit_EEDB_Labor_Reinforc_steel_Superstr' 'Unit_EEDB_Labor_Reinforc_steel_Dome' 'Unit_EEDB_Labor_Reinforc_steel_Interior' 'Unit_EEDB_Labor_Rubbing_surfaces_Superstr' 'Unit_EEDB_Labor_Rubbing_surfaces_Dome' 'Unit_EEDB_Labor_Rubbing_surfaces_Interior' 'Unit_EEDB_Labor_Waterproofing_Substr' 'Unit_EEDB_Labor_Waterproofing_Superstr' 'Unit_EEDB_Labor_Waterproofing_Dome' 'Unit_EEDB_Labor_Welded_wire_fabric_Substr' 'Unit_EEDB_Labor_Lighting_Power' 'Unit_EEDB_Labor_Plumb_drains' 'Unit_EEDB_Labor_Special_HVAC' 'Unit_EEDB_Labor_other' 'Unit_EEDB_Labor_Misc_steel_frames' 'Unit_EEDB_Labor_React_cav_liner' 'Unit_EEDB_Labor_Struct_steel' 'Unit_EEDB_Labor_cont_liner' 'Unit_EEDB_Labor_fl_grate_handrail_stairs' 'Unit_EEDB_Labor_painting' 'Unit_EEDB_Mat_Cadweld_Substr' 'Unit_EEDB_Mat_Cadweld_Superstr' 'Unit_EEDB_Mat_Cadweld_Dome' 'Unit_EEDB_Mat_Cadweld_Interior' 'Unit_EEDB_Mat_Concrete_Substr' 'Unit_EEDB_Mat_Concrete_Superstr' 'Unit_EEDB_Mat_Concrete_Dome' 'Unit_EEDB_Mat_Concrete_Interior' 'Unit_EEDB_Mat_Constr_joints_Substr' 'Unit_EEDB_Mat_Constr_joints_Superstr' 'Unit_EEDB_Mat_Constr_joints_Dome' 'Unit_EEDB_Mat_Constr_joints_Interior' 'Unit_EEDB_Mat_Embedded_steel_Substr' 'Unit_EEDB_Mat_Embedded_steel_Superstr' 'Unit_EEDB_Mat_Embedded_steel_Dome' 'Unit_EEDB_Mat_Embedded_steel_Interior' 'Unit_EEDB_Mat_Formwork_Substr' 'Unit_EEDB_Mat_Formwork_Superstr' 'Unit_EEDB_Mat_Formwork_Dome' 'Unit_EEDB_Mat_Formwork_Interior' 'Unit_EEDB_Mat_Maj_supp_embedments_Interior' 'Unit_EEDB_Mat_Reinforc_steel_Substr' 'Unit_EEDB_Mat_Reinforc_steel_Superstr' 'Unit_EEDB_Mat_Reinforc_steel_Dome' 'Unit_EEDB_Mat_Reinforc_steel_Interior' 'Unit_EEDB_Mat_Rubbing_surfaces_Superstr' 'Unit_EEDB_Mat_Rubbing_surfaces_Dome' 'Unit_EEDB_Mat_Rubbing_surfaces_Interior' 'Unit_EEDB_Mat_Waterproofing_Substr' 'Unit_EEDB_Mat_Waterproofing_Superstr' 'Unit_EEDB_Mat_Waterproofing_Dome' 'Unit_EEDB_Mat_Welded_wire_fabric_Substr' 'Unit_EEDB_Mat_Lighting_Power' 'Unit_EEDB_Mat_Plumb_drains' 'Unit_EEDB_Mat_Special_HVAC' 'Unit_EEDB_Mat_other' 'Unit_EEDB_Mat_Misc_steel_frames' 'Unit_EEDB_Mat_React_cav_liner' 'Unit_EEDB_Mat_Struct_steel' 'Unit_EEDB_Mat_cont_liner' 'Unit_EEDB_Mat_fl_grate_handrail_stairs' 'Unit_EEDB_Mat_painting' 'Unit_Labor_Cadweld_Substr' 'Unit_Labor_Cadweld_Superstr' 'Unit_Labor_Cadweld_Dome' 'Unit_Labor_Cadweld_Interior' 'Unit_Labor_Concrete_Substr' 'Unit_Labor_Concrete_Superstr' 'Unit_Labor_Concrete_Dome' 'Unit_Labor_Concrete_Interior' 'Unit_Labor_Constr_joints_Substr' 'Unit_Labor_Constr_joints_Superstr' 'Unit_Labor_Constr_joints_Dome' 'Unit_Labor_Constr_joints_Interior' 'Unit_Labor_Embedded_steel_Substr' 'Unit_Labor_Embedded_steel_Superstr' 'Unit_Labor_Embedded_steel_Dome' 'Unit_Labor_Embedded_steel_Interior' 'Unit_Labor_Formwork_Substr' 'Unit_Labor_Formwork_Superstr' 'Unit_Labor_Formwork_Dome' 'Unit_Labor_Formwork_Interior' 'Unit_Labor_Maj_supp_embedments_Interior' 'Unit_Labor_Reinforc_steel_Substr' 'Unit_Labor_Reinforc_steel_Superstr' 'Unit_Labor_Reinforc_steel_Dome' 'Unit_Labor_Reinforc_steel_Interior' 'Unit_Labor_Rubbing_surfaces_Superstr' 'Unit_Labor_Rubbing_surfaces_Dome' 'Unit_Labor_Rubbing_surfaces_Interior' 'Unit_Labor_Waterproofing_Substr' 'Unit_Labor_Waterproofing_Superstr' 'Unit_Labor_Waterproofing_Dome' 'Unit_Labor_Welded_wire_fabric_Substr' 'Unit_Labor_Lighting_Power' 'Unit_Labor_Plumb_drains' 'Unit_Labor_Special_HVAC' 'Unit_Labor_other' 'Unit_Labor_Misc_steel_frames' 'Unit_Labor_React_cav_liner' 'Unit_Labor_Struct_steel' 'Unit_Labor_cont_liner' 'Unit_Labor_fl_grate_handrail_stairs' 'Unit_Labor_painting' 'Unit_Mat_Cadweld_Substr' 'Unit_Mat_Cadweld_Superstr' 'Unit_Mat_Cadweld_Dome' 'Unit_Mat_Cadweld_Interior' 'Unit_Mat_Concrete_Substr' 'Unit_Mat_Concrete_Superstr' 'Unit_Mat_Concrete_Dome' 'Unit_Mat_Concrete_Interior' 'Unit_Mat_Constr_joints_Substr' 'Unit_Mat_Constr_joints_Superstr' 'Unit_Mat_Constr_joints_Dome' 'Unit_Mat_Constr_joints_Interior' 'Unit_Mat_Embedded_steel_Substr' 'Unit_Mat_Embedded_steel_Superstr' 'Unit_Mat_Embedded_steel_Dome' 'Unit_Mat_Embedded_steel_Interior' 'Unit_Mat_Formwork_Substr' 'Unit_Mat_Formwork_Superstr' 'Unit_Mat_Formwork_Dome' 'Unit_Mat_Formwork_Interior' 'Unit_Mat_Maj_supp_embedments_Interior' 'Unit_Mat_Reinforc_steel_Substr' 'Unit_Mat_Reinforc_steel_Superstr' 'Unit_Mat_Reinforc_steel_Dome' 'Unit_Mat_Reinforc_steel_Interior' 'Unit_Mat_Rubbing_surfaces_Superstr' 'Unit_Mat_Rubbing_surfaces_Dome' 'Unit_Mat_Rubbing_surfaces_Interior' 'Unit_Mat_Waterproofing_Substr' 'Unit_Mat_Waterproofing_Superstr' 'Unit_Mat_Waterproofing_Dome' 'Unit_Mat_Welded_wire_fabric_Substr' 'Unit_Mat_Lighting_Power' 'Unit_Mat_Plumb_drains' 'Unit_Mat_Special_HVAC' 'Unit_Mat_other' 'Unit_Mat_Misc_steel_frames' 'Unit_Mat_React_cav_liner' 'Unit_Mat_Struct_steel' 'Unit_Mat_cont_liner' 'Unit_Mat_fl_grate_handrail_stairs' 'Unit_Mat_painting' 'Total_Labor_Cadweld_Substr' 'Total_Labor_Cadweld_Superstr' 'Total_Labor_Cadweld_Dome' 'Total_Labor_Cadweld_Interior' 'Total_Labor_Concrete_Substr' 'Total_Labor_Concrete_Superstr' 'Total_Labor_Concrete_Dome' 'Total_Labor_Concrete_Interior' 'Total_Labor_Constr_joints_Substr' 'Total_Labor_Constr_joints_Superstr' 'Total_Labor_Constr_joints_Dome' 'Total_Labor_Constr_joints_Interior' 'Total_Labor_Embedded_steel_Substr' 'Total_Labor_Embedded_steel_Superstr' 'Total_Labor_Embedded_steel_Dome' 'Total_Labor_Embedded_steel_Interior' 'Total_Labor_Formwork_Substr' 'Total_Labor_Formwork_Superstr' 'Total_Labor_Formwork_Dome' 'Total_Labor_Formwork_Interior' 'Total_Labor_Maj_supp_embedments_Interior' 'Total_Labor_Reinforc_steel_Substr' 'Total_Labor_Reinforc_steel_Superstr' 'Total_Labor_Reinforc_steel_Dome' 'Total_Labor_Reinforc_steel_Interior' 'Total_Labor_Rubbing_surfaces_Superstr' 'Total_Labor_Rubbing_surfaces_Dome' 'Total_Labor_Rubbing_surfaces_Interior' 'Total_Labor_Waterproofing_Substr' 'Total_Labor_Waterproofing_Superstr' 'Total_Labor_Waterproofing_Dome' 'Total_Labor_Welded_wire_fabric_Substr' 'Total_Labor_Lighting_Power' 'Total_Labor_Plumb_drains' 'Total_Labor_Special_HVAC' 'Total_Labor_other' 'Total_Labor_Misc_steel_frames' 'Total_Labor_React_cav_liner' 'Total_Labor_Struct_steel' 'Total_Labor_cont_liner' 'Total_Labor_fl_grate_handrail_stairs' 'Total_Labor_painting' 'Total_Mat_Cadweld_Substr' 'Total_Mat_Cadweld_Superstr' 'Total_Mat_Cadweld_Dome' 'Total_Mat_Cadweld_Interior' 'Total_Mat_Concrete_Substr' 'Total_Mat_Concrete_Superstr' 'Total_Mat_Concrete_Dome' 'Total_Mat_Concrete_Interior' 'Total_Mat_Constr_joints_Substr' 'Total_Mat_Constr_joints_Superstr' 'Total_Mat_Constr_joints_Dome' 'Total_Mat_Constr_joints_Interior' 'Total_Mat_Embedded_steel_Substr' 'Total_Mat_Embedded_steel_Superstr' 'Total_Mat_Embedded_steel_Dome' 'Total_Mat_Embedded_steel_Interior' 'Total_Mat_Formwork_Substr' 'Total_Mat_Formwork_Superstr' 'Total_Mat_Formwork_Dome' 'Total_Mat_Formwork_Interior' 'Total_Mat_Maj_supp_embedments_Interior' 'Total_Mat_Reinforc_steel_Substr' 'Total_Mat_Reinforc_steel_Superstr' 'Total_Mat_Reinforc_steel_Dome' 'Total_Mat_Reinforc_steel_Interior' 'Total_Mat_Rubbing_surfaces_Superstr' 'Total_Mat_Rubbing_surfaces_Dome' 'Total_Mat_Rubbing_surfaces_Interior' 'Total_Mat_Waterproofing_Substr' 'Total_Mat_Waterproofing_Superstr' 'Total_Mat_Waterproofing_Dome' 'Total_Mat_Welded_wire_fabric_Substr' 'Total_Mat_Lighting_Power' 'Total_Mat_Plumb_drains' 'Total_Mat_Special_HVAC' 'Total_Mat_other' 'Total_Mat_Misc_steel_frames' 'Total_Mat_React_cav_liner' 'Total_Mat_Struct_steel' 'Total_Mat_cont_liner' 'Total_Mat_fl_grate_handrail_stairs' 'Total_Mat_painting' 'Sum_Labor_Cadweld' 'Sum_Labor_Concrete' 'Sum_Labor_Constr_joints' 'Sum_Labor_Embedded_steel' 'Sum_Labor_Formwork' 'Sum_Labor_Maj_supp_embedments' 'Sum_Labor_Reinforc_steel' 'Sum_Labor_Rubbing_surfaces' 'Sum_Labor_Waterproofing' 'Sum_Labor_Welded_wire_fabric' 'Sum_Mat_Cadweld' 'Sum_Mat_Concrete' 'Sum_Mat_Constr_joints' 'Sum_Mat_Embedded_steel' 'Sum_Mat_Formwork' 'Sum_Mat_Maj_supp_embedments' 'Sum_Mat_Reinforc_steel' 'Sum_Mat_Rubbing_surfaces' 'Sum_Mat_Waterproofing' 'Sum_Mat_Welded_wire_fabric' 'Tot_Labor_concr' 'Tot_Labor_equipment' 'Tot_Labor_others' 'Tot_Mat_concr' 'Tot_Mat_equipment' 'Tot_Mat_others' 'Tot_Labor_containment' 'Tot_Mat_containment'  ]
        }
        value{
            MinOccurs = 1
            MaxOccurs = 1
            ValType = Real
            MinValInc = 0
            MaxValExc = NoLimit
        }
        unit{
            MinOccurs = 1
            MaxOccurs = 1
            ValType = String
            ValEnums = [squareMeter cubeMeter kW MW W lbs ton kg million 'gpm*feet' '1' m 'm^2' 'm^3' 'dollar/m^3' 'dollar/m^2']
        }
    }
    l0COA{
        Description = "level 0 code of account"
        MinOccurs = 0
        MaxOccurs = NoLimit
        InputTmpl = "L0COA"
        id{
            MinOccurs = 0
            MaxOccurs = 1
            ValType = String
            ValEnums = [ '1' '2' '3' '4' '5' 'new']
        }
        l1COA{
        	Description = "level 1 code of account"
        	MinOccurs = 0
        	MaxOccurs = NoLimit
        	InputTmpl = "L1COA" % TODO: add template
            id{
                MinOccurs = 0
                MaxOccurs = 1
                ValType = String
                ValEnums = ['21' '22' '23' '24' '25' '26' 'new' ]
            }
            total_cost{
                Description = "total cost value"
                MinOccurs = 0
                MaxOccurs = NoLimit
                InputTmpl = "total_cost" % TODO: Add template
                value{
                    MinOccurs = 1
                    MaxOccurs = 1
                    ValType = Real
                    MinValInc = 0
                    MaxValExc = NoLimit
                }
                unit{
                    MinOccurs = 1
                    MaxOccurs = 1
                    ValType = String
                    ValEnums = [ million  dollar]
                }                                
            }
            % there is no cost element in this level
            l2COA{
        		Description = "level 2 code of account"
        		MinOccurs = 0
        		MaxOccurs = NoLimit
        		InputTmpl = "L2COA" % TODO: add template
                id{
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = String
                    ValEnums = ['211' '212' '213' '214' '215' '216' '217' '218' '220A' '221' '222' '223' '224' '225' '226' '227' '228' '231' '233' '234' '235' '236' '237' '241' '242' '243' '244' '245' '246' '251' '252' '253' '254' '255' '261' '262' 'new' '23and24and25'] 
                }
                total_cost{
                    Description = "total cost value"
                    MinOccurs = 0
                    MaxOccurs = NoLimit
                    InputTmpl = "total_cost"
                    value{
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        MinValInc = 0
                        MaxValExc = NoLimit
                    }
                    unit{
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = String
                        ValEnums = [ million  dollar]
                    }                            
                }
                ce{
        			Description = "???" % needs to be added
        			MinOccurs = 0
        			MaxOccurs = NoLimit
        			InputTmpl = "ce" % TODO: add template
                    id{
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = String
                        ValEnums = ['211_fac' '212_fac' '213_fac' '214_fac' '215_fac' '216_fac' '217_fac' '218_fac' '220A_fac' '221_fac' '222_fac' '223_fac' '224_fac' '225_fac' '226_fac' '227_fac' '228_fac' '231_fac' '233_fac' '234_fac' '235_fac' '236_fac' '237_fac' '241_fac' '242_fac' '243_fac' '244_fac' '245_fac' '246_fac' '251_fac' '252_fac' '253_fac' '254_fac' '255_fac' '261_fac' '262_fac' '211_lab' '212_lab' '213_lab' '214_lab' '215_lab' '216_lab' '217_lab' '218_lab' '220A_lab' '221_lab' '222_lab' '223_lab' '224_lab' '225_lab' '226_lab' '227_lab' '228_lab' '231_lab' '233_lab' '234_lab' '235_lab' '236_lab' '237_lab' '241_lab' '242_lab' '243_lab' '244_lab' '245_lab' '246_lab' '251_lab' '252_lab' '253_lab' '254_lab' '255_lab' '261_lab' '262_lab' '211_mat' '212_mat' '213_mat' '214_mat' '215_mat' '216_mat' '217_mat' '218_mat' '220A_mat' '221_mat' '222_mat' '223_mat' '224_mat' '225_mat' '226_mat' '227_mat' '228_mat' '231_mat' '233_mat' '234_mat' '235_mat' '236_mat' '237_mat' '241_mat' '242_mat' '243_mat' '244_mat' '245_mat' '246_mat' '251_mat' '252_mat' '253_mat' '254_mat' '255_mat' '261_mat' '262_mat' '23and24and25_fac']
                    }
                    alg{
        				Description = "???" % needs to be added
        				MinOccurs = 0
        				MaxOccurs = NoLimit
        				InputTmpl = "alg" % TODO: add template
                        id{
                            MinOccurs = 0
                            MaxOccurs = 1
                            ValType = String
                            ValEnums = [esc_1987 NO_ALG MWth_scale default_0 dev_factor_ref ptn_account MWe_scale sum_multi_accounts]
                        }
                        var{
                            Description = "changed variable value"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            InputTmpl = "alg_var"  % TODO add template
                            id{
                                MinOccurs = 1
                                MaxOccurs = 1
                                ValType = String
                                ValEnums = ['ref_211_mat' 'ref_211_lab' 'ref_211_fac' 'escalate_1987' 'c_213_mat' 'c_213_lab' 'c_213_fac' 'scale_0.8' 'mwth' 'c_222_mat' 'c_222_lab' 'c_222_fac' 'scale_1.0' 'ref_224_mat' 'ref_224_lab' 'ref_224_fac' 'ref_227_mat' 'ref_227_lab' 'ref_227_fac' 'ref_228_mat' 'ref_228_lab' 'prn_fac_231_mat' 'prn_fac_231_lab' 'c_231_fac' 'scale_tur_231_fac' 'n_231' 'c_turbine' 'c_233_mat' 'c_233_lab' 'c_233_fac' 'c_234_mat' 'c_234_lab' 'c_234_fac' 'prn_235_of_231_mat' 'prn_235_of_231_lab' 'prn_235_of_231_fac' 'c_231_mat' 'c_231_lab' 'ref_236_mat' 'ref_236_lab' 'ref_236_fac' 'c_237_mat' 'c_237_lab' 'c_241_mat' 'c_241_lab' 'c_241_fac' 'scale_0.4' 'mwe' 'c_242_mat' 'c_242_lab' 'c_242_fac' 'c_245_mat' 'c_245_lab' 'c_246_mat' 'c_246_lab' 'c_246_fac' 'c_251.17_mat' 'c_251.16_mat' 'c_251.112_mat' 'c_251.111_mat' 'c_251.12_mat' 'c_251.17_lab' 'c_251.16_lab' 'c_251.112_lab' 'c_251.111_lab' 'c_251.12_lab' 'c_251.17_fac' 'c_251.16_fac' 'c_251.112_fac' 'c_251.111_fac' 'c_251.12_fac' 'ref_252_mat' 'ref_252_lab' 'ref_252_fac' 'ref_253_mat' 'ref_253_lab' 'ref_253_fac' 'c_262_mat' 'c_262_lab' 'c_262_fac']
                            }
                            value{
                                MinOccurs = 0
                                MaxOccurs = 1
                                ValType = Real
                                MinValInc = 0
                                MaxValExc = NoLimit
                            }
                            unit{
                                MinOccurs = 0
                                MaxOccurs = 1
                                ValType = String
                                ValEnums = [squareMeter cubeMeter ton lbs million "1" "gpm*feet" bar "m^3" "dollar/m^3" MW psi psf dollar thousand]
                            }
                            alg{ % is this an alg within var within alg???? it should use a different name to avoid confusion.
                                Description = "valriable algorithm"
                                MinOccurs = 0
                                MaxOccurs = 1
                                InputTmpl = "alg_var_alg" % ???
                                id{
                                    MinOccurs = 1
                                    MaxOccurs = 1
                                    ValType = String
                                    ValEnums = ['tur_exp_n' 'rpv_mass' 'pump' ]
                                }
                                var{
                                    Description = "changed variable value"
                                    MinOccurs = 1
                                    MaxOccurs = NoLimit
                                    InputTmpl = "alg_var_alg_var" % ???
                                    id{
                                        MinOccurs = 1
                                        MaxOccurs = 1
                                        ValType = String
                                        ValEnums = [ 'p_in' 'c_221.12_cs_weight' 'c_221.12_ss_weight' 'c_pump_ap1000' 'CH_12be' 'CH_AP1000' 'scale_0.52' ]
                                    }
                                    value{
                                        MinOccurs = 1
                                        MaxOccurs = 1
                                        ValType = Real
                                        MinValInc = 0
                                        MaxValExc = NoLimit
                                    }
                                    unit{
                                        MinOccurs = 1
                                        MaxOccurs = 1
                                        ValType = String
                                        ValEnums = [ bar psi psf lbs ton million  'gpm*feet' '1' ]
                                    }
                                }
                            }                           
                        }
                    }
                }
                l3COA{
                	% same as abobe - definition - min - max + template
                    id{
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = String
                        ValEnums = [ '218A' '218B' '218D' '218E' '218F' '218G' '218H' '218J' '218K' '218L' '218P' '218S' '218T' '218V' '220A.211' '220A.2121' '220A.2122' '220A.2131' '220A.2132' '220A.221' '220A.222' '220A.223' '220A.224' '220A.225' '220A.2311' '220A.2312' '220A.2321' '220A.2322' '220A.2323' '220A.2324' '220A.2325' '220A.251' '220A.254' '220A.2611' '220A.2612' '220A.2613' '220A.2614' '220A.262' '220A.27' '221.11' '221.12' '221.13' '221.14' '221.21' '221.22' '221.23' '221.24' '222.11' '222.12' '222.13' '222.14' '223.1' '223.3' '223.4' '223.5' '226.1' '226.3' '226.4' '226.6' '226.7' '226.8' '226.9' 'new' ]
                    }
                    total_cost{
                        Description = "total cost value"
                        MinOccurs = 0
                        MaxOccurs = NoLimit
                        value{
                            MinOccurs = 1
                            MaxOccurs = 1
                            ValType = Real
                            MinValInc = 0
                            MaxValExc = NoLimit
                        }
                        unit{
                            MinOccurs = 1
                            MaxOccurs = 1
                            ValType = String
                            ValEnums = [ million  dollar]
                        }                            
                    }
                    ce{
                                    	% same as abobe - definition - min - max + template
                        id{
                            MinOccurs = 0
                            MaxOccurs = 1
                            ValType = String
                            ValEnums = [ '218A_fac' '218B_fac' '218D_fac' '218E_fac' '218F_fac' '218G_fac' '218H_fac' '218J_fac' '218K_fac' '218L_fac' '218P_fac' '218S_fac' '218T_fac' '218V_fac' '220A.211_fac' '220A.2121_fac' '220A.2122_fac' '220A.2131_fac' '220A.2132_fac' '220A.221_fac' '220A.222_fac' '220A.223_fac' '220A.224_fac' '220A.225_fac' '220A.2311_fac' '220A.2312_fac' '220A.2321_fac' '220A.2322_fac' '220A.2323_fac' '220A.2324_fac' '220A.2325_fac' '220A.251_fac' '220A.254_fac' '220A.2611_fac' '220A.2612_fac' '220A.2613_fac' '220A.2614_fac' '220A.262_fac' '220A.27_fac' '221.11_fac' '221.12_fac' '221.13_fac' '221.14_fac' '221.21_fac' '221.23_mat' '222.11_fac' '222.12_fac' '222.13_fac' '222.14_fac' '223.1_fac' '223.3_fac' '223.4_fac' '223.5_fac' '226.1_fac' '226.3_fac' '226.4_fac' '226.6_fac' '226.7_fac' '226.8_fac' '226.9_fac' '218A_lab' '218B_lab' '218D_lab' '218E_lab' '218F_lab' '218G_lab' '218H_lab' '218J_lab' '218K_lab' '218L_lab' '218P_lab' '218S_lab' '218T_lab' '218V_lab' '220A.211_lab' '220A.2121_lab' '220A.2122_lab' '220A.2131_lab' '220A.2132_lab' '220A.221_lab' '220A.222_lab' '220A.223_lab' '220A.224_lab' '220A.225_lab' '220A.2311_lab' '220A.2312_lab' '220A.2321_lab' '220A.2322_lab' '220A.2323_lab' '220A.2324_lab' '220A.2325_lab' '220A.251_lab' '220A.254_lab' '220A.2611_lab' '220A.2612_lab' '220A.2613_lab' '220A.2614_lab' '220A.262_lab' '220A.27_lab' '221.11_lab' '221.12_lab' '221.13_lab' '221.14_lab' '221.21_lab' '221.24_mat' '222.11_lab' '222.12_lab' '222.13_lab' '222.14_lab' '223.1_lab' '223.3_lab' '223.4_lab' '223.5_lab' '226.1_lab' '226.3_lab' '226.4_lab' '226.6_lab' '226.7_lab' '226.8_lab' '226.9_lab' '218A_mat' '218B_mat' '218D_mat' '218E_mat' '218F_mat' '218G_mat' '218H_mat' '218J_mat' '218K_mat' '218L_mat' '218P_mat' '218S_mat' '218T_mat' '218V_mat' '220A.211_mat' '220A.2121_mat' '220A.2122_mat' '220A.2131_mat' '220A.2132_mat' '220A.221_mat' '220A.222_mat' '220A.223_mat' '220A.224_mat' '220A.225_mat' '220A.2311_mat' '220A.2312_mat' '220A.2321_mat' '220A.2322_mat' '220A.2323_mat' '220A.2324_mat' '220A.2325_mat' '220A.251_mat' '220A.254_mat' '220A.2611_mat' '220A.2612_mat' '220A.2613_mat' '220A.2614_mat' '220A.262_mat' '220A.27_mat' '221.11_mat' '221.12_mat' '221.13_mat' '221.14_mat' '221.21_mat' 221.22_mat '222.11_mat' '222.12_mat' '222.13_mat' '222.14_mat' '223.1_mat' '223.3_mat' '223.4_mat' '223.5_mat' '226.1_mat' '226.3_mat' '226.4_mat' '226.6_mat' '226.7_mat' '226.8_mat' '226.9_mat' ]
                        }
                        alg{
                            id{
                                MinOccurs = 1
                                MaxOccurs = 1
                                ValType = String
                                ValEnums = ['NO_ALG' 'complex' 'unit_weights' 'unit_facility' 'unit_weights_plate' 'unit_weights_factor' 'total_weight_prn' 'esc_1978' 'sum_multi_accounts' 'default_0' 'MWth_scale' 'esc_1987' 'factor_sum' 'unit_volume' 'cost_by_weight' ]
                            }
                            var{
                                Description = "changed variable value"
                                MinOccurs = 1
                                MaxOccurs = NoLimit
                                id{
                                    MinOccurs = 1
                                    MaxOccurs = 1
                                    ValType = String
                                    ValEnums = [  'c_218B_mat' 'c_218B_lab' 'c_218B_fac' 'c_218J_mat' 'c_218J_lab' 'c_218J_fac' 'c_218T_mat' 'c_218T_lab' 'c_218T_fac' 'c_221.12_ss_weight' 'c_221.12_cs_weight' 'c_220A.2121_ss_weight' 'c_zero' 'c_220A.2122_ss_weight' 'c_cr_per_unit_fac' 'no_of_cr' 'c_crd_per_unit_fac' 'no_of_crd' 'c_pump_per_unit_fac' 'no_of_rcpump' 'c_220A.222_ss_weight' 'c_220A.224_ss_weight' 'c_220A.224_cs_weight_plate' 'c_220A.225_ss_weight' 'c_220A.2311_fac' 'factor_220A.2312' 'c_220A.2312_ss_weight' 'c_220A.2312_cs_weight' 'c_220A.2321_fac' 'no_of_acu' 'prn_220A.2322ss' 'prn_220A.2322cs' 'c_220A.2322_tot_weight' 'no_of_bit' 'prn_220A.2323ss' 'prn_220A.2323cs' 'c_220A.2323_tot_weight' 'c_220A.2324_ss_weight' 'c_220A.2325_fac' 'factor_220A.251' 'c_220A.251_ss_weight' 'c_220A.251_cs_weight' 'ref_220A.254_1978' 'escalate_1978' 'c_226.41152_fac' 'c_226.41151_fac' 'c_226.4114_fac' 'c_226.41132_fac' 'c_226.41131_fac' 'c_226.4112_fac' 'c_226.4111_fac' 'c_226.4128_fac' 'c_226.4127_fac' 'c_226.4126_fac' 'c_226.4125_fac' 'c_226.4124_fac' 'c_226.4123_fac' 'c_226.4122_fac' 'c_226.4121_fac' 'c_226.4131_fac' 'c_226.4135_fac' 'c_226.4134_fac' 'c_226.4133_fac' 'c_226.4145_fac' 'c_226.4144_fac' 'c_226.4143_fac' 'c_226.4142_fac' 'c_226.4141_fac' 'c_rpv_mat' 'c_rpv_lab' 'c_221.12_tol_weight' 'ref_221.14_mat' 'escalate_1987' 'c_222.11_mat' 'c_222.11_lab' 'c_222.11_fac' 'scale_1.0' 'mwth' 'c_222.12_mat' 'c_222.12_lab' 'c_222.12_fac' 'c_SG_per_unit_mat' 'c_SG_per_unit_lab' 'no_of_sg' 'ref_222.13_fac' 'c_222.14_mat' 'c_222.14_lab' 'c_222.14_fac' 'c_220A.2312_fac' 'prn_223.1_mat' 'prn_223.1_lab' 'prn_223.1_fac' 'fac_223.1' 'c_220A.2324_fac' 'c_220A.2323_fac' 'c_220A.2322_fac' 'prn_223.3_mat' 'prn_223.3_lab' 'prn_223.3_fac' 'fac_223.3' 'c_223.4_unit_vol_mat' 'c_223.4_unit_vol_lab' 'c_223.4_unit_vol_fac' 'vol_223.4' 'c_226.4_mat' 'c_226.4_lab' 'c_226.4_fac' 'c_226.7_mat' 'c_226.7_lab' 'c_226.7_fac' ]
                                }
                                value{
                                    MinOccurs = 0
                                    MaxOccurs = 1
                                    ValType = Real
                                    MinValInc = 0
                                    MaxValExc = NoLimit
                                }
                                unit{
                                    MinOccurs = 0
                                    MaxOccurs = 1
                                    ValType = String
                                    ValEnums = [million ton lbs '1' 'million/ton']
                                }
                                alg{
                                    Description = "valriable algorithm"
                                    MinOccurs = 0
                                    MaxOccurs = 1
                                    id{
                                        MinOccurs = 1
                                        MaxOccurs = 1
                                        ValType = String
                                        ValEnums = ['tur_exp_n' 'rpv_mass' 'pump' ]
                                    }
                                    var{
                                        Description = "changed variable value"
                                        MinOccurs = 1
                                        MaxOccurs = NoLimit
                                        id{
                                            MinOccurs = 1
                                            MaxOccurs = 1
                                            ValType = String
                                            ValEnums = [ 'p_in' 'c_221.12_cs_weight' 'c_221.12_ss_weight' 'c_pump_ap1000' 'CH_12be' 'CH_AP1000' 'scale_0.52' ]
                                        }
                                        value{
                                            MinOccurs = 1
                                            MaxOccurs = 1
                                            ValType = Real
                                            MinValInc = 0
                                            MaxValExc = NoLimit
                                        }
                                        unit{
                                            MinOccurs = 1
                                            MaxOccurs = 1
                                            ValType = String
                                            ValEnums = [m_2 bar lbs ton million "gpm*feet" "1" psi psf]
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                newCOA{
                    Description = "new code of account"
                    MinOccurs = 0
                    MaxOccurs = NoLimit
                    InputTmpl = "newCOA" % TODO: add template
                    id{
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = String
                    }
                    descr{
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = String
                    }
                }
            }
        }

    }
}
