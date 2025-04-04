import subprocess
from collections import defaultdict
from typing import Callable, Dict, List, Union
from xml.etree import ElementTree


def son_input_to_str(input_path: str, necost_path: str):
    """
    Converts a SON XML input file to a string representation using the 'sonvalidxml' subprocess.

    This function takes an input_path to the SON XML file and the necost_path to the NECOST installation
    directory, and executes the 'sonvalidxml' subprocess to validate the input file and obtain the
    string representation of the XML.

    Parameters
    ----------
    input_path : str
        The file path of the input SON XML file to be converted.

    necost_path : str
        The path to the NECOST installation directory containing 'sonvalidxml' and the schema file.

    Returns
    -------
    bytes
        The string representation of the SON XML file as returned by the 'sonvalidxml' subprocess.

    Raises
    ------
    Exception
        If the 'sonvalidxml' subprocess fails to execute or returns an error code.
    """
    son_valid_xml = necost_path + "/bin/sonvalidxml"
    schema = necost_path + "/src/etc/necost.sch"
    cmd = ' '.join([son_valid_xml, schema, input_path])

    try:
        xml_result = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        err_msgs = [
            f"Running subprocess 'sonvalidxml' exited with code {e.returncode}",
            f"Failed Trying to execute command: `{cmd}`",
        ]
        raise Exception("\n--- ".join(err_msgs)) from None

    return xml_result


def xml_tree_to_dict(root):
    """
    Converts an XML Element tree into a nested Python dictionary representation.

    This function recursively traverses the XML Element tree and converts it into a nested dictionary
    representation, preserving the hierarchical structure of the XML. Each element tag becomes a key in
    the dictionary, and its value can be another dictionary (for nested elements) or a string (for leaf elements).

    SOURCE: https://stackoverflow.com/a/10076823/7407086

    Parameters
    ----------
    root : Element
        The root element of the XML Element tree to be converted.

    Returns
    -------
    dict
        The nested dictionary representation of the XML Element tree.
    """
    parsed = {root.tag: {} if root.attrib else None}
    children = list(root)

    # Parse children of the current node
    if children:
        children_nodes = defaultdict(list)
        for child_node in map(xml_tree_to_dict, children):
            for k, v in child_node.items():
                children_nodes[k].append(v)
        parsed = {root.tag: {k: v[0] if len(v) == 1 else v for k, v in children_nodes.items()}}

    # Add attributes to the current node
    if root.attrib:
        parsed[root.tag].update(('@' + k, v) for k, v in root.attrib.items())

    # Add the text node to the current node
    if root.text:
        text = root.text.strip()
        if children or root.attrib:
            if text:
                parsed[root.tag]['#text'] = text
        else:
            parsed[root.tag] = text

    return parsed


