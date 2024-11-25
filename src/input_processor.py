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

    fuel_type = None if "quantity" not in reactor["fuel_type"] else parse_list_of_items(
        inp=reactor["fuel_type"]["quantity"],
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
        "fuel_type": fuel_type
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
    lead_time = 0 if "lead_time" not in item else float(getval(item["lead_time"]))

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
    ffc = fuel["fresh_fuel"]

    avg_discharge_burnup = None
    if "avg_discharge_burnup" in fuel.keys():
        avg_discharge_burnup = float(getval(fuel["avg_discharge_burnup"]))
    
    num_batches = None
    if "num_batches" in fuel.keys():
        num_batches = float(getval(fuel["num_batches"]))

    avg_fuel_residence_time = None
    if "avg_fuel_residence_time" in fuel.keys():
        avg_fuel_residence_time = float(getval(fuel["avg_fuel_residence_time"]))

    two_stage_params = None
    if "two_stage_params" in ffc["EU"]:
        two_stage_params = {
            "stage_1_enrichment": float(getval(ffc["EU"]["two_stage_params"]["stage_1_enrichment"])),
            "stage_1_tails": float(getval(ffc["EU"]["two_stage_params"]["stage_1_tails"])),
        }

    def get_array(obj: dict):
        return parse_list_of_items(obj, lambda x: x["#text"])

    def get_costs_and_others(obj, kind: int = 1):
        cost_ids = get_array(obj["costs"]["value"])

        type1 = {} #if kind == 1
        type2 = {} #if kind == 2 else {"fraction_disposed": float(getval(obj["fraction_disposed"]))}
        type3 = {"loss_fraction": float(getval(obj["loss_fraction"]))} if kind == 3 else {} 

        return {
            **type1, **type2, **type3,
            "costs": get_array(obj["costs"]["value"]),
        }

    rec_u_frac_params = {"product": None, "tails": None, "losses": None, 'feed': None}

    return {
        "id": fuel["id"]["#text"],
        "avg_specific_power": None if "avg_specific_power" not in fuel else float(getval(fuel["avg_specific_power"])),
        "avg_discharge_burnup": avg_discharge_burnup,
        "num_batches": num_batches,
        "avg_fuel_residence_time": avg_fuel_residence_time,
        "fresh_fuel": {
            "fabrication": {
                "loss": float(getval(ffc["fabrication"]["loss"])),
                'costs': get_array(ffc["fabrication"]["costs"]["value"])
            },
            "DU": None if "DU" not in ffc else {
                "fuel_fraction": float(getval(ffc["DU"]["fuel_fraction"])),
                "costs": get_array(ffc["DU"]["costs"]["value"]),
                "avoided_costs": None if "avoided_costs" not in ffc["DU"] else
                get_array(ffc["DU"]["avoided_costs"]["value"])
            },
            "NU": None if "NU" not in ffc else {
                "fuel_fraction": float(getval(ffc["NU"]["fuel_fraction"])),
                "costs": get_array(ffc["NU"]["costs"]["value"]),
            },
            "EU": None if "EU" not in ffc else {
                "fuel_fraction": float(getval(ffc["EU"]["fuel_fraction"])),
            },
            "RU": None if "RU" not in ffc else {
                "fuel_fraction": float(getval(ffc["RU"]["fuel_fraction"])),
            },
            "Th": None if "Th" not in ffc else {
                "fuel_fraction": float(getval(ffc["Th"]["fuel_fraction"])),
                "costs": get_array(ffc["Th"]["costs"]["value"]),
            },
            "TRU": None if "TRU" not in ffc else {
                "fuel_fraction": float(getval(ffc["TRU"]["fuel_fraction"])),
                "np": None if "np" not in ffc["TRU"] else float(getval(ffc["TRU"]["np"])),
                "pu": None if "pu" not in ffc["TRU"] else float(getval(ffc["TRU"]["pu"])),
                "am_cm": None if "am_cm" not in ffc["TRU"] else float(getval(ffc["TRU"]["am_cm"])),
                "costs": get_array(ffc["TRU"]["costs"]["value"])
            },
            "FP": None if "FP" not in ffc else {
                "fuel_fraction": float(getval(ffc["FP"]["fuel_fraction"])),
                "costs": get_array(ffc["FP"]["costs"]["value"]),
            }           
        },
        "spent_fuel": None if "spent_fuel" not in fuel else {
            "costs": get_array(fuel["spent_fuel"]["costs"]["value"]),
            "FP": None if "FP" not in fuel["spent_fuel"] else {
                "fuel_fraction": float(getval(fuel["spent_fuel"]["FP"]["fuel_fraction"])),
                "costs": get_array(fuel["spent_fuel"]["FP"]["costs"]["value"]),
            }},
        "EU": None if "EU" not in fuel else {
            "conversion": get_costs_and_others(fuel["EU"]["conversion"], kind=3),
            "enrichment": {
                "type": getval(fuel["EU"]["enrichment"]["type"]),
                "loss_fraction": float(getval(fuel["EU"]["enrichment"]["loss_fraction"])),
                "stage_1": {
                    "feed": float(getval(fuel["EU"]["enrichment"]["stage_1"]["feed"])),
                    "product": float(getval(fuel["EU"]["enrichment"]["stage_1"]["product"])),
                    "tails": float(getval(fuel["EU"]["enrichment"]["stage_1"]["tails"])),
                },
                "stage_2": None if "stage_2" not in fuel["EU"]["enrichment"] else {
                    "feed": float(getval(fuel["EU"]["enrichment"]["stage_2"]["feed"])),
                    "product": float(getval(fuel["EU"]["enrichment"]["stage_2"]["product"])),
                    "tails": float(getval(fuel["EU"]["enrichment"]["stage_2"]["tails"])),
                },
                "SWU_costs":{
                    "costs": get_array(fuel["EU"]["enrichment"]["SWU_costs"]["value"]),
                },
                "NU_costs": {"costs": get_array(fuel["EU"]["enrichment"]["NU_costs"]["value"]),},
                "DU_costs": {"costs": get_array(fuel["EU"]["enrichment"]["DU_costs"]["value"]),},
            },  
        },
        "RU": None if "RU" not in fuel else {
            "reprocessing": None if "reprocessing" not in fuel["RU"] else get_costs_and_others(fuel["RU"]["reprocessing"], kind=2),
            "conversion": get_costs_and_others(fuel["RU"]["conversion"], kind=2),
            "reenrichment": None if "reenrichment" not in fuel["RU"] else {
                "loss_fraction": float(getval(fuel["RU"]["reenrichment"]["loss_fraction"])),
                "stage_1": {
                    "feed": float(getval(fuel["RU"]["reenrichment"]["stage_1"]["feed"])),
                    "product": float(getval(fuel["RU"]["reenrichment"]["stage_1"]["product"])),
                    "tails": float(getval(fuel["RU"]["reenrichment"]["stage_1"]["tails"])),
                },
                "SWU_costs": {"costs": get_array(fuel["RU"]["reenrichment"]["SWU_costs"]["value"]),},
                "DU_costs": {"costs": get_array(fuel["RU"]["reenrichment"]["DU_costs"]["value"]),},
        },
        },
        "discharge_fuel_composition": None if "discharge_fuel_composition" not in fuel else parse_list_of_items(
            inp=fuel["discharge_fuel_composition"]["year"],
            callback=lambda x: {
                "year": x["id"]["#text"],
                "th": float(getval(x["th"])),
                "u": float(getval(x["u"])),
                "u235": float(getval(x["u235"])),
                "np": float(getval(x["np"])),
                "pu": float(getval(x["pu"])),
                "am_cm": float(getval(x["am_cm"])),
                "fp": float(getval(x["fp"])),
            }
        )
    }
