def closest(value, options):
    return min(options, key=lambda x: abs(x - value))

def apply_itc_rounding(lever_dict, allowed=(6, 30, 40, 50)):
    lever_dict["itc_percent"] = closest(lever_dict["itc_percent"], allowed)
    return lever_dict