def parse_son_input(input_path: str, necost_path: str) -> Dict:
    """
    Parses the SON XML input file and extracts relevant data into a dictionary.

    This function reads the SON XML file specified by 'input_path' and processes it to extract
    specific data elements such as construction and operations interest rates, fuel cycles,
    reactors, capital costs, operation and maintenance costs, and fuels. It then organizes this
    extracted information into a structured dictionary.

    Parameters
    ----------
    input_path : str
        The file path of the input SON XML file to be parsed.
    necost_path : str
        The path to the NECOST installation directory.

    Returns
    -------
    dict
        A dictionary containing the parsed information from the SON XML input file.

    Note
    ----
    This function relies on the following helper functions:
    - son_input_to_str: Converts the SON XML input file to a string representation.
    - xml_tree_to_dict: Converts the XML Element tree to a nested Python dictionary.
    - parse_list_of_items: Parses a list of XML elements into a list of dictionaries.
    - parse_fuel_cycles: Helper function for parsing fuel cycles.
    - parse_reactor: Helper function for parsing reactor information.
    - parse_capital_cost_items: Helper function for parsing capital cost items.
    - parse_om_cost_items: Helper function for parsing operation and maintenance cost items.
    - parse_fuels: Helper function for parsing fuels.
    """

    xml_str = son_input_to_str(input_path, necost_path)
    xml_dict = xml_tree_to_dict(ElementTree.fromstring(xml_str))
    result = xml_dict["document"]["necost"]
    return {
        "construction_interest_rate": float(getval(result["construction_interest_rate"])),
        "operations_interest_rate": float(getval(result["operations_interest_rate"])),
        "sample_size": int(getval(result["sample_size"])),
        "fuel_cycles": parse_list_of_items(result["fuel_cycles"]["cycle"], parse_fuel_cycles),
        "reactors": parse_list_of_items(result["reactors"]["reactor"], parse_reactor),
        "capital_costs": parse_list_of_items(result["capital_costs"]["item"], parse_capital_cost_items),
        "om_costs": parse_list_of_items(result["om_costs"]["item"], parse_om_cost_items),
        "fuel_costs": parse_list_of_items(result["fuel_costs"]["item"], parse_fuel_cost_items),
        "fuels": parse_list_of_items(result["fuels"]["fuel"], parse_fuels),
    }


def parse_list_of_items(inp: Union[List, Dict], callback: Callable[[Dict], Dict]):
    """
    Parses a list of items using the specified callback function and returns a list of dictionaries.

    This function takes an input 'inp', which can be either a list of dictionaries or a single dictionary.
    The 'callback' function is applied to each item in the list, and the result is returned as a new list
    of dictionaries.

    Parameters
    ----------
    inp : Union[List, Dict]
        The input data, either a list of dictionaries or a single dictionary.
    callback : Callable[[Dict], Dict]
        The callback function to be applied to each item in the list.

    Returns
    -------
    List[Dict]
        A list of dictionaries containing the results after applying the 'callback' function to each item.
    """
    return [callback(r) for r in (inp if isinstance(inp, List) else [inp])]


def getval(x: Dict) -> str:
    """
    Retrieves the value from a nested dictionary.

    This function takes a nested dictionary 'x' and extracts the value associated with the key '#text'
    under the 'value' key.

    Parameters
    ----------
    x: Dict
        The input nested dictionary.

    Returns
    -------
    str
        The value extracted from the nested dictionary.
    """
    return x["value"]["#text"]


def parse_fuel_cycles(cycle: Dict):
    """
    Parse fuel cycles data from a dictionary representation.

    This function takes a dictionary representing a fuel cycle and extracts relevant information
    such as cycle ID, reactor information, fleet capacity, and fleet energy.

    Parameters
    ----------
    cycle : dict
        A dictionary containing fuel cycle data.

    Returns
    -------
    dict
        A dictionary containing parsed fuel cycle information.
    """
    return {
        "cycle": cycle["id"]["#text"],
        "reactors": parse_list_of_items(
            cycle["reactor"], lambda x: {
                "reactor": x["id"]["#text"],
                "fleet_capacity": float(getval(x["fleet_capacity"])),
                "fleet_energy": None if "fleet_energy" not in x else float(getval(x["fleet_energy"]))
            }
        )
    }


