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
        ValEnums = [ REF:user_defined_names  REF:ref_models]
        }            

    use_gncoa{
        Description = "[optional] use generic code of account"
        MinOccurs = 0
        MaxOccurs = 1
        InputType=String
        InputTmpl="flagtypes"
        ValEnums=[true false]
        InputDefault=false
    }
    
    power{
        Description = "[required] User input power"
        MinOccurs = 0
        MaxOccurs = NoLimit
        InputTmpl = "power"
        id{
            MinOccurs = 1
            MaxOccurs = 1
            ValType = String
            ValEnums = [ REF:user_defined_names REF:power_type]
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
            ValEnums = [ REF:user_defined_names REF:power_unit]
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
            ValEnums =[ REF:user_defined_names REF:pwr_var_names REF:abr_var_names REF:containment_var_names REF:heatpipe_var_names REF:fusion_var_names]
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
            ValEnums = [ REF:user_defined_names  REF:unit_names]
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
            ValEnums = [ REF:user_defined_names   REF:l0COA_names]
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
                ValEnums = [ REF:user_defined_names  REF:l1COA_names ]
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
                    ValEnums = [ REF:user_defined_names   million  dollar]
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
                    ValEnums = [ REF:user_defined_names  REF:l2COA_names] 
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
                        ValEnums = [ REF:user_defined_names REF:total_cost_unit ]
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
                        ValEnums = [ REF:user_defined_names  REF:L2cost_element_names]
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
                            ValEnums = [ REF:user_defined_names  REF:alg_names REF:fusion_alg_names]
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
                                ValEnums =[ REF:user_defined_names REF:pwr_var_names REF:abr_var_names REF:containment_var_names 
                                REF:heatpipe_var_names
                                REF:fusion_var_names]
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
                                ValEnums = [ REF:user_defined_names  REF:unit_names]
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
                                    ValEnums = [ REF:user_defined_names  REF:alg_names REF:fusion_alg_names ]
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
                                        ValEnums =[ REF:user_defined_names REF:pwr_var_names REF:abr_var_names REF:containment_var_names REF:heatpipe_var_names REF:fusion_var_names]
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
                                        ValEnums = [ REF:user_defined_names   REF:unit_names ]
                                    }
                                }
                            }                           
                        }
                    }
                }
                alg{
                    id{
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = String
                        ValEnums = [ REF:user_defined_names  REF:alg_names REF:fusion_alg_names ]
                    }
                    var{
                        Description = "changed variable value"
                        MinOccurs = 1
                        MaxOccurs = NoLimit
                        id{
                            MinOccurs = 1
                            MaxOccurs = 1
                            ValType = String
                            ValEnums =[ REF:user_defined_names REF:pwr_var_names REF:abr_var_names REF:containment_var_names REF:heatpipe_var_names REF:fusion_var_names]
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
                            ValEnums = [ REF:user_defined_names  REF:unit_names]
                        }
                        alg{
                            Description = "valriable algorithm"
                            MinOccurs = 0
                            MaxOccurs = 1
                            id{
                                MinOccurs = 1
                                MaxOccurs = 1
                                ValType = String
                                ValEnums = [ REF:user_defined_names  REF:alg_names REF:fusion_alg_names ]
                            }
                            var{
                                Description = "changed variable value"
                                MinOccurs = 1
                                MaxOccurs = NoLimit
                                id{
                                    MinOccurs = 1
                                    MaxOccurs = 1
                                    ValType = String
                                    ValEnums =[ REF:user_defined_names REF:pwr_var_names REF:abr_var_names REF:containment_var_names REF:heatpipe_var_names REF:fusion_var_names]
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
                                    ValEnums = [ REF:user_defined_names  REF:unit_names]
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
                        ValEnums = [ REF:user_defined_names   REF:l3COA_names ]
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
                            ValEnums = [ REF:user_defined_names   million  dollar]
                        }                            
                    }
                    alg{
                        id{
                            MinOccurs = 1
                            MaxOccurs = 1
                            ValType = String
                            ValEnums = [ REF:user_defined_names  REF:alg_names REF:fusion_alg_names ]
                        }
                        var{
                            Description = "changed variable value"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            id{
                                MinOccurs = 1
                                MaxOccurs = 1
                                ValType = String
                                ValEnums =[ REF:user_defined_names REF:pwr_var_names REF:abr_var_names REF:containment_var_names REF:heatpipe_var_names REF:fusion_var_names]
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
                                ValEnums = [ REF:user_defined_names  REF:unit_names]
                            }
                            alg{
                                Description = "valriable algorithm"
                                MinOccurs = 0
                                MaxOccurs = 1
                                id{
                                    MinOccurs = 1
                                    MaxOccurs = 1
                                    ValType = String
                                    ValEnums = [ REF:user_defined_names  REF:alg_names REF:fusion_alg_names ]
                                }
                                var{
                                    Description = "changed variable value"
                                    MinOccurs = 1
                                    MaxOccurs = NoLimit
                                    id{
                                        MinOccurs = 1
                                        MaxOccurs = 1
                                        ValType = String
                                        ValEnums =[ REF:user_defined_names REF:pwr_var_names REF:abr_var_names REF:containment_var_names REF:heatpipe_var_names REF:fusion_var_names]
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
                                        ValEnums = [ REF:user_defined_names  REF:unit_names]
                                    }
                                }
                            }
                        }
                    }
                    ce{
                        % same as abobe - definition - min - max + template
                        id{
                            MinOccurs = 0
                            MaxOccurs = 1
                            ValType = String
                            ValEnums = [ REF:user_defined_names  REF:L3cost_element_names ]
                        }
                        alg{
                            id{
                                MinOccurs = 1
                                MaxOccurs = 1
                                ValType = String
                                ValEnums = [ REF:user_defined_names  REF:alg_names REF:fusion_alg_names ]
                            }
                            var{
                                Description = "changed variable value"
                                MinOccurs = 1
                                MaxOccurs = NoLimit
                                id{
                                    MinOccurs = 1
                                    MaxOccurs = 1
                                    ValType = String
                                    ValEnums =[ REF:user_defined_names REF:pwr_var_names REF:abr_var_names REF:containment_var_names REF:heatpipe_var_names REF:fusion_var_names]
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
                                    ValEnums = [ REF:user_defined_names  REF:unit_names]
                                }
                                alg{
                                    Description = "valriable algorithm"
                                    MinOccurs = 0
                                    MaxOccurs = 1
                                    id{
                                        MinOccurs = 1
                                        MaxOccurs = 1
                                        ValType = String
                                        ValEnums = [ REF:user_defined_names  REF:alg_names REF:fusion_alg_names ]
                                    }
                                    var{
                                        Description = "changed variable value"
                                        MinOccurs = 1
                                        MaxOccurs = NoLimit
                                        id{
                                            MinOccurs = 1
                                            MaxOccurs = 1
                                            ValType = String
                                            ValEnums =[ REF:user_defined_names REF:pwr_var_names REF:abr_var_names REF:containment_var_names REF:heatpipe_var_names REF:fusion_var_names]
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
                                            ValEnums = [ REF:user_defined_names  REF:unit_names]
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

EndOfSchema{}
ref_models = [ "PWR12-BE" "ABR1000" "LFR", "heatpipe","fusion"]
power_type = ["Thermal" "Electric"] 
power_unit = ["W" "kWW" "MW"]
total_cost_unit = ["million" "dollar"]
l0COA_names = ['1' '2' '3' '4' '5' '6' '7' '8' '9' 'new']
l0GNCOA_names=['10' '20' '30' '40' '50' '60' '70' '80' '90' 'new']
l1COA_names = ['11' '12' '13' '14' '15' '16' '17' '18' '19' 
               '21' '22' '23' '24' '25' '26' '27' '28' '29'
               '31' '32' '33' '34' '35' '36' '37' '38' '39'
               '41' '42' '43' '44' '45' '46' '47' '48' '49'
               '51' '52' '53' '54' '55' '56' '57' '58' '59'
               '61' '62' '63' '64' '65' '66' '67' '68' '69'
               '71' '72' '73' '74' '75' '76' '77' '78' '79'
               '81' '82' '83' '84' '85' '86' '87' '88' '89'
               '91' '92' '93' '94' '95' '96' '97' '98' '99' 'new']

l2COA_names = ['211' '212' '213' '214' '215' '216' '217' '218' '219' '220A' '221' '222' 
'223' '224' '225' '226' '227' '228' '229' '231' '233' '234' '235' '236' '237' '238' '239' 
'241' '242' '243' '244' '245' '246' '247' '248' '249' '251' '252' '253' '254' '255' '256' 
'257' '258' '259' '261' '262' '263' '264' '265' '266' '267' '268' '269' '271' '272' '273' 
'274' '275' '276' '277' '278' '279' '281' '282' '283' '284' '285' '286' '287' '288' '289' 
'291' '292' '293' '294' '295' '296' '297' '298' '299' 'new' ]

l2GNCOA_names = ['121'  '122'  '123'  '131'  '132'  '133'  '211'  '212'  '213'  '214'  
'215'  '216'  '217'  '221'  '222'  '223'  '224'  '225'  '226'  '227'  '228'  '231'  '232'  
'233'  '234'  '235'  '236'  '237'  '241'  '242'  '243'  '244'  '245'  '246'  '251'  '252'  
'253'  '254'  '255'  '261'  '262'  '263'  '264'  '265'  '311'  '312'  '313'  '314'  
'315'  '316'  '317'  '318'  '319'  '331'  '332'  '341'  '342'  '343'  '344'  '345'  '351'  
'352'  '353'  '361'  '362'  '363'  '711'  '712'  '713'  '714'  '715'  '716'  '717'  '718'  
'741'  '742'  '743'  '744'  '745'  '811'  '812'  '813'  '814'  '815'  '816'  '817'  '818'  
'821'  '822'  '823'  '824'  '825'  '826'  '831'  '832'  '833' 'new']


l3COA_names = ['218A' '218B' '218D' '218E' '218F' '218G' '218H' '218J' '218K' '218L' '218P' 
'218S' '218T' '218V' '220A.211' '220A.2121' '220A.2122' '220A.2131' '220A.2132' '220A.221' 
'220A.222' '220A.223' '220A.224' '220A.225' '220A.2311' '220A.2312' '220A.2321' '220A.2322' 
'220A.2323' '220A.2324' '220A.2325' '220A.251' '220A.254' '220A.2611' '220A.2612' 
'220A.2613' '220A.2614' '220A.262' '220A.27' '221.11' '221.12' '221.13' '221.14' '221.21' 
'221.22' '221.23' '221.24' '222.11' '222.12' '222.13' '222.14' '223.1' '223.3' '223.4' 
'223.5' '226.1' '226.3' '226.4' '226.6' '226.7' '226.8' '226.9' 'new']

fusion_L3COA_names = ['2141' '2142' '2171' '2172' '2173' '2174' '2211' '2212' '2213' '2214' 
'2215' '2221' '2222' '2223' '2231' '2232' '2233' '2241' '2242' '2243' '2244' '2245' '2246' 
'2251' '2252' '2253' '2261' '2262' '2263' '2271' '2272' '2273' '2274' 'new']

l3GNCOA_names = ['213.1' '213.2' '213.3' '213.4' '214.1' '214.2' '214.3' '214.4' '214.5' '214.6' '214.7' '215.1' '215.2' '215.3' '215.4' '215.5' '216.1' '216.2' '216.3' '216.4' '217.1' '217.2' '217.3' '217.4' '221.1' '221.2' '221.3' '222.1' '222.2' '222.3' '222.4' '222.5' '223.1' '223.2' '223.3' '223.4' '223.5' '225.1' '225.2' '231.1' '231.2' '232.1' '232.2' '232.3' '232.4' '232.5' '232.6' '232.7' '232.8' '232.9' '233.1' '233.2' '331.1' '331.2' '331.3' '331.4' '331.5' '832.1']

l4GNCOA_names = ['221.11' '221.12' '221.13' '221.21' '221.31' '221.32' '221.33']

fusion_l4COA_names = ['22121' '22122' '22123' '22124' '22131' '22132' '22211' '22212' 
'22213' '22214' '22215' '22221' '22222' '22223' '22224' '22511' '22512' '22513' '22514' 
'22515' '22521' '22522' '22523' '22524' '22525' '22526' '22527' '22611' '22612' 'new']

unit_names = [squareMeter cubeMeter kW MW W lbs ton kg million 'gpm*feet' '1' m 'm^2' 'm^3' 
'dollar/m^3' 'dollar/m^2' 'psi' 'psf' 'bar' 'dollar' 'thousand']

alg_names = ['sum_multi_accounts' 'sum_multi_weights' 'sum_multi_pumps' 'ptn_account' 
'unit_weights' 'pump' 'containment' 'MWth_scale' 'unit_volume' 'dev_factor_ref' 'tur_exp_n' 
'esc_1987' 'cost_by_weight' 'default_0' 'rpv_mass' 'unit_facility' 'MWe_scale' 
'unit_weights_plate' 'esc_1978' 'total_weight_prn' 'unit_weights_factor' 'factor_sum' 
'complex' 'MWth_lmfbrscale' 'MWreth_scale' 'Sgsum' 'containmentsum' 'inside_rad' 
'round_surface' 'basemat_volume' 'wall_height' 'walls_surface' 'wall_volume' 
'dome_inside_diameter' 'roof_surface' 'roof_volume' 'tot_internal_volume' 
'building_internal_volume' 'building_internal _surface' 'volume_of_the_structures' 
'Inside_liner_surface' 'liner_Surface' 'painted_surface' 'Inflation_rate' 
'unitcost_v_eedb_to_accert' 'unitcost_s_eedb_to_accert' 'tol_contaiment_ce_cost' 'sum_ce' 
'Yardwork_cost' 'Reactor_containment_mat_cost' 'Reactor_containment_lab_cost' 
'Building_and_utilities_mat_cost' 'Building_and_utilities_lab_cost' 
'Reactor_startup_facility_cost' 'Outer_vessel_mat_cost' 'Outer_vessel_lab_cost' 
'Inner_vessel_cost' 'Reactivity_control_system_cost' 'Reflector_cost' 'Shield_cost' 
'Moderator_cost' 'cooling_heat_pipes_cost' 'heat_exchangers_mat_cost' 
'heat_exchangers_lab_cost' 'heat_exchangers_fac_cost' 'instrumentation_contorl_cost' 
'turb_and_elec_sys_cost']

fusion_alg_names = ['acc2' 'acc21' 'acc211' 'acc212' 'acc213' 'acc214' 'acc2141' 'acc2142' 
'acc215' 'acc216' 'acc217' 'acc2171' 'acc2172' 'acc2173' 'acc2174' 'acc22' 'acc221' 
'acc2211' 'acc2212' 'acc22121' 'acc22122' 'acc22123' 'acc22124' 'acc2213' 'acc22131' 
'acc22132' 'acc2214' 'acc2215' 'acc222' 'acc2221' 'acc22211' 'acc22212' 'acc22213' 
'acc22214' 'acc22215' 'acc2222' 'acc22221' 'acc22222' 'acc22223' 'acc22224' 'acc2223' 
'acc223' 'acc2231' 'acc2232' 'acc2233' 'acc224' 'acc2241' 'acc2242' 'acc2243' 'acc2244' 
'acc2245' 'acc2246' 'acc225' 'acc2251' 'acc22511' 'acc22512' 'acc22513' 'acc22514' 
'acc22515' 'acc2252' 'acc22521' 'acc22522' 'acc22523' 'acc22524' 'acc22525' 'acc22526' 
'acc22527' 'acc2253' 'acc226' 'acc2261' 'acc22611' 'acc22612' 'acc2262' 'acc2263' 'acc227' 
'acc2271' 'acc2272' 'acc2273' 'acc2274' 'acc228' 'acc229' 'acc23' 'acc24' 'acc241' 'acc242' 
'acc243' 'acc244' 'acc245' 'acc25' 'acc26' ]

L2cost_element_names = ['211_fac' '211_lab' '211_mat' '212_fac' '212_lab' '212_mat' 
'213_fac' '213_lab' '213_mat' '214_fac' '214_lab' '214_mat' '215_fac' '215_lab' '215_mat' 
'216_fac' '216_lab' '216_mat' '217_fac' '217_lab' '217_mat' '218_fac' '218_lab' '218_mat' 
'219_fac' '219_lab' '219_mat' '220A_fac' '220A_lab' '220A_mat' '221_fac' '221_lab' '221_mat' 
'222_fac' '222_lab' '222_mat' '223_fac' '223_lab' '223_mat' '224_fac' '224_lab' '224_mat' 
'225_fac' '225_lab' '225_mat' '226_fac' '226_lab' '226_mat' '227_fac' '227_lab' '227_mat' 
'228_fac' '228_lab' '228_mat' '229_fac' '229_lab' '229_mat' '231_fac' '231_lab' '231_mat' 
'233_fac' '233_lab' '233_mat' '234_fac' '234_lab' '234_mat' '235_fac' '235_lab' '235_mat' 
'236_fac' '236_lab' '236_mat' '237_fac' '237_lab' '237_mat' '238_fac' '238_lab' '238_mat' 
'239_fac' '239_lab' '239_mat' '241_fac' '241_lab' '241_mat' '242_fac' '242_lab' '242_mat' 
'243_fac' '243_lab' '243_mat' '244_fac' '244_lab' '244_mat' '245_fac' '245_lab' '245_mat' 
'246_fac' '246_lab' '246_mat' '247_fac' '247_lab' '247_mat' '248_fac' '248_lab' '248_mat' 
'249_fac' '249_lab' '249_mat' '251_fac' '251_lab' '251_mat' '252_fac' '252_lab' '252_mat' 
'253_fac' '253_lab' '253_mat' '254_fac' '254_lab' '254_mat' '255_fac' '255_lab' '255_mat' 
'256_fac' '256_lab' '256_mat' '257_fac' '257_lab' '257_mat' '258_fac' '258_lab' '258_mat' 
'259_fac' '259_lab' '259_mat' '261_fac' '261_lab' '261_mat' '262_fac' '262_lab' '262_mat' 
'263_fac' '263_lab' '263_mat' '264_fac' '264_lab' '264_mat' '265_fac' '265_lab' '265_mat' 
'266_fac' '266_lab']

L3cost_element_names = ['218A_fac' '218B_fac' '218D_fac' '218E_fac' '218F_fac' '218G_fac' '218H_fac' '218J_fac' '218K_fac' '218L_fac' '218P_fac' '218S_fac' '218T_fac' '218V_fac' '220A.211_fac' '220A.2121_fac' '220A.2122_fac' '220A.2131_fac' '220A.2132_fac' '220A.221_fac' '220A.222_fac' '220A.223_fac' '220A.224_fac' '220A.225_fac' '220A.2311_fac' '220A.2312_fac' '220A.2321_fac' '220A.2322_fac' '220A.2323_fac' '220A.2324_fac' '220A.2325_fac' '220A.251_fac' '220A.254_fac' '220A.2611_fac' '220A.2612_fac' '220A.2613_fac' '220A.2614_fac' '220A.262_fac' '220A.27_fac' '221.11_fac' '221.12_fac' '221.13_fac' '221.14_fac' '221.21_fac' '222.11_fac' '222.12_fac' '222.13_fac' '222.14_fac' '223.1_fac' '223.3_fac' '223.4_fac' '223.5_fac' '226.1_fac' '226.3_fac' '226.4_fac' '226.6_fac' '226.7_fac' '226.8_fac' '226.9_fac' '218A_lab' '218B_lab' '218D_lab' '218E_lab' '218F_lab' '218G_lab' '218H_lab' '218J_lab' '218K_lab' '218L_lab' '218P_lab' '218S_lab' '218T_lab' '218V_lab' '220A.211_lab' '220A.2121_lab' '220A.2122_lab' '220A.2131_lab' '220A.2132_lab' '220A.221_lab' '220A.222_lab' '220A.223_lab' '220A.224_lab' '220A.225_lab' '220A.2311_lab' '220A.2312_lab' '220A.2321_lab' '220A.2322_lab' '220A.2323_lab' '220A.2324_lab' '220A.2325_lab' '220A.251_lab' '220A.254_lab' '220A.2611_lab' '220A.2612_lab' '220A.2613_lab' '220A.2614_lab' '220A.262_lab' '220A.27_lab' '221.11_lab' '221.12_lab' '221.13_lab' '221.14_lab' '221.21_lab' '222.11_lab' '222.12_lab' '222.13_lab' '222.14_lab' '223.1_lab' '223.3_lab' '223.4_lab' '223.5_lab' '226.1_lab' '226.3_lab' '226.4_lab' '226.6_lab' '226.7_lab' '226.8_lab' '226.9_lab' '218A_mat' '218B_mat' '218D_mat' '218E_mat' '218F_mat' '218G_mat' '218H_mat' '218J_mat' '218K_mat' '218L_mat' '218P_mat' '218S_mat' '218T_mat' '218V_mat' '220A.211_mat' '220A.2121_mat' '220A.2122_mat' '220A.2131_mat' '220A.2132_mat' '220A.221_mat' '220A.222_mat' '220A.223_mat' '220A.224_mat' '220A.225_mat' '220A.2311_mat' '220A.2312_mat' '220A.2321_mat' '220A.2322_mat' '220A.2323_mat' '220A.2324_mat' '220A.2325_mat' '220A.251_mat' '220A.254_mat' '220A.2611_mat' '220A.2612_mat' '220A.2613_mat' '220A.2614_mat' '220A.262_mat' '220A.27_mat' '221.11_mat' '221.12_mat' '221.13_mat' '221.14_mat' '221.21_mat' '222.11_mat' '222.12_mat' '222.13_mat' '222.14_mat' '223.1_mat' '223.3_mat' '223.4_mat' '223.5_mat' '226.1_mat' '226.3_mat' '226.4_mat' '226.6_mat' '226.7_mat' '226.8_mat' '226.9_mat']

pwr_var_names = ['c_turbine' 'n_231' 'p_in' 'scale_tur_231_fac' 'c_231_fac' 'prn_fac_231_lab' 
'prn_fac_231_mat' 'c_262_fac' 'c_262_lab' 'c_262_mat' 'mwth' 'scale_0.8' 'c_233_fac' 
'c_233_lab' 'c_233_mat' 'escalate_1987' 'ref_252_fac' 'ref_252_lab' 'ref_252_mat' 
'c_221.12_cs_weight' 'c_221.12_ss_weight' 'c_221.12_tol_weight' 'c_rpv_lab' 'c_rpv_mat' 
'ref_211_fac' 'ref_211_lab' 'ref_211_mat' 'ref_222.13_fac' 'no_of_sg' 'c_SG_per_unit_lab' 
'c_SG_per_unit_mat' 'c_234_fac' 'c_234_lab' 'c_234_mat' 'c_213_fac' 'c_213_lab' 'c_213_mat' 
'c_231_lab' 'c_231_mat' 'prn_235_of_231_fac' 'prn_235_of_231_lab' 'prn_235_of_231_mat' 'mwe' 
'scale_0.4' 'c_241_fac' 'c_241_lab' 'c_241_mat' 'c_242_fac' 'c_242_lab' 'c_242_mat' 
'c_245_fac' 'c_245_lab' 'c_245_mat' 'c_246_fac' 'c_246_lab' 'c_246_mat' 'ref_227_fac' 
'ref_227_lab' 'ref_227_mat' 'ref_224_fac' 'ref_224_lab' 'ref_224_mat' 'scale_1.0' 'c_226.7_fac' 
'c_226.7_lab' 'c_226.7_mat' 'no_of_rcpump' 'c_pump_per_unit_fac' 'c_pump_ap1000' 
'CH_12be' 'CH_AP1000' 'scale_0.52' 'c_226.4_fac' 'c_226.4_lab' 'c_226.4_mat' 'c_222.11_fac' 
'c_222.11_lab' 'c_222.11_mat' 'c_222.12_fac' 'c_222.12_lab' 'c_222.12_mat' 'c_222.13_fac' 
'c_222.13_lab' 'c_222.13_mat' 'c_222.14_fac' 'c_222.14_lab' 'c_222.14_mat' 'c_222_fac' 
'c_222_lab' 'c_222_mat' 'c_zero' 'c_220A.222_ss_weight' 'c_220A.2121_ss_weight' 'c_220A.2122_ss_weight' 'no_of_cr' 
'no_of_crd' 'c_cr_per_unit_fac' 'c_crd_per_unit_fac' 'c_220A.224_cs_weight_plate' 'c_220A.224_ss_weight' 'c_237_lab' 
'c_237_mat' 'ref_228_lab' 
'ref_228_mat' 'ref_236_fac' 'ref_236_lab' 'ref_236_mat' 'ref_253_fac' 'ref_253_lab' 
'ref_253_mat' 'ref_221.14_mat' 'ref_220A.254_fac' 'c_220A.225_ss_weight' 'c_220A.2324_ss_weight' 
'c_220A.2322_tot_weight' 'prn_220A.2322cs' 'prn_220A.2322ss' 'no_of_acu' 
'c_220A.2323_tot_weight' 'prn_220A.2323cs' 'prn_220A.2323ss' 'no_of_bit' 'c_220A.251_cs_weight' 
'c_220A.251_ss_weight' 'factor_220A.251' 'c_220A.2312_cs_weight' 'c_220A.2312_ss_weight' 
'factor_220A.2312' 'vol_223.4' 'c_223.4_unit_vol_fac' 'c_223.4_unit_vol_lab' 
'c_223.4_unit_vol_mat' 'escalate_1978' 'ref_220A.254_1978' 'c_226.4111_fac' 'c_226.4112_fac' 
'c_226.41131_fac' 'c_226.41132_fac' 'c_226.4114_fac' 'c_226.41151_fac' 'c_226.41152_fac' 
'c_226.4121_fac' 'c_226.4122_fac' 'c_226.4123_fac' 'c_226.4124_fac' 'c_226.4125_fac' 'c_226.4126_fac' 'c_226.4127_fac' 
'c_226.4128_fac' 'c_226.4133_fac' 'c_226.4134_fac' 'c_226.4135_fac' 
'c_226.4131_fac' 'c_226.4141_fac' 'c_226.4142_fac' 'c_226.4143_fac' 'c_226.4144_fac' 'c_226.4145_fac' 'c_251.12_fac' 
'c_251.111_fac' 'c_251.112_fac' 'c_251.16_fac' 'c_251.17_fac' 'c_251.12_lab' 'c_251.111_lab' 'c_251.112_lab' 'c_251.16_lab' 
'c_251.17_lab' 'c_251.12_mat' 'c_251.111_mat' 'c_251.112_mat' 'c_251.16_mat' 'c_251.17_mat' 'fac_223.1' 
'prn_223.1_fac' 'prn_223.1_lab' 
'prn_223.1_mat' 'c_220A.2311_fac' 'c_220A.2312_fac' 'fac_223.3' 'prn_223.3_fac' 
'prn_223.3_lab' 'prn_223.3_mat' 'c_220A.2321_fac' 'c_220A.2322_fac' 'c_220A.2323_fac' 'c_220A.2324_fac' 'c_220A.2325_fac' 
'c_218B_fac' 'c_218J_fac' 'c_218T_fac' 'c_220A.2311_fac' 'c_220A.2321_fac' 'c_220A.2325_fac' 'c_218B_lab' 'c_218J_lab' 
'c_218T_lab' 'c_218B_mat' 'c_218J_mat' 
'c_218T_mat' ]

abr_var_names = [ 'CH_abr1000' 'CH_AP1000' 
 'escalate_1987'  'mwreth' 'no_of_cr' 'no_of_crd' 'no_of_rcpump' 
 'prn_235_of_231_fac' 'prn_235_of_231_lab' 'prn_235_of_231_mat' 'prn_fac_231_lab' 
 'prn_fac_231_mat' 'r_222.13_lab' 'r_222.13_mat' 'r_78_220A224_fac' 'r_78_226.4_fac' 
 'liner_fraction'  ]

containment_var_names = ['CPI' 'Void_fraction' 'liner_fraction' 'Cont_H_tot_m' 'Cont_rad_out_m' 
 'Cont_shell_t_m' 'Cont_H_wall_m' 'Basemat_t_m' 'Dome_t_m' 'Intern_wall_t' 'React_cav_A_m2' 
 'Cont_rad_in_m' 'Basemat_s_m2' 'Basemat_v_m3' 'Walls_s_m2' 'Walls_v_m3' 'Dome_rad_in_m' 
 'Dome_s_m2' 'Dome_v_m3' 'Intern_tot_v_m3' 'Internal_v_m3' 'Internal_s_m2' 'Struct_v_m3' 
 'Inside_liner_s' 'Liner_s_m2' 'Surf_paint_m2' 'infl' 'Unit_EEDB_Labor_Cadweld_Substr' 
 'Unit_EEDB_Labor_Cadweld_Superstr' 'Unit_EEDB_Labor_Cadweld_Dome' 
 'Unit_EEDB_Labor_Cadweld_Interior' 'Unit_EEDB_Labor_Concrete_Substr' 
 'Unit_EEDB_Labor_Concrete_Superstr' 'Unit_EEDB_Labor_Concrete_Dome' 
 'Unit_EEDB_Labor_Concrete_Interior' 'Unit_EEDB_Labor_Constr_joints_Substr' 
 'Unit_EEDB_Labor_Constr_joints_Superstr' 'Unit_EEDB_Labor_Constr_joints_Dome' 
 'Unit_EEDB_Labor_Constr_joints_Interior' 'Unit_EEDB_Labor_Embedded_steel_Substr' 
 'Unit_EEDB_Labor_Embedded_steel_Superstr' 'Unit_EEDB_Labor_Embedded_steel_Dome' 
 'Unit_EEDB_Labor_Embedded_steel_Interior' 'Unit_EEDB_Labor_Formwork_Substr' 
 'Unit_EEDB_Labor_Formwork_Superstr' 'Unit_EEDB_Labor_Formwork_Dome' 
 'Unit_EEDB_Labor_Formwork_Interior' 'Unit_EEDB_Labor_Maj_supp_embedments_Interior' 
 'Unit_EEDB_Labor_Reinforc_steel_Substr' 'Unit_EEDB_Labor_Reinforc_steel_Superstr' 
 'Unit_EEDB_Labor_Reinforc_steel_Dome' 'Unit_EEDB_Labor_Reinforc_steel_Interior' 
 'Unit_EEDB_Labor_Rubbing_surfaces_Superstr' 'Unit_EEDB_Labor_Rubbing_surfaces_Dome' 
 'Unit_EEDB_Labor_Rubbing_surfaces_Interior' 'Unit_EEDB_Labor_Waterproofing_Substr' 
 'Unit_EEDB_Labor_Waterproofing_Superstr' 'Unit_EEDB_Labor_Waterproofing_Dome' 
 'Unit_EEDB_Labor_Welded_wire_fabric_Substr' 'Unit_EEDB_Labor_Lighting_Power' 
 'Unit_EEDB_Labor_Plumb_drains' 'Unit_EEDB_Labor_Special_HVAC' 'Unit_EEDB_Labor_other' 
 'Unit_EEDB_Labor_Misc_steel_frames' 'Unit_EEDB_Labor_React_cav_liner' 
 'Unit_EEDB_Labor_Struct_steel' 'Unit_EEDB_Labor_cont_liner' 
 'Unit_EEDB_Labor_fl_grate_handrail_stairs' 'Unit_EEDB_Labor_painting' 
 'Unit_EEDB_Mat_Cadweld_Substr' 'Unit_EEDB_Mat_Cadweld_Superstr' 
 'Unit_EEDB_Mat_Cadweld_Dome' 'Unit_EEDB_Mat_Cadweld_Interior' 
 'Unit_EEDB_Mat_Concrete_Substr' 'Unit_EEDB_Mat_Concrete_Superstr' 
 'Unit_EEDB_Mat_Concrete_Dome' 'Unit_EEDB_Mat_Concrete_Interior' 
 'Unit_EEDB_Mat_Constr_joints_Substr' 'Unit_EEDB_Mat_Constr_joints_Superstr' 
 'Unit_EEDB_Mat_Constr_joints_Dome' 'Unit_EEDB_Mat_Constr_joints_Interior' 
 'Unit_EEDB_Mat_Embedded_steel_Substr' 'Unit_EEDB_Mat_Embedded_steel_Superstr' 
 'Unit_EEDB_Mat_Embedded_steel_Dome' 'Unit_EEDB_Mat_Embedded_steel_Interior' 
 'Unit_EEDB_Mat_Formwork_Substr' 'Unit_EEDB_Mat_Formwork_Superstr' 
 'Unit_EEDB_Mat_Formwork_Dome' 'Unit_EEDB_Mat_Formwork_Interior' 
 'Unit_EEDB_Mat_Maj_supp_embedments_Interior' 'Unit_EEDB_Mat_Reinforc_steel_Substr' 
 'Unit_EEDB_Mat_Reinforc_steel_Superstr' 'Unit_EEDB_Mat_Reinforc_steel_Dome' 
 'Unit_EEDB_Mat_Reinforc_steel_Interior' 'Unit_EEDB_Mat_Rubbing_surfaces_Superstr' 
 'Unit_EEDB_Mat_Rubbing_surfaces_Dome' 'Unit_EEDB_Mat_Rubbing_surfaces_Interior' 
 'Unit_EEDB_Mat_Waterproofing_Substr' 'Unit_EEDB_Mat_Waterproofing_Superstr' 
 'Unit_EEDB_Mat_Waterproofing_Dome' 'Unit_EEDB_Mat_Welded_wire_fabric_Substr' 
 'Unit_EEDB_Mat_Lighting_Power' 'Unit_EEDB_Mat_Plumb_drains' 'Unit_EEDB_Mat_Special_HVAC' 
 'Unit_EEDB_Mat_other' 'Unit_EEDB_Mat_Misc_steel_frames' 'Unit_EEDB_Mat_React_cav_liner' 
 'Unit_EEDB_Mat_Struct_steel' 'Unit_EEDB_Mat_cont_liner' 
 'Unit_EEDB_Mat_fl_grate_handrail_stairs' 'Unit_EEDB_Mat_painting' 
 'Unit_Labor_Cadweld_Substr' 'Unit_Labor_Cadweld_Superstr' 'Unit_Labor_Cadweld_Dome' 
 'Unit_Labor_Cadweld_Interior' 'Unit_Labor_Concrete_Substr' 'Unit_Labor_Concrete_Superstr' 
 'Unit_Labor_Concrete_Dome' 'Unit_Labor_Concrete_Interior' 'Unit_Labor_Constr_joints_Substr' 
 'Unit_Labor_Constr_joints_Superstr' 'Unit_Labor_Constr_joints_Dome' 
 'Unit_Labor_Constr_joints_Interior' 'Unit_Labor_Embedded_steel_Substr' 
 'Unit_Labor_Embedded_steel_Superstr' 'Unit_Labor_Embedded_steel_Dome' 
 'Unit_Labor_Embedded_steel_Interior' 'Unit_Labor_Formwork_Substr' 
 'Unit_Labor_Formwork_Superstr' 'Unit_Labor_Formwork_Dome' 'Unit_Labor_Formwork_Interior' 
 'Unit_Labor_Maj_supp_embedments_Interior' 'Unit_Labor_Reinforc_steel_Substr' 
 'Unit_Labor_Reinforc_steel_Superstr' 'Unit_Labor_Reinforc_steel_Dome' 
 'Unit_Labor_Reinforc_steel_Interior' 'Unit_Labor_Rubbing_surfaces_Superstr' 
 'Unit_Labor_Rubbing_surfaces_Dome' 'Unit_Labor_Rubbing_surfaces_Interior' 
 'Unit_Labor_Waterproofing_Substr' 'Unit_Labor_Waterproofing_Superstr' 
 'Unit_Labor_Waterproofing_Dome' 'Unit_Labor_Welded_wire_fabric_Substr' 
 'Unit_Labor_Lighting_Power' 'Unit_Labor_Plumb_drains' 'Unit_Labor_Special_HVAC' 
 'Unit_Labor_other' 'Unit_Labor_Misc_steel_frames' 'Unit_Labor_React_cav_liner' 
 'Unit_Labor_Struct_steel' 'Unit_Labor_cont_liner' 'Unit_Labor_fl_grate_handrail_stairs' 
 'Unit_Labor_painting' 'Unit_Mat_Cadweld_Substr' 'Unit_Mat_Cadweld_Superstr' 
 'Unit_Mat_Cadweld_Dome' 'Unit_Mat_Cadweld_Interior' 'Unit_Mat_Concrete_Substr' 
 'Unit_Mat_Concrete_Superstr' 'Unit_Mat_Concrete_Dome' 'Unit_Mat_Concrete_Interior' 
 'Unit_Mat_Constr_joints_Substr' 'Unit_Mat_Constr_joints_Superstr' 
 'Unit_Mat_Constr_joints_Dome' 'Unit_Mat_Constr_joints_Interior' 
 'Unit_Mat_Embedded_steel_Substr' 'Unit_Mat_Embedded_steel_Superstr' 
 'Unit_Mat_Embedded_steel_Dome' 'Unit_Mat_Embedded_steel_Interior' 
 'Unit_Mat_Formwork_Substr' 'Unit_Mat_Formwork_Superstr' 'Unit_Mat_Formwork_Dome' 
 'Unit_Mat_Formwork_Interior' 'Unit_Mat_Maj_supp_embedments_Interior' 
 'Unit_Mat_Reinforc_steel_Substr' 'Unit_Mat_Reinforc_steel_Superstr' 
 'Unit_Mat_Reinforc_steel_Dome' 'Unit_Mat_Reinforc_steel_Interior' 
 'Unit_Mat_Rubbing_surfaces_Superstr' 'Unit_Mat_Rubbing_surfaces_Dome' 
 'Unit_Mat_Rubbing_surfaces_Interior' 'Unit_Mat_Waterproofing_Substr' 
 'Unit_Mat_Waterproofing_Superstr' 'Unit_Mat_Waterproofing_Dome' 
 'Unit_Mat_Welded_wire_fabric_Substr' 'Unit_Mat_Lighting_Power' 'Unit_Mat_Plumb_drains' 
 'Unit_Mat_Special_HVAC' 'Unit_Mat_other' 'Unit_Mat_Misc_steel_frames' 
 'Unit_Mat_React_cav_liner' 'Unit_Mat_Struct_steel' 'Unit_Mat_cont_liner' 
 'Unit_Mat_fl_grate_handrail_stairs' 'Unit_Mat_painting' 'Total_Labor_Cadweld_Substr' 
 'Total_Labor_Cadweld_Superstr' 'Total_Labor_Cadweld_Dome' 'Total_Labor_Cadweld_Interior' 
 'Total_Labor_Concrete_Substr' 'Total_Labor_Concrete_Superstr' 'Total_Labor_Concrete_Dome' 
 'Total_Labor_Concrete_Interior' 'Total_Labor_Constr_joints_Substr' 
 'Total_Labor_Constr_joints_Superstr' 'Total_Labor_Constr_joints_Dome' 
 'Total_Labor_Constr_joints_Interior' 'Total_Labor_Embedded_steel_Substr' 
 'Total_Labor_Embedded_steel_Superstr' 'Total_Labor_Embedded_steel_Dome' 
 'Total_Labor_Embedded_steel_Interior' 'Total_Labor_Formwork_Substr' 
 'Total_Labor_Formwork_Superstr' 'Total_Labor_Formwork_Dome' 'Total_Labor_Formwork_Interior' 
 'Total_Labor_Maj_supp_embedments_Interior' 'Total_Labor_Reinforc_steel_Substr' 
 'Total_Labor_Reinforc_steel_Superstr' 'Total_Labor_Reinforc_steel_Dome' 
 'Total_Labor_Reinforc_steel_Interior' 'Total_Labor_Rubbing_surfaces_Superstr' 
 'Total_Labor_Rubbing_surfaces_Dome' 'Total_Labor_Rubbing_surfaces_Interior' 
 'Total_Labor_Waterproofing_Substr' 'Total_Labor_Waterproofing_Superstr' 
 'Total_Labor_Waterproofing_Dome' 'Total_Labor_Welded_wire_fabric_Substr' 
 'Total_Labor_Lighting_Power' 'Total_Labor_Plumb_drains' 'Total_Labor_Special_HVAC' 
 'Total_Labor_other' 'Total_Labor_Misc_steel_frames' 'Total_Labor_React_cav_liner' 
 'Total_Labor_Struct_steel' 'Total_Labor_cont_liner' 'Total_Labor_fl_grate_handrail_stairs' 
 'Total_Labor_painting' 'Total_Mat_Cadweld_Substr' 'Total_Mat_Cadweld_Superstr' 
 'Total_Mat_Cadweld_Dome' 'Total_Mat_Cadweld_Interior' 'Total_Mat_Concrete_Substr' 
 'Total_Mat_Concrete_Superstr' 'Total_Mat_Concrete_Dome' 'Total_Mat_Concrete_Interior' 
 'Total_Mat_Constr_joints_Substr' 'Total_Mat_Constr_joints_Superstr' 
 'Total_Mat_Constr_joints_Dome' 'Total_Mat_Constr_joints_Interior' 
 'Total_Mat_Embedded_steel_Substr' 'Total_Mat_Embedded_steel_Superstr' 
 'Total_Mat_Embedded_steel_Dome' 'Total_Mat_Embedded_steel_Interior' 
 'Total_Mat_Formwork_Substr' 'Total_Mat_Formwork_Superstr' 'Total_Mat_Formwork_Dome' 
 'Total_Mat_Formwork_Interior' 'Total_Mat_Maj_supp_embedments_Interior' 
 'Total_Mat_Reinforc_steel_Substr' 'Total_Mat_Reinforc_steel_Superstr' 
 'Total_Mat_Reinforc_steel_Dome' 'Total_Mat_Reinforc_steel_Interior' 
 'Total_Mat_Rubbing_surfaces_Superstr' 'Total_Mat_Rubbing_surfaces_Dome' 
 'Total_Mat_Rubbing_surfaces_Interior' 'Total_Mat_Waterproofing_Substr' 
 'Total_Mat_Waterproofing_Superstr' 'Total_Mat_Waterproofing_Dome' 
 'Total_Mat_Welded_wire_fabric_Substr' 'Total_Mat_Lighting_Power' 'Total_Mat_Plumb_drains' 
 'Total_Mat_Special_HVAC' 'Total_Mat_other' 'Total_Mat_Misc_steel_frames' 
 'Total_Mat_React_cav_liner' 'Total_Mat_Struct_steel' 'Total_Mat_cont_liner' 
 'Total_Mat_fl_grate_handrail_stairs' 'Total_Mat_painting' 'Sum_Labor_Cadweld' 
 'Sum_Labor_Concrete' 'Sum_Labor_Constr_joints' 'Sum_Labor_Embedded_steel' 
 'Sum_Labor_Formwork' 'Sum_Labor_Maj_supp_embedments' 'Sum_Labor_Reinforc_steel' 
 'Sum_Labor_Rubbing_surfaces' 'Sum_Labor_Waterproofing' 'Sum_Labor_Welded_wire_fabric' 
 'Sum_Mat_Cadweld' 'Sum_Mat_Concrete' 'Sum_Mat_Constr_joints' 'Sum_Mat_Embedded_steel' 
 'Sum_Mat_Formwork' 'Sum_Mat_Maj_supp_embedments' 'Sum_Mat_Reinforc_steel' 
 'Sum_Mat_Rubbing_surfaces' 'Sum_Mat_Waterproofing' 'Sum_Mat_Welded_wire_fabric' 
 'Tot_Labor_concr' 'Tot_Labor_equipment' 'Tot_Labor_others' 'Tot_Mat_concr' 
 'Tot_Mat_equipment' 'Tot_Mat_others' 'Tot_Labor_containment' 'Tot_Mat_containment' ]

heatpipe_var_names = ['land_surface_area' 'containment_subVolume' 'Containment_hole_volume' 'Turbine_building_surface_area' 'Distance_to_utilities' 'Number_of_shipping_containers' 'Battery_capacity_required' 'primary_outer_vessel_SS_mass' 'primary_inner_vessel_SS_mass' 'B4C_total_neutron_poison_mass_Kg' 'Number_of_control_rod_drums' 'number_of_emergency_control_rods' 'stainless_steel_316_reflector_mass' 'Al2O3_reflector_mass' 'BeO_reflector_mass' 'shield_B4C_mass' 'moderator_ZrH_mass' 'mass_production_cost_reduction_factor' 'number_of_core_cooling_heat_pipes' 'number_of_heat_exchangers' 'heat_exchangers_mass' 'number_of_IO_sensors' 'mwth' 'mwe']

fusion_var_names = ['a' 'acptmax' 'admvol' 'afuel' 'ai' 'aintmass' 'akappa' 'areaoh' 'awpoh' 'b0' 'blmass' 'cconfix' 'cconshpf' 'cconshtf' 'cdirt' 'cdriv0' 'cdriv1' 'cdriv2' 'cdriv3' 'cfind_0' 'cfind_1' 'cfind_2' 'cfind_3' 'cland' 'clgsmass' 'coilmass' 'convol' 'coolmass' 'coolwh' 'cowner' 'cpstcst' 'cpttf' 'crypmw' 'cryvol' 'csi' 'cturbb' 'd_0' 'd_1' 'd_2' 'd_3' 'dcdrv0' 'dcdrv1' 'dcdrv2' 'dcond_0' 'dcond_1' 'dcond_2' 'dcond_3' 'dcond_4' 'dcond_5' 'dcond_6' 'dcond_7' 'dcond_8' 'dcopper' 'dens' 'divcst' 'divsur' 'dlscal' 'drbi' 'dtstor' 'dvrtmass' 'ealphadt' 'echarge' 'echpwr' 'edrive' 'effrfss' 'elevol' 'ensxpfm' 'esbldgm3' 'estotftgj' 'etadrv' 'expel' 'expepe' 'exphts' 'exprb' 'exprf' 'exptpe' 'faccd' 'faccdfix' 'fachtmw' 'fburn' 'fcap0' 'fcdfuel' 'fcontng' 'fcsht' 'fcuohsu' 'fcupfsu' 'fkind' 'fncmass' 'fndt' 'ftrit' 'fusionrate' 'fwallcst' 'fwarea' 'fwmass' 'fwmatm' 'gain' 'gsmass' 'hccl' 'hcwt' 'helpow' 'hrbi' 'i_tf_sc_mat' 'i_tf_sup' 'iblanket' 'iefrf' 'ife' 'ifedrv' 'ifueltyp' 'imax' 'iohcl' 'ipfres' 'ireactor' 'istore' 'isumatoh' 'isumatpf' 'itart' 'l1' 'lpulse' 'lsa' 'ltot' 'mbvfac' 'mcdriv' 'n_tf' 'n_tf_turn' 'nohc' 'nphx' 'ntype' 'nvduct' 'oh_steel_frac' 'pacpmw' 'palpnb' 'peakmva' 'pfbldgm3' 'pfckts' 'pfmass' 'pfwdiv' 'pfwndl' 'pgrossmw' 'pheat' 'pibv' 'pinjht' 'pinjwp' 'plascur' 'plhybd' 'pnbitot' 'pnetelmw' 'pnucblkt' 'pnucshld' 'powfmw' 'pthermmw' 'r0' 'rbrt' 'rbvfac' 'rbvol' 'rbwt' 'reprat' 'ric_0' 'ric_1' 'ric_2' 'ric_3' 'ric_4' 'ric_5' 'ric_6' 'rjconpf_0' 'rjconpf_1' 'rjconpf_2' 'rjconpf_3' 'rjconpf_4' 'rjconpf_5' 'rjconpf_6' 'rjconpf_7' 'rjconpf_8' 'rjconpf_9' 'rjconpf_10' 'rjconpf_11' 'rjconpf_12' 'rjconpf_13' 'rjconpf_14' 'rjconpf_15' 'rjconpf_16' 'rjconpf_17' 'rjconpf_18' 'rjconpf_19' 'rjconpf_20' 'rjconpf_21' 'rpf_0' 'rpf_1' 'rpf_2' 'rpf_3' 'rpf_4' 'rpf_5' 'rpf_6' 'shmatm' 'spfbusl' 'srcktpm' 'stcl' 'tdown' 'tdspmw' 'tf_h_width ' 'tfacmw' 'tfbusl' 'tfbusmas' 'tfcbv' 'tfckw' 'tfcmw' 'tfhmax' 'tfleng' 'tfmass' 'tlvpmw' 'tmpcry' 'trcl' 'trithtmw' 'triv' 'turns_0' 'turns_1' 'turns_2' 'turns_3' 'turns_4' 'turns_5' 'turns_6' 'twopi' 'ucad' 'ucaf' 'ucahts' 'ucap' 'ucblbe' 'ucblbreed' 'ucblli' 'ucblli2o' 'ucbllipb' 'ucblss' 'ucblvd' 'ucbpmp' 'ucbus' 'uccarb' 'uccase' 'ucco' 'ucconc' 'uccpcl1' 'uccpclb' 'uccpmp' 'uccr' 'uccry' 'uccryo' 'uccu' 'ucdgen' 'ucdiv' 'ucdtc' 'ucduct' 'ucech' 'ucel' 'ucf1' 'ucfnc' 'ucfpr' 'ucfwa' 'ucfwps' 'ucfws' 'ucgss' 'uchrs' 'uchts_0' 'uchts_1' 'uciac' 'ucich' 'ucint' 'uclh' 'uclv' 'ucmb' 'ucme' 'ucmisc' 'ucnbi' 'ucnbv' 'ucpens' 'ucpfb' 'ucpfbk' 'ucpfbs' 'ucpfcb' 'ucpfdr1' 'ucpfic' 'ucpfps' 'ucphx' 'ucpp' 'ucrb' 'ucsc_0' 'ucsc_1' 'ucsc_2' 'ucsc_3' 'ucsc_4' 'ucsc_5' 'ucsc_6' 'ucsc_7' 'ucsc_8' 'ucsh' 'ucshld' 'ucswyd' 'uctfbr' 'uctfbus' 'uctfdr' 'uctfgr' 'uctfic' 'uctfps' 'uctfsw' 'uctpmp' 'uctr' 'ucturb_0' 'ucturb_1' 'ucvalv' 'ucvdsh' 'ucviac' 'ucwindpf' 'ucwindtf' 'umass' 'vacdshm' 'vachtmw' 'vcdimax' 'vf' 'vfohc' 'vol' 'volrci' 'vpfskv' 'vpumpn' 'vtfskv' 'vvmass' 'wgt2' 'whtblbe' 'whtblbreed' 'whtblli' 'whtblss' 'whtblvd' 'whtcas' 'whtconcu' 'whtconsc' 'whtcp' 'whtpfs' 'whtshld' 'whttflgs' 'wpenshld' 'wrbi' 'wsvfac' 'wsvol' 'wtblli2o' 'wtbllipb' 'rmbvol' 'ucws' 'shovol' 'expcry']

user_defined_names = [ ]