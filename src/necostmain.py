import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
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






def _input_dir(input_path):
    return Path(input_path).resolve().parent


def _resolve_path(path, base_dir):
    if not path:
        return None
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return Path(base_dir, candidate).resolve()


def _read_accert_occ_per_kw(post_csv, metric="total_OCC"):
    post = pd.read_csv(post_csv)
    row = post.loc[post["metric"].astype(str).eq(metric)]
    if row.empty:
        raise ValueError(f"Could not find ACCERT post-process metric '{metric}' in {post_csv}")
    if "value_2024_dollar_per_kw" in row.columns and pd.notna(row["value_2024_dollar_per_kw"].iloc[0]):
        return float(row["value_2024_dollar_per_kw"].iloc[0])
    if "value_dollar_per_kw" in row.columns and pd.notna(row["value_dollar_per_kw"].iloc[0]):
        return float(row["value_dollar_per_kw"].iloc[0])
    raise ValueError(f"ACCERT post-process file {post_csv} does not include an OCC $/kW column")


def _run_accert(input_path, output_dir):
    main_path = Path(__file__).resolve().parent / "Main.py"
    before = {p.resolve() for p in Path(output_dir).glob("*_post_*.csv")}
    subprocess.run(
        [sys.executable, str(main_path), "-i", str(input_path)],
        cwd=output_dir,
        check=True,
    )
    candidates = [p for p in Path(output_dir).glob("*_post_*.csv") if p.resolve() not in before]
    if not candidates:
        candidates = list(Path(output_dir).glob("*_post_*.csv"))
    if not candidates:
        raise FileNotFoundError("ACCERT run did not produce a *_post_*.csv file")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _apply_accert_coupling(res, input_path, output_dir):
    coupling = res.get("accert_coupling")
    if not coupling:
        return None

    base_dir = _input_dir(input_path)
    post_csv = _resolve_path(coupling.get("accert_post_csv"), base_dir)
    if post_csv is None:
        accert_input = _resolve_path(coupling.get("accert_input"), base_dir)
        if accert_input is None:
            raise ValueError("accert_coupling requires either accert_input or accert_post_csv")
        post_csv = _run_accert(accert_input, output_dir)

    occ_metric = coupling.get("occ_metric", "total_OCC")
    occ_per_kw = _read_accert_occ_per_kw(post_csv, metric=occ_metric)
    uncertainty = float(coupling.get("uncertainty_fraction", 0.0) or 0.0)
    cost_id = coupling.get("capital_cost_id", "capital_cost")
    low = occ_per_kw * (1 - uncertainty)
    high = occ_per_kw * (1 + uncertainty)

    matched = False
    for item in res.get("capital_costs", []):
        if item.get("id") == cost_id:
            item.update({
                "distribution": "triangular",
                "min": low,
                "nominal": occ_per_kw,
                "max": high,
            })
            matched = True
    if not matched:
        res.setdefault("capital_costs", []).append({
            "id": cost_id,
            "cost_type": "s_curve",
            "expenditure_time": 5,
            "distribution": "triangular",
            "min": low,
            "nominal": occ_per_kw,
            "max": high,
        })

    return {
        "accert_post_csv": str(post_csv),
        "capital_cost_id": cost_id,
        "occ_metric": occ_metric,
        "occ_2024_dollar_per_kw": occ_per_kw,
    }


def _reactor_weight_map(res):
    weights = {}
    for cycle in res.get("fuel_cycles", []):
        for reactor in cycle.get("reactors", []):
            reactor_id = reactor["reactor"]
            if reactor.get("fleet_energy") is not None:
                weights[reactor_id] = float(reactor["fleet_energy"])
            elif reactor.get("energy_fraction") is not None:
                weights[reactor_id] = float(reactor["energy_fraction"])
            elif reactor.get("mass_fraction") is not None:
                weights[reactor_id] = float(reactor["mass_fraction"])
            else:
                weights[reactor_id] = float(reactor.get("fleet_capacity") or 1.0)
    return weights


def _reference_capacity_mwe(reactor):
    power_level = reactor.get("power_level") or {}
    if power_level.get("reference_net_electrical") is not None:
        return float(power_level["reference_net_electrical"]) / 1e6
    if power_level.get("reference_thermal") is None:
        return None
    efficiency = float(power_level.get("net_thermal_efficiency") or 0.0)
    return float(power_level["reference_thermal"]) * efficiency / 100.0 / 1e6


def _validate_cycle_weight_inputs(res, tolerance=1e-3):
    reactors_by_id = {reactor["id"]: reactor for reactor in res.get("reactors", [])}
    for cycle in res.get("fuel_cycles", []):
        for cycle_reactor in cycle.get("reactors", []):
            if (
                cycle_reactor.get("fleet_capacity") is None
                or (
                    cycle_reactor.get("energy_fraction") is None
                    and cycle_reactor.get("mass_fraction") is None
                )
            ):
                continue

            reactor_id = cycle_reactor["reactor"]
            expected = _reference_capacity_mwe(reactors_by_id.get(reactor_id, {}))
            if expected is None or expected == 0:
                continue

            supplied = float(cycle_reactor["fleet_capacity"])
            rel_error = abs(supplied - expected) / expected
            if rel_error > tolerance:
                raise ValueError(
                    f"fleet_capacity for {reactor_id} is {supplied:g} MWe, but the "
                    f"reactor power block implies {expected:g} MWe. If an "
                    "energy_fraction or mass_fraction is provided, fleet_capacity is "
                    "optional; omit it unless it is the physical MWe capacity."
                )