def parse_reactor(reactor: Dict):
    """
    Parse reactor data from a dictionary representation.

    This function takes a dictionary representing a reactor and extracts relevant information
    such as reactor ID, power level, capacity factor, cycle length, lifetime in years, capital costs,
    operation and maintenance (O&M) costs, and fuel reloads.

    Parameters
    ----------
    reactor : dict
        A dictionary containing reactor data.

    Returns
    -------
    dict
        A dictionary containing parsed reactor information.
    """
    power_level = reactor["power_level"]

    reference_net_electrical = None
    if "reference_net_electrical" in power_level.keys():
        reference_net_electrical = float(getval(power_level["reference_net_electrical"]))

    reference_thermal = None
    if "reference_thermal" in power_level.keys():
        reference_thermal = float(getval(power_level["reference_thermal"]))

    capital_costs = None if "scaling_factor" not in reactor["capital_costs"] else parse_list_of_items(
        inp=reactor["capital_costs"]["scaling_factor"],
        callback=lambda x: {"id": x["id"]["#text"], "scaling_factor": float(getval(x))}
    )

    om_costs = None if "scaling_factor" not in reactor["om_costs"] else parse_list_of_items(
        inp=reactor["om_costs"]["scaling_factor"],
        callback=lambda x: {"id": x["id"]["#text"], "scaling_factor": float(getval(x))}
    )

    fuel_reloads = None if "quantity" not in reactor["fuel_reloads"] else parse_list_of_items(
        inp=reactor["fuel_reloads"]["quantity"],
        callback=lambda x: {
            "id": x["id"]["#text"],
            "heavy_metal_mass": float(getval(x["heavy_metal_mass"])) if "heavy_metal_mass" in x else None,
            "thermal_power_fraction": float(
                getval(x["thermal_power_fraction"])
            ) if "thermal_power_fraction" in x else None
        }
    )

    return {
        "id": reactor["id"]["#text"],
        "power_level": {
            "net_thermal_efficiency": float(getval(power_level["net_thermal_efficiency"])),
            "reference_net_electrical": reference_net_electrical,
            "reference_thermal": reference_thermal,
        },
        "capacity_factor": float(getval(reactor["capacity_factor"])),
        "cycle_length": float(getval(reactor["capacity_factor"])),
        "lifetime_years": float(getval(reactor["capacity_factor"])),
        "capital_costs": capital_costs,
        "om_costs": om_costs,
        "fuel_reloads": fuel_reloads
    }


def parse_capital_cost_items(item: Dict):
    """
    Parse capital cost items from a dictionary representation.

    This function takes a dictionary representing a capital cost item and extracts relevant information
    such as item ID, cost value, cost type, expenditures, and additional cost distributions.

    Parameters
    ----------
    item : dict
        A dictionary containing capital cost item data.

    Returns
    -------
    dict
        A dictionary containing parsed capital cost item information.
    """
    return {
        "id": item["id"]["#text"],
        "cost_value": None if "cost_value" not in item else float(getval(item["cost_value"])),
        "cost_type": getval(item["cost_type"]),
        "expenditure_time": float(getval(item["expenditure_time"])),
        **get_cost_distributions(item)
    }


def parse_om_cost_items(item: Dict):
    """
    Parse operation and maintenance (O&M) cost items from a dictionary representation.

    This function takes a dictionary representing an O&M cost item and extracts relevant information
    such as item ID, cost type, and expenditure time.

    Parameters
    ----------
    item : dict
        A dictionary containing O&M cost item data.

    Returns
    -------
    dict
        A dictionary containing parsed O&M cost item.

    Raises
    ------
    AssertionError
        If the O&M cost item data is missing the "expenditure_time" key when cost type is "single" or "periodic,"
        or if the "expenditure_time" key is present when cost type is "variable" or "fixed."
    """

    cost_id = item["id"]["#text"]
    cost_type = getval(item["cost_type"])

    expenditure_time = None
    if cost_type == "single" or cost_type == "periodic":
        err_msg = f"Expected 'expenditure_time' for O&M cost item '{cost_id}' when cost type is '{cost_type}'."
        assert "expenditure_time" in item.keys(), err_msg
        expenditure_time = getval(item["expenditure_time"])
    else:
        err_msg = f"Did not expect 'expenditure_time' for O&M cost item '{cost_id}' when cost type is '{cost_type}'."
        assert "expenditure_time" not in item.keys(), err_msg

    return {
        "id": cost_id,
        "cost_type": cost_type,
        "expenditure_time": expenditure_time,
        **get_cost_distributions(item)
    }


