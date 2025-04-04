ChildExactlyOne = [ necost ]

necost {
    Description = "Input parameters for LCAE Calculations"
    MinOccurs = 0
    MaxOccurs = 1
    InputTmpl = "necost"

    construction_interest_rate {
        Description = "" % TODO
        MinOccurs = 0
        MaxOccurs = 1
        MinValInc = 0
        ValType = Real
        InputTmpl="flagtypes"
        % TODO: What are min-max values for this?
    }

    operations_interest_rate {
        Description = "" % TODO
        MinOccurs = 0
        MaxOccurs = 1
        MinValInc = 0
        ValType = Real
        InputTmpl="flagtypes"
        % TODO: What are min-max values for this?
    }

    sample_size {
        Description = "" % TODO
        MinOccurs = 0
        MaxOccurs = 1
        MinValExc = 0
        ValType = Real
        InputTmpl="flagtypes"
        % TODO: What are min-max values for this?
    }

    fuel_cycles {
        Description = "" % TODO
        MinOccurs = 0
        MaxOccurs = 1
        ChildUniqueness = ["cycle/id"]
        InputTmpl = "fuel_cycles/fuel_cycles"

        cycle {
            Description = "" % TODO
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
                Description = "" % TODO
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
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    MinValInc=0 % TODO: Should we allow 0? (if so, change to MinValInc=0)
                    %MaxValInc=1
                    %SumOver("../..") = 1
                    InputTmpl="flagtypes"
                }

                fleet_energy {
                    Description = "" % TODO
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
        Description = "" % TODO
        MinOccurs = 0
        MaxOccurs = 1
        ChildUniqueness = ["reactor/id"]
        InputTmpl="reactors/reactors"

        reactor {
            Description = "" % TODO
            MinOccurs = 0
            MaxOccurs = NoLimit
            InputTmpl="reactors/single_reactor"

            id {
                MinOccurs = 0
                MaxOccurs = 1
                ValType = String
            }

            power_level {
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                InputTmpl="reactors/power_level"
                ChildExactlyOne=[reference_net_electrical reference_thermal]

                reference_net_electrical {
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }

                reference_thermal {
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }

                net_thermal_efficiency {
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }
            }

            capacity_factor {
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            cycle_length {
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            lifetime_years {
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            capital_costs {
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ChildUniqueness = ["scaling_factor/id"]
                InputTmpl="reactors/capital_costs"

                scaling_factor {
                    Description = "" % TODO
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
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ChildUniqueness = ["scaling_factor/id"]
                InputTmpl="reactors/om_costs"

                scaling_factor {
                    Description = "" % TODO
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
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ChildUniqueness = ["quantity_of_fuel/id"]
                InputTmpl="reactors/fuel_reloads"

                quantity {
                    Description = "" % TODO
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
                        Description = "" % TODO
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    thermal_power_fraction {
                        Description = "" % TODO
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    fuel_fraction{
                        Description = "" % TODO
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
        Description = "" % TODO
        MinOccurs = 0
        MaxOccurs = 1
        ChildUniqueness = ["item/id"]
        InputTmpl="capital_costs/capital_costs"

        item {
            Description = "" % TODO
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
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            cost_type {
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ValType = String
                ValEnums = [single s_curve]
                InputTmpl="flagtypes"
            }

            expenditure_time {
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            distribution {
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                InputTmpl="cost_distribution"

                type {
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = String
                    ValEnums = [triangular uniform]
                    InputTmpl="flagtypes"
                }

                low {
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }

                high {
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }

                nominal {
                    Description = "" % TODO
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
        Description = "" % TODO
        MinOccurs = 0
        MaxOccurs = 1
        ChildUniqueness = ["item/id"]
        InputTmpl="om_costs/om_costs"

        item {
            Description = "" % TODO
            MinOccurs = 0
            MaxOccurs = NoLimit
            ChildExactlyOne=[nominal_value distribution]
            ChildAtMostOne=[expenditure_time cost_type=variable cost_type=fixed]
            InputTmpl="om_costs/cost_item"

            id {
                MinOccurs = 0
                MaxOccurs = 1
                ValType = String
            }

            cost_type {
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ValType = String
                ValEnums = [variable fixed single periodic]
                InputTmpl="flagtypes"
            }

            expenditure_time {
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            nominal_value {
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            distribution {
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                InputTmpl="cost_distribution"

                type {
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = String
                    ValEnums = [triangular uniform]
                    InputTmpl="flagtypes"
                }

                low {
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }

                high {
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }

                nominal {
                    Description = "" % TODO
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
        Description = "" % TODO
        MinOccurs = 0
        MaxOccurs = 1
        ChildUniqueness = ["item/id"]
        InputTmpl="fuels/fuel_costs"

        item {
            Description = "" % TODO
            MinOccurs = 0
            MaxOccurs = NoLimit
            InputTmpl="fuels/cost_item"

            id {
                MinOccurs = 0
                MaxOccurs = 1
                ValType = String
            }

            cost_value {
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            lead_time {
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            distribution {
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                InputTmpl="cost_distribution"

                type {
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = String
                    ValEnums = [triangular uniform]
                    InputTmpl="flagtypes"
                }

                low {
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }

                high {
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    ValType = Real
                    InputTmpl="flagtypes"
                    % TODO: What are min-max values for this?
                }

                nominal {
                    Description = "" % TODO
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
        Description = "" % TODO
        MinOccurs = 0
        MaxOccurs = 1
        ChildUniqueness = ["fuel/id"]
        InputTmpl="fuels/fuels"

        fuel {
            Description = "" % TODO
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
                Description = "" % TODO
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
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            avg_fuel_residence_time {
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                ValType = Real
                InputTmpl="flagtypes"
                % TODO: What are min-max values for this?
            }

            fresh_fuel{
                Description = "" % TODO
                MinOccurs = 1
                MaxOccurs = 1
                InputTmpl="fuels/fresh_fuel_composition"

                fabrication {
                    Description = "" % TODO
                    MinOccurs = 1
                    MaxOccurs = 1
                    InputTmpl="fuels/fabrication"

                    lead_time {
                        Description = "" % TODO
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    loss_fraction {
                        Description = "loss_fraction of the fresh fuel during fabrication" 
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    costs {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }

                DU {
                    Description = "" % TODO
                    MinOccurs = 1
                    MaxOccurs = 1
                    InputTmpl="fuels/fcc_depleted_uranium"

                    fuel_fraction {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
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
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }

                    avoided_costs {
                        Description = "" % TODO
                        MinOccurs = 0
                        MaxOccurs = 1

                        value {
                            Description = "" % TODO
                            MinOccurs = 0
                            MaxOccurs = NoLimit
                            ValType = String
                            InputTmpl="sonarray"
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }

                NU {
                    Description = "" % TODO
                    MinOccurs = 1
                    MaxOccurs = 1
                    InputTmpl="fuels/ffc_natural_uranium"

                    fuel_fraction {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
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
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }

                EU {
                    Description = "" % TODO
                    MinOccurs = 1
                    MaxOccurs = 1
                    InputTmpl="fuels/ffc_enriched_uranium"

                    fuel_fraction {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
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
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }

                Th {
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="fuels/ffc_thorium_fraction"

                    lead_time {
                        Description = "" % TODO
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    fuel_fraction {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    costs {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }

                RTh {
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="fuels/ffc_thorium_fraction"

                    lead_time {
                        Description = "" % TODO
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    loss_fraction {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    costs {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }

                RU {
                    Description = "" % TODO
                    MinOccurs = 1
                    MaxOccurs = 1
                    ChildCountEqual(EvenNone)=[product is_reenrichment=yes]
                    ChildCountEqual(EvenNone)=[tails is_reenrichment=yes]
                    ChildCountEqual(EvenNone)=[loss_fraction is_reenrichment=yes]
                    ChildCountEqual(EvenNone)=[losses is_reenrichment=yes]
                    InputTmpl="fuels/ffc_recovered_uranium_fraction"

                    fuel_fraction {
                        Description = "" % TODO
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
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"
                        
                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }

                TRU {
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="fuels/ffc_recovered_tru_fraction"

                    fuel_fraction {
                        Description = "" % TODO
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
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"
                        
                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }
                
                FP {
                    Description = "" % TODO
                    MinOccurs = 1
                    MaxOccurs = 1
                    InputTmpl="fuels/ffc_natural_uranium"

                    fuel_fraction {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
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
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }
            }

            spent_fuel{
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                InputTmpl="fuels/spent_fuel_composition"

                costs {
                    Description = "" % TODO
                    MinOccurs = 1
                    MaxOccurs = 1
                    InputTmpl="sonarray"

                    value {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = NoLimit
                        ValType = String
                        ExistsIn = [ "/necost/fuel_costs/item/id" ]
                    }
                }
                FP {
                    Description = "" % TODO
                    MinOccurs = 1
                    MaxOccurs = 1
                    InputTmpl="fuels/ffc_natural_uranium"

                    fuel_fraction {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
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
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }
            }

            EU{
                Description = "" % TODO
                MinOccurs = 1
                MaxOccurs = 1
                InputTmpl="fuels/EU"

                conversion {
                    Description = "" % TODO
                    MinOccurs = 1
                    MaxOccurs = 1
                    % TODO: Template

                    lead_time {
                        Description = "" % TODO
                        MinOccurs = 0
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        % TODO: What are min-max values for this?
                    }

                    loss_fraction {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    costs {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }
                enrichment{
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="fuels/ffc_enriched_uranium"
                    ChildCountEqual(EvenNone)=[stage_2 type=two_stage]

                    type {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = String
                        ValEnums = [one_stage two_stage]
                        InputTmpl="flagtypes"
                    }
                    
                    loss_fraction {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    stage_1{
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="fuels/ffc_enriched_uranium_two_stage_params"
                        feed {
                            Description = "" % TODO
                            MinOccurs = 0
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        }

                        product {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        }

                        tails {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        } 
                    }

                    stage_2{
                        Description = "" % TODO
                        MinOccurs = 0
                        MaxOccurs = 1
                        InputTmpl="fuels/ffc_enriched_uranium_two_stage_params"
                        feed {
                            Description = "" % TODO
                            MinOccurs = 0
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        }

                        product {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        }

                        tails {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        } 
                    }

                    SWU_costs{
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }                        
                    }

                    NU_costs{
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }

                    DU_costs{
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }
            }
            
            RU{
                Description = "" % TODO
                MinOccurs = 0
                MaxOccurs = 1
                InputTmpl="fuels/RU"

                reprocess{
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1

                    loss_fraction {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }
                    costs {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }
                conversion{
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="sonarray"

                    loss_fraction {
                        Description = "" % TODO
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
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"
                        
                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }
                    }
                }

                reenrichment{
                    Description = "" % TODO
                    MinOccurs = 0
                    MaxOccurs = 1
                    InputTmpl="sonarray"

                    loss_fraction {
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        ValType = Real
                        InputTmpl="flagtypes"
                        MinValExc = 0
                        MaxValInc = 1
                    }

                    stage_1{
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="fuels/ffc_enriched_uranium_two_stage_params"

                        feed {
                            Description = "" % TODO
                            MinOccurs = 0
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        }

                        product {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        }

                        tails {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = 1
                            ValType = Real
                            InputTmpl="flagtypes"
                            % TODO: What are min-max values for this?
                        } 
                    }

                    SWU_costs{
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "" % TODO
                            MinOccurs = 1
                            MaxOccurs = NoLimit
                            ValType = String
                            ExistsIn = [ "/necost/fuel_costs/item/id" ]
                        }                        
                    }

                    DU_costs{
                        Description = "" % TODO
                        MinOccurs = 1
                        MaxOccurs = 1
                        InputTmpl="sonarray"

                        value {
                            Description = "" % TODO
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