def _default_inputs(code_folder):
    return pd.read_csv(f"{code_folder}/necost/default_input.csv").set_index("var_name").transpose()


def _run_single_reactor(res, reactor, code_folder, discount_rate, sample_size):
    default_inputs = _default_inputs(code_folder)
    fuel_ids = {reload["id"] for reload in (reactor.get("fuel_reloads") or [])}
    fuels = [fuel for fuel in res.get("fuels", []) if not fuel_ids or fuel.get("id") in fuel_ids]
    reactor_res = {**res, "reactors": [reactor], "fuels": fuels}
    default_inputs = update_default_inputs_reactor(default_inputs, reactor_res, mapping_with_distribution)
    monte_carlo_data = generate_monte_carlo_samples(
        params_data=default_inputs,
        sampling_amount=sample_size,
        discount_rate=discount_rate * 100,
    )
    results = NECost(data=monte_carlo_data, **default_params).run()
    return results.drop(columns=["HM_mass_direct_spec", "t_cyc", "L_direct_spec"], errors="ignore")


def _weighted_cycle_results(reactor_results, weights):
    if len(reactor_results) == 1:
        reactor_id, results = next(iter(reactor_results.items()))
        out = results.copy()
        out.insert(0, "reactor_id", reactor_id)
        return out

    weight_sum = sum(weights.get(reactor_id, 1.0) for reactor_id in reactor_results)
    if weight_sum <= 0:
        weight_sum = float(len(reactor_results))
    combined = None
    for reactor_id, results in reactor_results.items():
        frac = weights.get(reactor_id, 1.0) / weight_sum
        numeric = results[["Capital", "LCOE", "O&M", "FCC"]] * frac
        combined = numeric if combined is None else combined.add(numeric, fill_value=0)
    combined.insert(0, "reactor_id", "weighted_cycle")
    return combined


def run_necost(input_path, output_dir=None, make_plot=True):
    code_folder = os.path.dirname(os.path.abspath(__file__))
    necost_path = os.path.abspath(os.path.join(code_folder, os.pardir))
    input_path = Path(input_path).resolve()
    output_dir = Path(output_dir or os.getcwd()).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    res = parse_son_input(str(input_path), necost_path)
    _validate_cycle_weight_inputs(res)
    coupling_summary = _apply_accert_coupling(res, input_path, output_dir)
    discount_rate = res.get("operations_interest_rate", 0.05)
    sample_size = res.get("sample_size", 40000)
    print(f"Discount rate: {discount_rate}")
    print(f"Sample size: {sample_size}")

    reactor_results = {}
    for reactor in res.get("reactors", []):
        reactor_results[reactor["id"]] = _run_single_reactor(
            res,
            reactor,
            code_folder,
            discount_rate,
            sample_size,
        )

    weights = _reactor_weight_map(res)
    results = _weighted_cycle_results(reactor_results, weights)
    reactor_detail = pd.concat(
        [df.assign(reactor_id=reactor_id) for reactor_id, df in reactor_results.items()],
        ignore_index=True,
    )

    results_csv = output_dir / "NECOST_results.csv"
    detail_csv = output_dir / "NECOST_reactor_results.csv"
    results.to_csv(results_csv, index=False)
    reactor_detail.to_csv(detail_csv, index=False)

    if make_plot:
        mpl_config = output_dir / ".mplconfig"
        mpl_config.mkdir(exist_ok=True)
        os.environ.setdefault("MPLCONFIGDIR", str(mpl_config))
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        plot_data = results.drop(columns=["reactor_id"], errors="ignore")
        bin_num = max(10, int(sample_size / 10))
        plot_data.plot(kind="hist", bins=bin_num, alpha=0.5)
        plt.title("NECOST Results")
        plt.xlabel("levelized cost ($/MWh)")
        plt.tight_layout()
        plt.savefig(output_dir / "NECOST_results.png")
        plt.close()

    with open(output_dir / "output.json", "w") as f:
        json.dump({"input": res, "accert_coupling": coupling_summary}, f, indent=4)

    print(f"Saved NEcost results to {results_csv}")
    if len(reactor_results) > 1:
        print(f"Saved per-reactor NEcost details to {detail_csv}")
    if coupling_summary:
        print(
            "ACCERT OCC coupling: "
            f"{coupling_summary['occ_2024_dollar_per_kw']:.2f} $/kWe "
            f"from {coupling_summary['accert_post_csv']}"
        )
    return results



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run NEcost from a SON input file.")
    parser.add_argument("-i", "--input", required=True, help="NEcost SON input file")
    parser.add_argument("-o", "--output-dir", default=os.getcwd(), help="Directory for NEcost outputs")
    parser.add_argument("--no-plot", action="store_true", help="Skip NECOST_results.png generation")
    args = parser.parse_args()

    if os.path.exists(args.input):
        run_necost(args.input, output_dir=args.output_dir, make_plot=not args.no_plot)
    else:
        print('NE-COST did not find the input file {}'.format(args.input))
        raise SystemExit