def parse_fuel_cost_items(item: Dict):
    """
    Parse fuel cost items from a dictionary representation.

    This function takes a dictionary representing a fuel cost item and extracts relevant information
    such as item ID, cost value, and optional distribution.

    Parameters
    ----------
    item : dict
        A dictionary containing fuel cost item data.

    Returns
    -------
    dict
        A dictionary containing parsed fuel cost item.
    """

    cost_id = item["id"]["#text"]
    cost_value = float(getval(item["cost_value"]))
    lead_time = 0 if "lead_time" not in item.keys() else float(getval(item["lead_time"]))
    return {
        "id": cost_id,
        "cost_value": cost_value,
        "lead_time": lead_time,
        **get_cost_distributions(item, cost_value)
    }


def get_cost_distributions(inp: Dict, default: float = None):
    """
    Extract cost distributions from a dictionary representation.

    This function takes a dictionary representing cost distribution data and extracts relevant information
    such as the type of distribution, minimum value, nominal value, and maximum value.

    Parameters
    ----------
    inp : dict
        A dictionary containing cost distribution data.
    default : float
        In the case that no distribution and no nominal value is present in the input, use the `default` value
        for the min, nominal, and max values.

    Returns
    -------
    dict
        A dictionary containing parsed cost distribution information.
    """
    distribution = None

    if "nominal_value" in inp.keys():
        nominal_val = float(getval(inp["nominal_value"]))
        min_val = max_val = nominal_val
    elif "distribution" in inp.keys():
        distribution = getval(inp["distribution"]["type"])
        min_val = getval(inp["distribution"]["low"])
        nominal_val = getval(inp["distribution"]["nominal"])
        max_val = getval(inp["distribution"]["high"])
    else:
        min_val = nominal_val = max_val = default
        print(f"Warning: No distribution or nominal value found for cost item '{inp['id']['#text']}'.")
        distribution = 0

    return {
        "distribution": distribution,
        "min": min_val,
        "nominal": nominal_val,
        "max": max_val,
    }


