ChildExactlyOne = [ necost ]

necost {
    Description = "Input parameters for LCAE Calculations"
    MinOccurs = 0
    MaxOccurs = 1
    InputTmpl = "necost"

    construction_interest_rate {
        Description = "Construction interest rate for the project" 
        MinOccurs = 0
        MaxOccurs = 1
        MinValInc = 0
        ValType = Real
        InputTmpl="flagtypes"
        % TODO: What are min-max values for this?
    }

    operations_interest_rate {
        Description = "Operations interest rate for the plant after construction"
        MinOccurs = 0
        MaxOccurs = 1
        MinValInc = 0
        ValType = Real
        InputTmpl="flagtypes"
        % TODO: What are min-max values for this?
    }

    sample_size {
        Description = "Sample size for the Monte Carlo simulation"
        MinOccurs = 0
        MaxOccurs = 1
        MinValExc = 0
        ValType = Real
        InputTmpl="flagtypes"
        % TODO: What are min-max values for this?
    }

    fuel_cycles {
        Description = "Fuel cycle parameters for the reactors"
        MinOccurs = 0
        MaxOccurs = 1
        ChildUniqueness = ["cycle/id"]
        InputTmpl = "fuel_cycles/fuel_cycles"

        cycle {
            Description = "Fuel cycle parameters for the reactors"
            MinOccurs = 0
            MaxOccurs = NoLimit
            ChildUniqueness = ["reactor/id"]
            InputTmpl = "fuel_cycles/cycle"

            id {
                MinOccurs = 0
                MaxOccurs = 1
                ValType = String
            }

            reactor {
                Description = "Reactor parameters and characteristics"
                MinOccurs = 0
                MaxOccurs = NoLimit
                InputTmpl="fuel_cycles/cycle_reactor"

                id {
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = String
                    ExistsIn = [ "/necost/reactors/reactor/id" ]
                }

                fleet_capacity {
                    Description = "Fleet capacity of the reactors unit in MWe"
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    MinValInc=0 % TODO: Should we allow 0? (if so, change to MinValInc=0)
                    %MaxValInc=1
                    %SumOver("../..") = 1
                    InputTmpl="flagtypes"
                }

                fleet_energy {
                    Description = "Fleet energy of the reactors unit in MWh"
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    MinValInc=0 % TODO: Should we allow 0? (if so, change to MinValInc=0)
                    %MaxValInc=1
                    %SumOver("../..") = 1
                    InputTmpl="flagtypes"
                }
            }
        }
    }

    reactors {
        Description = "Reactor parameters and characteristics"
        MinOccurs = 0
        MaxOccurs = 1
        ChildUniqueness = ["reactor/id"]
        InputTmpl="reactors/reactors"

        reactor {
            Description = "Reactor parameters and characteristics"
            MinOccurs = 0
            MaxOccurs = NoLimit
            InputTmpl="reactors/single_reactor"

            id {
                MinOccurs = 0
                MaxOccurs = 1
                ValType = String
            }

            power_level {
                Description = "Power level of the reactor"
                MinOccurs = 0
                MaxOccurs = 1
                InputTmpl="reactors/power_level"
                ChildExactlyOne=[reference_net_electrical reference_thermal]

                reference_net_electrical {
                    Description = "Reference net electrical power level of the reactor in W electrical" % TODO change the unit in future PR
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }

                reference_thermal {
                    Description = "Reference thermal power level of the reactor in W thermal" % TODO change the unit in future PR
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }

                net_thermal_efficiency {
                    Description = "Net thermal efficiency of the reactor unit in % (0-100)" % TODO change the unit in future PR
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }
            }

            capacity_factor {
                Description = "Capacity factor of the reactor unit in 1"
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            cycle_length {
                Description = "Cycle length of the reactor unit in years"
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            lifetime_years {
                Description = "Lifetime of the reactor unit in years"
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            capital_costs {
                Description = "Capital costs for the reactors, will select the cost item from the capital_costs section"
                MinOccurs = 0
                MaxOccurs = 1
                ChildUniqueness = ["scaling_factor/id"]
                InputTmpl="reactors/capital_costs"

                scaling_factor {
                    Description = "Simple scaling factor for the capital costs item"
                    MinOccurs = 0
                    MaxOccurs = NoLimit
                    ValType = Real
                    InputTmpl="reactors/scaling_factor"
                    % TODO: What are min-max values for this?

                    id {
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = String
                        ExistsIn = [ "/necost/capital_costs/item/id" ]
                    }
                }
            }

            om_costs {
                Description = "Operating and maintenance costs for the reactors, will select the cost item from the om_costs section"
                MinOccurs = 0
                MaxOccurs = 1
                ChildUniqueness = ["scaling_factor/id"]
                InputTmpl="reactors/om_costs"

                scaling_factor {
                    Description = "Simple scaling factor for the operating and maintenance costs item"
                    MinOccurs = 0
                    MaxOccurs = NoLimit
                    ValType = Real
                    InputTmpl="reactors/scaling_factor"
                    % TODO: What are min-max values for this?

                    id {
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = String
                        ExistsIn = [ "/necost/om_costs/item/id" ]
                    }
                }
            }

            fuel_reloads {
                Description = "Fuel reloads cost for the reactors, will select the fuel from fuels section"
                MinOccurs = 0
                MaxOccurs = 1
                ChildUniqueness = ["quantity_of_fuel/id"]
                InputTmpl="reactors/fuel_reloads"

                quantity {
                    Description = "Quantity of fuel reloads for the reactors, will select the fuel from fuels section"
                    MinOccurs = 0
                    MaxOccurs = NoLimit
                    ChildExactlyOne=[heavy_metal_mass thermal_power_fraction]
                    InputTmpl="reactors/fuel_reloads_quantity"

                    id {
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = String
                        ExistsIn = [ "/necost/fuels/fuel/id" ]
                    }

                    heavy_metal_mass {
                        Description = "Heavy metal mass of the fuel reloads for the reactor unit in MTiHM / Cycle"
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    thermal_power_fraction {
                        Description = "Fraction of Fuel Reloaded in the reactor unit in 1"
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    fuel_fraction{
                        Description = " Fuel fraction of the fuel reloads for the reactor unit in 1"
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValInc = 0
                        MaxValInc = 1
                    }
                }
            }
        }
    }

    capital_costs {
        Description = "Capital costs for the reactors"
        MinOccurs = 0
        MaxOccurs = 1
        ChildUniqueness = ["item/id"]
        InputTmpl="capital_costs/capital_costs"

        item {
            Description = "Capital costs items for the reactors"
            MinOccurs = 0
            MaxOccurs = NoLimit
            ChildExactlyOne=[nominal_value distribution]
            InputTmpl="capital_costs/cost_item"

            id {
                MinOccurs = 0
                MaxOccurs = 1
                ValType = String
            }

            cost_value {
                Description = "Overnight capital cost value for the reactor unit in $/kWe" 
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            cost_type {
                Description = "Cost type for the capital costs, can be S curve with expenditure or single point cost"
                MinOccurs = 0
                MaxOccurs = 1
                ValType = String
                ValEnums = [single s_curve]
                InputTmpl="flagtypes"
            }

            expenditure_time {
                Description = "Expenditure time for the capital costs in years"
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            distribution {
                Description = "Distribution for the capital costs"
                MinOccurs = 0
                MaxOccurs = 1
                InputTmpl="cost_distribution"

                type {
                    Description = "Choose the type of distribution for the capital costs"
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = String
                    ValEnums = [triangular uniform]
                    InputTmpl="flagtypes"
                }

                low {
                    Description = "Lower bound for the distribution"
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }

                high {
                    Description = "Upper bound for the distribution"
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }

                nominal {
                    Description = "Nominal value for the distribution"
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }
            }
        }
    }

    om_costs {
        Description = "Operating and maintenance costs for the reactors"
        MinOccurs = 0
        MaxOccurs = 1
        ChildUniqueness = ["item/id"]
        InputTmpl="om_costs/om_costs"

        item {
            Description = "Operating and maintenance costs items for the reactors"
            MinOccurs = 0
            MaxOccurs = NoLimit
            ChildAtMostOne=[expenditure_time cost_type=variable cost_type=fixed]
            InputTmpl="om_costs/cost_item"

            id {
                MinOccurs = 0
                MaxOccurs = 1
                ValType = String
            }

            cost_type {
                Description = "Cost type for the operating and maintenance costs, can be variable, fixed, single or periodic" 
                MinOccurs = 0
                MaxOccurs = 1
                ValType = String
                ValEnums = [variable fixed single periodic]
                InputTmpl="flagtypes"
            }

            expenditure_time {
                Description = "Expenditure time for the operating and maintenance costs in years"
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            nominal_value {
                Description = "Operating and maintenance cost value for the reactor unit in $/kWe"
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            distribution {
                Description = "Distribution for the operating and maintenance costs"
                MinOccurs = 0
                MaxOccurs = 1
                InputTmpl="cost_distribution"

                type {
                    Description = "Choose the type of distribution for the operating and maintenance costs"
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = String
                    ValEnums = [triangular uniform]
                    InputTmpl="flagtypes"
                }

                low {
                    Description = "Lower bound for the distribution"
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }

                high {
                    Description = "Upper bound for the distribution"
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }

                nominal {
                    Description = "Nominal value for the distribution"
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }
            }
        }
    }

    fuel_costs {
        Description = "Fuel costs"
        MinOccurs = 0
        MaxOccurs = 1
        ChildUniqueness = ["item/id"]
        InputTmpl="fuels/fuel_costs"

        item {
            Description = "Fuel costs items"
            MinOccurs = 0
            MaxOccurs = NoLimit
            InputTmpl="fuels/cost_item"

            id {
                MinOccurs = 0
                MaxOccurs = 1
                ValType = String
            }

            cost_value {
                Description = "Fuel cost value for the reactor unit in $/kg"
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            lead_time {
                Description = "Lead time for the fuel cost item in years"
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            distribution {
                Description = "Distribution for the fuel costs"
                MinOccurs = 0
                MaxOccurs = 1
                InputTmpl="cost_distribution"

                type {
                    Description = "Choose the type of distribution for the fuel costs"
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = String
                    ValEnums = [triangular uniform]
                    InputTmpl="flagtypes"
                }

                low {
                    Description = "Lower bound for the distribution"
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }

                high {
                    Description = "Upper bound for the distribution"
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }

                nominal {
                    Description = "Nominal value for the distribution"
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }
            }
        }
    }

    fuels {
        Description = "Fuel parameters and characteristics"
        MinOccurs = 0
        MaxOccurs = 1
        ChildUniqueness = ["fuel/id"]
        InputTmpl="fuels/fuels"

        fuel {
            Description = "Fuel parameters and characteristics"
            MinOccurs = 0
            MaxOccurs = NoLimit
            % ChildUniqueness = ["backend_system_parameters/fuel_id"]
            ChildExactlyOne=[avg_discharge_burnup avg_fuel_residence_time]
            InputTmpl="fuels/single_fuel"

            id {
                MinOccurs = 0
                MaxOccurs = 1
                ValType = String
            }

            avg_discharge_burnup {
                Description = "Average discharge burnup of the fuel in GWt-d/MTiHM"
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            num_batches{
                Description= "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            avg_specific_power {
                Description = "Average specific power of the fuel in Wt/g"
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            avg_fuel_residence_time {
                Description = "Average fuel residence time of the fuel in EFPY"
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            fresh_fuel{
                Description = "Fresh fuel parameters and characteristics"
                MinOccurs = 1
                MaxOccurs = 1
                InputTmpl="fuels/fresh_fuel_composition"

                fabrication {
                    Description = "fabrication parameters and characteristics"
                    MinOccurs = 1
                    MaxOccurs = 1
                    InputTmpl="fuels/fabrication"

                    lead_time {
                        Description = "Lead time for the fresh fuel fabrication in years"
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    loss_fraction {
                        Description = "Loss fraction of the fresh fuel during fabrication" 
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    costs {
                        Description = "Costs for the fresh fuel fabrication"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "Costs for the fresh fuel fabrication, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }

                DU {
                    Description = "Depleted uranium parameters and characteristics"
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="fuels/fcc_depleted_uranium"

                    fuel_fraction {
                        Description = "Fuel fraction of the depleted uranium unit in 1"
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    lead_time {
                        Description = "Lead time for the depleted uranium in years"
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    costs {
                        Description = "Costs for the depleted uranium"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "Costs for the depleted uranium, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }

                    avoided_costs {
                        Description = "Avoided costs for the depleted uranium"
                        MinOccurs = 0
                        MaxOccurs = 1

                        value {
                            Description = "Costs for the depleted uranium, choose the cost item from the fuel_costs section"
                            MinOccurs = 0
                            MaxOccurs = NoLimit
                            ValType = String
                            InputTmpl="sonarray"
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }

                NU {
                    Description = "Natural uranium parameters and characteristics"
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="fuels/ffc_natural_uranium"

                    fuel_fraction {
                        Description = "Fuel fraction of the natural uranium unit in 1"
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    lead_time {
                        Description = "Lead time for the natural uranium in years"
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    costs {
                        Description = "Costs for the natural uranium"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "Costs for the natural uranium, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }

                EU {
                    Description = "Enriched uranium parameters and characteristics"
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="fuels/ffc_enriched_uranium"

                    fuel_fraction {
                        Description = "Fuel fraction of the enriched uranium unit in 1"
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    lead_time {
                        Description = "Lead time for the enriched uranium in years"
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    costs {
                        Description = "Costs for the enriched uranium"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "Costs for the enriched uranium, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }

                Th {
                    Description = "Thorium parameters and characteristics"
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="fuels/ffc_thorium_fraction"

                    lead_time {
                        Description = "Lead time for the thorium in years"
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    fuel_fraction {
                        Description = "Fuel fraction of the thorium unit in 1"
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    costs {
                        Description = "Costs for the thorium"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "Costs for the thorium, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }

                RTh {
                    Description = "Recovered thorium parameters and characteristics"
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="fuels/ffc_thorium_fraction"

                    lead_time {
                        Description = "Lead time for the recovered thorium in years"
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    loss_fraction {
                        Description = "Loss fraction of the recovered thorium during fabrication"
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    costs {
                        Description = "Costs for the recovered thorium"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "Costs for the recovered thorium, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }

                RU {
                    Description = "Recovered uranium parameters and characteristics"
                    MinOccurs = 0
                    MaxOccurs = 1
                    ChildCountEqual(EvenNone)=[product is_reenrichment=yes]
                    ChildCountEqual(EvenNone)=[tails is_reenrichment=yes]
                    ChildCountEqual(EvenNone)=[loss_fraction is_reenrichment=yes]
                    ChildCountEqual(EvenNone)=[losses is_reenrichment=yes]
                    InputTmpl="fuels/ffc_recovered_uranium_fraction"

                    fuel_fraction {
                        Description = "Fuel fraction of the recovered uranium unit in 1"
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                    }

                    lead_time {
                        Description = "" % TODO
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    costs {
                        Description = "Costs for the recovered uranium"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"
                        
                        value {
                            Description = "Costs for the recovered uranium, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }

                TRU {
                    Description = "Transuranic parameters and characteristics"
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="fuels/ffc_recovered_tru_fraction"

                    fuel_fraction {
                        Description = "Fuel fraction of the transuranic unit in 1"
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                    }

                    lead_time {
                        Description = "Lead time for the transuranic in years"
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    costs {
                        Description = "Costs for the transuranic"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"
                        
                        value {
                            Description = "Costs for the transuranic, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }
                
                FP {
                    Description = "Fission products parameters and characteristics"
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="fuels/ffc_natural_uranium"

                    fuel_fraction {
                        Description = "Fuel fraction of the fission products unit in 1"
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    lead_time {
                        Description = "Lead time for the fission products in years"
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    costs {
                        Description = "Costs for the fission products"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "Costs for the fission products, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }
            }

            spent_fuel{
                Description = "Spent fuel parameters and characteristics"
                MinOccurs = 0
                MaxOccurs = 1
                InputTmpl="fuels/spent_fuel_composition"

                costs {
                    Description = "Costs for the spent fuel"
                    MinOccurs = 1
                    MaxOccurs = 1
                    InputTmpl="sonarray"

                    value {
                        Description = 'Costs for the spent fuel, choose the cost item from the fuel_costs section"
                        MinOccurs = 1
                        MaxOccurs = NoLimit
                        ValType = String
                        ExistsIn = [ "/necost/fuel_costs/item/id" ]
                    }
                }
                FP {
                    Description = "Fission products parameters and characteristics"
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="fuels/ffc_natural_uranium"

                    fuel_fraction {
                        Description = "Fuel fraction of the fission products unit in 1"
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    lead_time {
                        Description = "Lead time for the fission products in years"
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    costs {
                        Description = "Costs for the fission products"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "Costs for the fission products, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }
            }

            EU{
                Description = "Enriched uranium parameters and characteristics"
                MinOccurs = 0
                MaxOccurs = 1
                InputTmpl="fuels/EU"

                conversion {
                    Description = "Conversion parameters and characteristics"
                    MinOccurs = 1
                    MaxOccurs = 1
                    % TODO: Template

                    lead_time {
                        Description = "Lead time for the conversion in years"
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    loss_fraction {
                        Description = "Loss fraction of the enriched uranium during conversion"
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    costs {
                        Description = "Costs for the conversion"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "Costs for the conversion, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }
                enrichment{
                    Description = "Enrichment parameters and characteristics"
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="fuels/ffc_enriched_uranium"
                    ChildCountEqual(EvenNone)=[stage_2 type=two_stage]

                    type {
                        Description = "Enrichment type, can be one stage or two stage"
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = String
                        ValEnums = [one_stage two_stage]
                        InputTmpl="flagtypes"
                    }
                    
                    loss_fraction {
                        Description = "Loss fraction of the enriched uranium during enrichment"
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    stage_1{
                        Description = "Stage 1 parameters and characteristics"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="fuels/ffc_enriched_uranium_two_stage_params"
                        feed {
                            Description = "Feed enrichment"
                            MinOccurs = 0
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        }

                        product {
                            Description = "Product enrichment"
                            MinOccurs = 1
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        }

                        tails {
                            Description = "Tails enrichment"
                            MinOccurs = 1
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        } 
                    }

                    stage_2{
                        Description = "Stage 2 parameters and characteristics"
                        MinOccurs = 0
                        MaxOccurs = 1
                        InputTmpl="fuels/ffc_enriched_uranium_two_stage_params"
                        feed {
                            Description = "Feed enrichment"
                            MinOccurs = 0
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        }

                        product {
                            Description = "Product enrichment"
                            MinOccurs = 1
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        }

                        tails {
                            Description = "Tails enrichment"
                            MinOccurs = 1
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        } 
                    }

                    SWU_costs{
                        Description = "Enrichment costs"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "Enrichment costs, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }                        
                    }

                    NU_costs{
                        Description = "Natural uranium costs"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "Natural uranium costs, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }

                    DU_costs{
                        Description = "Depleted uranium costs"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "Depleted uranium costs, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }
            }
            
            RU{
                Description = "Recovered uranium parameters and characteristics"
                MinOccurs = 0
                MaxOccurs = 1
                InputTmpl="fuels/RU"

                reprocess{
                    Description = "Reprocessing parameters and characteristics"
                    MinOccurs = 0
                    MaxOccurs = 1

                    loss_fraction {
                        Description = "Loss fraction of the recovered uranium during reprocessing"
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }
                    costs {
                        Description = "Costs for the reprocessing"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "Costs for the reprocessing, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }
                conversion{
                    Description = "Conversion parameters and characteristics"
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="sonarray"

                    loss_fraction {
                        Description = "Loss fraction of the recovered uranium during conversion"
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                    }

                    lead_time {
                        Description = "Lead time for the conversion in years"
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    costs {
                        Description = "Costs for the conversion"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"
                        
                        value {
                            Description = "Costs for the conversion, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }

                reenrichment{
                    Description = "Reenrichment parameters and characteristics"
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="sonarray"

                    loss_fraction {
                        Description = "Loss fraction of the recovered uranium during reenrichment"
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    stage_1{
                        Description = "Stage 1 parameters and characteristics"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="fuels/ffc_enriched_uranium_two_stage_params"

                        feed {
                            Description = "Feed enrichment"
                            MinOccurs = 0
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        }

                        product {
                            Description = "Product enrichment"
                            MinOccurs = 1
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        }

                        tails {
                            Description = "Tails enrichment"
                            MinOccurs = 1
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        } 
                    }

                    SWU_costs{
                        Description = "Enrichment costs"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "Enrichment costs, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }                        
                    }

                    DU_costs{
                        Description = "Depleted uranium costs"
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "Depleted uranium costs, choose the cost item from the fuel_costs section"
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }
            }
        }
    }
}
