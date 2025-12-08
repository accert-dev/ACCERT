import os
import sys
import json
import pandas as pd

from input_processor import parse_son_input
from necost import NECost, generate_monte_carlo_samples

key_to_var_name = {
    "construction_interest_rate": "interest_rate_constrct",
    "net_thermal_efficiency": "therm_efficiency",
    "reference_net_electrical": "ref_therm_pwr",
    "cost_U": "cost_U",
}

default_params = {
    "is_new_plant": True,
    "is_new_fuel": False,
    "add_turb": False,
    "om_frac": 1.0,
    "t_plant": 60,
    "fuel_diam_ref": 0.8194,
    "assembly_ref": 193,
    "ref_burnup": 50.00,
    "fuel_density_ref": 10.4215,
    "weight_hm_ref": 88.15 / 100,
    "l_h_ref": 358,
    "batches_ref": 3,
    "pv_sg_ref": 100e6,
    "m_sg": 0.6,
    "pv_head_ref": 25e6,
    "pv_internals_ref": 25e6,
    "pv_turb_ref": 338e6,
    "m_turb": 0.8
}

# Adjust the function to update named rows
def update_default_inputs_reactor(default_inputs, res, mapping):
    for reactor in res.get("reactors", []):
        for key, column in mapping.items():
            # Split the key to traverse the nested structure dynamically
            parts = key.split('.')
            value = reactor
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part, None)
                elif isinstance(value, list):
                    value = next((item for item in value if item.get("id") == part), None)
                if value is None:
                    break
            # Handle distribution logic for capital_costs and other nested lists
            # value is a list of dictionaries
            if isinstance(value, list):
                for val_dict in value:
                    if 'heavy_metal_mass' in val_dict:
                        fuel_id = val_dict["id"]
                        HM_mass = val_dict['heavy_metal_mass']
                        default_inputs.loc["low",'HM_mass_direct_spec'] = HM_mass
                        default_inputs.loc["nominal",'HM_mass_direct_spec'] = HM_mass
                        default_inputs.loc["high",'HM_mass_direct_spec'] = HM_mass
                        default_inputs.loc["distribution",'HM_mass_direct_spec'] = 0
                    else:    
                        scaling_factor_id = val_dict["id"]  # Extract the id
                        # Find the corresponding entry in res["capital_costs"] or res["om_costs"]
                        target_costs = res.get("capital_costs", []) + res.get("om_costs", []) + res.get("fuel_costs", [])
                        matched_entry = next((item for item in target_costs if item.get("id") == scaling_factor_id), None)
                        if isinstance(column, dict):
                            for key, sub_column in column.items():
                                if matched_entry and key == matched_entry["id"]:
                                    dist = matched_entry["distribution"]
                                    if dist == "triangular":
                                        default_inputs.loc["low",sub_column] = float(matched_entry.get("min", 0))
                                        default_inputs.loc["nominal",sub_column] = float(matched_entry.get("nominal", 0))
                                        default_inputs.loc["high",sub_column] = float(matched_entry.get("max", 0))
                                        default_inputs.loc["distribution",sub_column] = 1

                        elif matched_entry and "distribution" in matched_entry:
                            dist = matched_entry["distribution"]
                            if dist == "triangular":
                                default_inputs.loc["low",column] = float(matched_entry.get("min", 0))  # Low
                                default_inputs.loc["nominal",column] = float(matched_entry.get("nominal", 0))  # Nominal
                                default_inputs.loc["high",column] = float(matched_entry.get("max", 0))  # High
                                default_inputs.loc["distribution",column] = 1  # Triangular Distribution
            elif value is not None:  # Handle standard fields without distribution
                default_inputs.loc["low",column] = value  # Low
                default_inputs.loc["nominal",column] = value  # Nominal
                default_inputs.loc["high",column] = value  # High
                default_inputs.loc["distribution",column] = 0  # No Distribution

    for fuel_cost in res.get("fuel_costs", []):
        fuel_cost_id = fuel_cost["id"]
        dist = fuel_cost["distribution"]
        if dist == "triangular":
            default_inputs.loc["low", fuel_cost_id] = float(fuel_cost.get("min", 0))
            default_inputs.loc["nominal", fuel_cost_id] = float(fuel_cost.get("nominal", 0))
            default_inputs.loc["high", fuel_cost_id] = float(fuel_cost.get("max", 0))
            default_inputs.loc["distribution", fuel_cost_id] = 1
        lead_time_id = mapping["fuel_costs_lead_time"].get(fuel_cost_id)
        if lead_time_id:
            lead_time = float(fuel_cost.get("lead_time", 0))
            default_inputs.loc["low", lead_time_id] = lead_time
            default_inputs.loc["nominal", lead_time_id] = lead_time
            default_inputs.loc["high", lead_time_id] = lead_time
            default_inputs.loc["distribution", lead_time_id] = 0

    for fuel in res.get("fuels", []):

        for key, column in mapping["fuel_input"].items():
            value = fuel.get(key, None)
            default_inputs.loc["low", column] = value
            default_inputs.loc["nominal", column] = value
            default_inputs.loc["high", column] = value
            default_inputs.loc["distribution", column] = 0
        # others
        for key, column in mapping.items():
            # Split the key to traverse the nested structure dynamically
            parts = key.split('.')
            value = fuel
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part, None)
                elif isinstance(value, list):
                    value = next((item for item in value if item.get("id") == part), None)
                if value is None:
                    break
            if value is not None:
                default_inputs.loc["low",column] = value  # Low
                default_inputs.loc["nominal",column] = value
                default_inputs.loc["high",column] = value
                default_inputs.loc["distribution",column] = 0



    return default_inputs