def parse_fuels(fuel: Dict):
    """
    Parse fuel data from a dictionary representation.

    This function takes a dictionary representing fuel data and extracts relevant information
    such as fuel ID, average specific power, average discharge burnup, average fuel residence time,
    fresh fuel composition, fabrication, reprocessing, and discharge fuel composition.

    Parameters
    ----------
    fuel : dict
        A dictionary containing fuel data.

    Returns
    -------
    dict
        A dictionary containing parsed fuel information.
    """

    def get_array(obj: dict):
        return parse_list_of_items(obj, lambda x: x["#text"])

    def get_lead_time_and_costs(obj, kind: int = 1):
        # leadtime is optional for all types

        type1 = {} if "lead_time" not in obj.keys() else {"lead_time": float(getval(obj["lead_time"]))}
        type2 = {} if kind != 2 else {"loss_fraction": float(getval(obj["loss_fraction"]))}
        type3 = {} if kind != 3 else {"fuel_fraction": float(getval(obj["fuel_fraction"]))}

        return {
            **type1, **type2, **type3,
            "costs": get_array(obj["costs"]["value"]),
        }
    avg_discharge_burnup = None
    if "avg_discharge_burnup" in fuel.keys():
        avg_discharge_burnup = float(getval(fuel["avg_discharge_burnup"]))
    
    num_batches = None
    if "num_batches" in fuel.keys():
        num_batches = float(getval(fuel["num_batches"]))

    avg_specific_power = None
    if "avg_specific_power" in fuel.keys():
        avg_specific_power = float(getval(fuel["avg_specific_power"]))
    
    fresh_fuel = fuel["fresh_fuel" ]
    fabrication = get_lead_time_and_costs(fresh_fuel["fabrication"], kind=2)
    fresh_fuel_DU = get_lead_time_and_costs(fresh_fuel["DU"], kind=3)
    fresh_fuel_NU = get_lead_time_and_costs(fresh_fuel["NU"], kind=3)
    fresh_fuel_EU = get_lead_time_and_costs(fresh_fuel["EU"], kind=3)
    fresh_fuel_RU = get_lead_time_and_costs(fresh_fuel["RU"], kind=3)
    fresh_fuel_Th = get_lead_time_and_costs(fresh_fuel["Th"], kind=3)
    fresh_fuel_TRU = get_lead_time_and_costs(fresh_fuel["TRU"], kind=3)
    fresh_fuel_FP = get_lead_time_and_costs(fresh_fuel["FP"], kind=3)

    spent_fuel = fuel["spent_fuel"]
    spent_fuel_FP = get_lead_time_and_costs(spent_fuel["FP"], kind=3)
    spent_fuel_costs = get_array(spent_fuel["costs"]["value"])

    EU = fuel["EU"]
    EU_conversion = get_lead_time_and_costs(EU["conversion"], kind=2)
    EU_enrichment = EU["enrichment"]
    EU_enrichment_type = getval(EU_enrichment["type"])
    EU_enrichment_loss = float(getval(EU_enrichment["loss_fraction"]))
    EU_enrichment_stage_1 = {"feed": float(getval(EU_enrichment["stage_1"]["feed"])),
                            "product": float(getval(EU_enrichment["stage_1"]["product"])),
                            "tails": float(getval(EU_enrichment["stage_1"]["tails"]))}
    if EU_enrichment_type == "two_stage":
        EU_enrichment_stage_2 = {"feed": float(getval(EU_enrichment["stage_2"]["feed"])),
                                "product": float(getval(EU_enrichment["stage_2"]["product"])),
                                "tails": float(getval(EU_enrichment["stage_2"]["tails"]))}
    else:
        EU_enrichment_stage_2 = None
    EU_enrichment_SWU_costs = get_array(EU_enrichment["SWU_costs"]["value"])
    EU_enrichment_NU_costs = get_array(EU_enrichment["NU_costs"]["value"])
    EU_enrichment_DU_costs = get_array(EU_enrichment["DU_costs"]["value"])

    RU = fuel["RU"]
    RU_reprocess = get_lead_time_and_costs(RU["reprocess"], kind=2)
    RU_conversion = get_lead_time_and_costs(RU["conversion"], kind=2)
    RU_reenrichment = RU["reenrichment"]
    RU_reenrichment_loss = float(getval(RU_reenrichment["loss_fraction"]))
    RU_reenrichment_stage_1 = {"feed": float(getval(RU_reenrichment["stage_1"]["feed"])),
                               "product": float(getval(RU_reenrichment["stage_1"]["product"])),
                               "tails": float(getval(RU_reenrichment["stage_1"]["tails"]))}
    RU_reenrichment_SWU_costs = get_array(RU_reenrichment["SWU_costs"]["value"])
    RU_reenrichment_DU_costs = get_array(RU_reenrichment["DU_costs"]["value"])

    return {
        "id": fuel["id"]["#text"],
        "avg_discharge_burnup": avg_discharge_burnup,
        "num_batches": num_batches,
        "avg_specific_power": None if "avg_specific_power" not in fuel else float(getval(fuel["avg_specific_power"])),
        "fresh_fuel_composition": {
            "fabrication": fabrication,
            "DU":fresh_fuel_DU,
            "NU": fresh_fuel_NU,
            "EU": fresh_fuel_EU,
            "RU": fresh_fuel_RU,
            "Th": fresh_fuel_Th,
            "TRU": fresh_fuel_TRU,
            "FP": fresh_fuel_FP
            },
        "spent_fuel": {
            "FP": spent_fuel_FP,
            "costs": spent_fuel_costs
        },
        "EU": {
            "conversion": EU_conversion,
            "enrichment": {
                "loss_fraction": EU_enrichment_loss,
                "stage_1": EU_enrichment_stage_1,
                "stage_2": EU_enrichment_stage_2,
                "SWU_costs": EU_enrichment_SWU_costs,
                "NU_costs": EU_enrichment_NU_costs,
                "DU_costs": EU_enrichment_DU_costs
            }
        },
        "RU": {
            "reprocess": RU_reprocess,
            "conversion": RU_conversion,
            "reenrichment": {
                "loss_fraction": RU_reenrichment_loss,
                "stage_1": RU_reenrichment_stage_1,
                "SWU_costs": RU_reenrichment_SWU_costs,
                "DU_costs": RU_reenrichment_DU_costs
            }
        }
    }
