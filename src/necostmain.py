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

def update_transposed_dataframe(df, data_dict, key_to_var_name):
    # Update direct values from data_dict
    for key, var_name in key_to_var_name.items():
        if key in data_dict:
            value = data_dict[key]
            if var_name in df.columns:
                df.at["low", var_name] = value
                df.at["nominal", var_name] = value
                df.at["high", var_name] = value
        # Update nested dictionary structures
        elif key == "net_thermal_efficiency" and "reactors" in data_dict:
            for reactor in data_dict["reactors"]:
                power_level = reactor.get("power_level", {})
                if "net_thermal_efficiency" in power_level and var_name in df.columns:
                    value = power_level["net_thermal_efficiency"]
                    df.at["low", var_name] = value
                    df.at["nominal", var_name] = value
                    df.at["high", var_name] = value
        elif key == "ref_therm_pwr" and "reactors" in data_dict:
            for reactor in data_dict["reactors"]:
                power_level = reactor.get("power_level", {})
                if "reference_net_electrical" in power_level and var_name in df.columns:
                    value = power_level["reference_net_electrical"]
                    df.at["low", var_name] = value
                    df.at["nominal", var_name] = value
                    df.at["high", var_name] = value
        elif key == "cost_U" and "fuel_costs" in data_dict:
            for cost in data_dict["fuel_costs"]:
                if cost.get("id") == "cost_U" and var_name in df.columns:
                    df.at["low", var_name] = cost["min"]
                    df.at["nominal", var_name] = cost["nominal"]
                    df.at["high", var_name] = cost["max"]
                    df.at["distribution", var_name] = cost.get("distribution", "triangular")
    return df

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
    default_inputs= update_transposed_dataframe(default_inputs, res, key_to_var_name)
    discount_rate = res.get("operations_interest_rate", 0.05)
    monte_carlo_data = generate_monte_carlo_samples(
        params_data=default_inputs,
        sampling_amount=50000,
        discount_rate=discount_rate*100
    )
    necost_cal = NECost(data=monte_carlo_data, **default_params)
    # save the results to a file
    results = necost_cal.run()
    # print the results and save them to a file
    # the results is a dataframe, save it to a file
    results.to_csv("NECOST_results.csv")
    # Save output to file (for verification only)
    json_formatted_str = json.dumps(res, indent=4)
    with open("output.json", "w") as f:
        f.write(json_formatted_str)
    