mapping_with_distribution = {
    "power_level.reference_thermal": "ref_therm_pwr",
    "capacity_factor": "L_direct_spec",
    "power_level.net_thermal_efficiency": "therm_efficiency",
    "capital_costs": "capital_cost",
    "om_costs": {"OM_per_year":"OM_direct_spec", 
                 "OM_per_MWh":"OM_fixed_cost"},
    "fuel_type": "HM_mass_direct_spec",
    "fuel_costs_lead_time": {"cost_U":"op",
                             "cost_SWU":"lead_time_nrchmt",
                             "cost_fuel_fab": "lead_time_fab",
                             "cost_conv": "lead_time_conv",
                             "cost_geologic_disposal":"lead_time_FP_disposal",
                             },
    "fuel_input": {"avg_discharge_burnup":"max_burnup",
                   "num_batches":"num_batches",
                   },
    "fresh_fuel.fabrication.loss":"fab_loss_percent",
    "fresh_fuel.EU.fuel_fraction":"frac_core_loaded_nat",
    "EU.conversion.loss_fraction":"conv_loss_percent",
    "EU.enrichment.stage_1.feed":"feed_nrchmt_fresh",
    "EU.enrichment.stage_1.product":"nrchmt_fresh",
    "EU.enrichment.stage_1.tails":"tails_nrchmt_fresh",
    }






# Apply the enhanced update function



if __name__ == "__main__":
    code_folder = os.path.dirname(os.path.abspath(__file__))
    necost_path = os.path.abspath(os.path.join(code_folder, os.pardir))
    user_input = sys.argv[2]

    if os.path.exists(user_input):
        input_path = os.path.abspath(user_input)
    else:
        print('NE-COST did not find the input file {}'.format(user_input))
        raise SystemExit

    # Parse the input (str->dict)
    res = parse_son_input(input_path, necost_path)
    # read the default input file
    default_inputs = pd.read_csv(f"{code_folder}/necost/default_input.csv").set_index("var_name").transpose()
    # default_inputs= update_transposed_dataframe(default_inputs, res, key_to_var_name)
    default_inputs = update_default_inputs_reactor(default_inputs, res, mapping_with_distribution)
    # save new default inputs to a file
    default_inputs.to_csv("default_inputs_new.csv")
    discount_rate = res.get("operations_interest_rate", 0.05)
    sample_size = res.get("sample_size", 40000)
    print(f"Discount rate: {discount_rate}")
    print(f"Sample size: {sample_size}")
    monte_carlo_data = generate_monte_carlo_samples(
        params_data=default_inputs,
        sampling_amount=sample_size,
        discount_rate=discount_rate*100
    )
    necost_cal = NECost(data=monte_carlo_data, **default_params)
    # save the results to a file
    results = necost_cal.run()
    # plot the results the results is a dataframe, plot it
    # remove HM_mass_direct_spec	t_cyc	L_direct_spec in results
    results = results.drop(columns=['HM_mass_direct_spec','t_cyc','L_direct_spec'])
    import matplotlib.pyplot as plt
    # plot is like a KDE plot fill in the gaps
    bin_num = int(sample_size/10)
    
    results.plot(kind='hist', bins=bin_num, alpha=0.5)
    plt.title("NECOST Results")
    plt.xlabel("levelized cost ($/MWh)")
    plt.show()
    # save the plot to a file
    plt.savefig("NECOST_results.png")

    # print the results and save them to a file
    # the results is a dataframe, save it to a file
    results.to_csv("NECOST_results.csv")
    # Save output to file (for verification only)
    json_formatted_str = json.dumps(res, indent=4)
    with open("output.json", "w") as f:
        f.write(json_formatted_str)
    