# Example of the XML structure for the fuel data






# 5 EU|conversion|loss_fraction|value|#text: 0.01
# 4 EU|conversion|costs|value: [{'@loc': '88.59', '#text': 'cost_conv'}, {'@loc': '88.69', '#text': 'cost_deconv'}]
# 5 EU|enrichment|type|value|#text: two_stage
# 5 EU|enrichment|loss_fraction|value|#text: 0.01
# 6 EU|enrichment|stage_1|feed|value|#text: 0.711
# 6 EU|enrichment|stage_1|product|value|#text: 4.2
# 6 EU|enrichment|stage_1|tails|value|#text: 0.25
# 6 EU|enrichment|stage_2|feed|value|#text: 0.711
# 6 EU|enrichment|stage_2|product|value|#text: 4.2
# 6 EU|enrichment|stage_2|tails|value|#text: 0.25
# 5 EU|enrichment|SWU_costs|value|#text: cost_SWU
# 5 EU|enrichment|NU_costs|value|#text: cost_U
# 5 EU|enrichment|DU_costs|value|#text: cost_DU_disposal
# 5 RU|reprocess|loss_fraction|value|#text: 0.01
# 4 RU|reprocess|costs|value: [{'@loc': '100.58', '#text': 'cost_conv'}, {'@loc': '100.68', '#text': 'cost_deconv'}]
# 5 RU|conversion|loss_fraction|value|#text: 0.01
# 4 RU|conversion|costs|value: [{'@loc': '101.59', '#text': 'cost_conv'}, {'@loc': '101.69', '#text': 'cost_deconv'}]
# 5 RU|reenrichment|loss_fraction|value|#text: 0.01
# 6 RU|reenrichment|stage_1|feed|value|#text: 0.711
# 6 RU|reenrichment|stage_1|product|value|#text: 4.2
# 6 RU|reenrichment|stage_1|tails|value|#text: 0.25
# 5 RU|reenrichment|SWU_costs|value|#text: cost_SWU
# 5 RU|reenrichment|DU_costs|value|#text: cost_DU_disposal


    # ffc = fuel["fresh_fuel_composition"]

    # avg_discharge_burnup = None
    # if "avg_discharge_burnup" in fuel.keys():
    #     avg_discharge_burnup = float(getval(fuel["avg_discharge_burnup"]))
    
    # num_batches = None
    # if "num_batches" in fuel.keys():
    #     num_batches = float(getval(fuel["num_batches"]))

    # avg_fuel_residence_time = None
    # if "avg_fuel_residence_time" in fuel.keys():
    #     avg_fuel_residence_time = float(getval(fuel["avg_fuel_residence_time"]))

    # two_stage_params = None
    # if "two_stage_params" in ffc["enriched_uranium"]:
    #     two_stage_params = {
    #         "stage_1_enrichment": float(getval(ffc["enriched_uranium"]["two_stage_params"]["stage_1_enrichment"])),
    #         "stage_1_tails": float(getval(ffc["enriched_uranium"]["two_stage_params"]["stage_1_tails"])),
    #     }

    # def get_array(obj: dict):
    #     return parse_list_of_items(obj, lambda x: x["#text"])

    # def get_lead_time_and_costs(obj, kind: int = 1):
    #     type1 = {} if kind == 3 else {"lead_time": float(getval(obj["lead_time"]))}
    #     type2 = {} if kind != 2 else {"loss_fraction": float(getval(obj["loss_fraction"]))}
    #     type3 = {} if kind != 3 else {"fraction_disposed": float(getval(obj["fraction_disposed"]))}

    #     return {
    #         **type1, **type2, **type3,
    #         "costs": get_array(obj["costs"]["value"]),
    #     }

    # rec_u_frac_params = {"product": None, "tails": None, "losses": None, 'feed': None}
    # ruf_is_reenrichment = getval(ffc["recovered_uranium_fraction"]["is_reenrichment"]) == "yes"
    # if ruf_is_reenrichment:
    #     rec_u_frac_params["product"] = float(getval(ffc["recovered_uranium_fraction"]["product"]))
    #     rec_u_frac_params["tails"] = float(getval(ffc["recovered_uranium_fraction"]["tails"]))
    #     rec_u_frac_params["losses"] = float(getval(ffc["recovered_uranium_fraction"]["losses"]))
    #     rec_u_frac_params["feed"] = float(getval(ffc["recovered_uranium_fraction"]["feed"]))

    # return {
    #     "id": fuel["id"]["#text"],
    #     "avg_specific_power": None if "avg_specific_power" not in fuel else float(getval(fuel["avg_specific_power"])),
    #     "avg_discharge_burnup": avg_discharge_burnup,
    #     "num_batches": num_batches,
    #     "avg_fuel_residence_time": avg_fuel_residence_time,
    #     "fresh_fuel_composition": {
    #         "depleted_uranium": {
    #             "fuel_fraction": float(getval(ffc["depleted_uranium"]["fuel_fraction"])),
    #             "lead_time": float(getval(ffc["depleted_uranium"]["lead_time"])),
    #             "costs": get_array(ffc["depleted_uranium"]["costs"]["value"]),
    #             "avoided_costs": None if "avoided_costs" not in ffc["depleted_uranium"] else
    #             get_array(ffc["depleted_uranium"]["avoided_costs"]["value"])
    #         },
    #         "natural_uranium": {
    #             "fuel_fraction": float(getval(ffc["natural_uranium"]["fuel_fraction"])),
    #             "lead_time": float(getval(ffc["natural_uranium"]["lead_time"])),
    #             "costs": get_array(ffc["natural_uranium"]["costs"]["value"]),
    #         },
    #         "thorium_fraction": {} if "thorium_fraction" not in ffc else {
    #             "fuel_fraction": float(getval(ffc["thorium_fraction"]["loss_fraction"])),
    #             "lead_time": float(getval(ffc["thorium_fraction"]["lead_time"])),
    #             "costs": get_array(ffc["thorium_fraction"]["costs"]["value"]),
    #         },
    #         "recovered_th_fraction_costs": None if "recovered_th_fraction_costs" not in ffc else get_array(ffc["recovered_th_fraction_costs"]["value"]),
    #         "enriched_uranium": {
    #             "type": getval(ffc["enriched_uranium"]["type"]),
    #             "product": float(getval(ffc["enriched_uranium"]["product"])),
    #             "feed": float(getval(ffc["enriched_uranium"]["feed"])),
    #             "tails": float(getval(ffc["enriched_uranium"]["tails"])),
    #             "two_stage_params": two_stage_params,
    #             "NU_costs": get_lead_time_and_costs(ffc["enriched_uranium"]["NU_costs"]),
    #             "DU_costs": get_lead_time_and_costs(ffc["enriched_uranium"]["DU_costs"]),
    #             "conversion": get_lead_time_and_costs(ffc["enriched_uranium"]["conversion"], kind=2),
    #             "stage_1_enrichment_costs": { # if two_stage_params is None, this is not present
    #                 **get_lead_time_and_costs(ffc["enriched_uranium"]["stage_1_enrichment_costs"], kind=2)
    #             },
    #             # stage_2_enrichment_costs may not be in ffc["enriched_uranium"]
    #             # so if ffc["enriched_uranium"] do not have key "stage_2_enrichment_costs"
    #             # then it will return an empty dictionary
    #             # if it has the key, then it will return the dictionary
    #             # with the values of the key "stage_2_enrichment_costs"
    #             # and the key "lead_time" with the value of the key "lead_time"
    #             # and the key "costs" with the value of the key "costs"
    #             # and the key "loss_fraction" with the value of the key "loss_fraction"
    #             "stage_2_enrichment_costs": { None: {} } if "stage_2_enrichment_costs" not in ffc["enriched_uranium"] else {
    #                 **get_lead_time_and_costs(ffc["enriched_uranium"]["stage_2_enrichment_costs"], kind=2)
    #             },
    #         },
    #         "recovered_uranium_fraction": {
    #             "is_reenrichment": ruf_is_reenrichment,
    #             **rec_u_frac_params,
    #             "loss_fraction": float(getval(ffc["recovered_uranium_fraction"]["loss_fraction"])),
    #             "costs": get_array(ffc["recovered_uranium_fraction"]["costs"]["value"]),
    #         },
    #         "recovered_tru_fraction": None if "recovered_tru_fraction" not in ffc else {
    #             "np": float(getval(ffc["recovered_tru_fraction"]["np"])),
    #             "pu": float(getval(ffc["recovered_tru_fraction"]["pu"])),
    #             "am_cm": float(getval(ffc["recovered_tru_fraction"]["am_cm"])),
    #             "costs": get_array(ffc["recovered_tru_fraction"]["costs"]["value"])
    #         }
    #     },
    #     "fabrication": get_lead_time_and_costs(fuel["fabrication"], kind=2),
    #     "reprocessing": None if "reprocessing" not in fuel else {
    #         "fuel_id": getval(fuel["reprocessing"]["fuel_id"]),
    #         "time_after_discharge": float(getval(fuel["reprocessing"]["time_after_discharge"])),
    #         "sep_leadtime": float(getval(fuel["reprocessing"]["sep_leadtime"])),
    #         "sep_losses": float(getval(fuel["reprocessing"]["sep_losses"])),
    #         "waste_management_costs": {
    #             "th": get_lead_time_and_costs(fuel["reprocessing"]["waste_management_costs"]["th"], kind=3),
    #             "ru": get_lead_time_and_costs(fuel["reprocessing"]["waste_management_costs"]["ru"], kind=3),
    #             "np": get_lead_time_and_costs(fuel["reprocessing"]["waste_management_costs"]["np"], kind=3),
    #             "pu": get_lead_time_and_costs(fuel["reprocessing"]["waste_management_costs"]["pu"], kind=3),
    #             "am_cm": get_lead_time_and_costs(fuel["reprocessing"]["waste_management_costs"]["am_cm"], kind=3),
    #             "fp": get_lead_time_and_costs(fuel["reprocessing"]["waste_management_costs"]["fp"], kind=3),
    #         },
    #         "avoided_costs": get_array(fuel["reprocessing"]["avoided_costs"]["value"])
    #     },
    #     # "discharge_fuel_composition": None if "discharge_fuel_composition" not in fuel else parse_list_of_items(
    #     #     inp=fuel["discharge_fuel_composition"]["year"],
    #     #     callback=lambda x: {
    #     #         "year": x["id"]["#text"],
    #     #         "th": float(getval(x["th"])),
    #     #         "u": float(getval(x["u"])),
    #     #         "u235": float(getval(x["u235"])),
    #     #         "np": float(getval(x["np"])),
    #     #         "pu": float(getval(x["pu"])),
    #     #         "am_cm": float(getval(x["am_cm"])),
    #     #         "fp": float(getval(x["fp"])),
    #     #     }
    #     # )
    # }
