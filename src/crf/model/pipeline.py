from .direct_cost import update_direct_cost
from .learning import learning_effect, act_cons_duration_plus_delay, duration_learning_effect
from .indirect_cost import update_indirect_cost
from .finance import tax_update, insurance_cost_update, decomission_cost_update, update_interest_cost, update_itc
import numpy as np

def calculate_final_result(config: dict, inp: dict, store, n_th: int, trace=None):
    """
    One unit (n_th) calculation.
    Returns: (final_df, levelized_net_OCC, levelized_NCI, final_construction_duration_scalar)
    """
    base0, power = store.get_baseline(config["reactor_type"])
    # direct updates (returns df + duration without supply chain delay)
    direct_df, dur_no_delay = update_direct_cost(
        store=store,
        reactor_type=config["reactor_type"],
        n_th=n_th,
        f_22=config["f_22"],
        f_2321=config["f_2321"],
        land_cost_per_acre_0=config["land_cost_per_acre_0"],
        RB_grade_0=inp["RB_grade_0"],
        BOP_grade_0=inp["BOP_grade_0"],
        num_orders=inp["num_orders"],
        design_completion_0=inp["design_completion_0"],
        ae_exp_0=inp["ae_exp_0"],
        N_AE=inp["N_AE"],
        ce_exp_0=inp["ce_exp_0"],
        N_cons=inp["N_cons"],
        mod_0=inp["mod_0"],
        trace=trace,
    )
    # duration: add delay + learning
    dur_plus_delay = act_cons_duration_plus_delay(
        reactor_type=config["reactor_type"],
        n_th=n_th,
        Design_Maturity_0=inp["Design_Maturity_0"],
        proc_exp_0=inp["proc_exp_0"],
        N_proc=inp["N_proc"],
        cons_duration_no_delay=dur_no_delay,
    )
    if trace is not None:
        trace["supply_chain_delay_months"] = float(dur_plus_delay) - float(dur_no_delay)
    final_dur = duration_learning_effect(reactor_type=config["reactor_type"], 
                                        n_th=n_th, 
                                        standardization_0=inp["standardization_0"], 
                                        actual_construction_duration_plus_delay=dur_plus_delay,
                                        n_of_NOAK=inp["num_orders"])
    no_supply_final_dur = duration_learning_effect(reactor_type=config["reactor_type"], 
                                        n_th=n_th, 
                                        standardization_0=inp["standardization_0"], 
                                        actual_construction_duration_plus_delay=dur_no_delay,
                                        n_of_NOAK=inp["num_orders"])
    if trace is not None:
        trace["duration_learning_months"] = float(final_dur) - float(dur_plus_delay)
    
    # learning on direct costs
    direct_plus_learning = learning_effect(direct_df, n_th, 
                                           inp["standardization_0"], 
                                           power, 
                                           config["reactor_type"],
                                           inp["num_orders"],
                                           trace=trace,
                                           )
    
    # indirect costs
    with_indirect = update_indirect_cost(n_th, inp["standardization_0"], direct_plus_learning, final_dur, power, reactor_type=config["reactor_type"])

    # Supplementary costs: tax, insurance, decommissioning
    with_tax = tax_update(with_indirect, power)
    with_insurance = insurance_cost_update(with_tax, power)
    with_decomm = decomission_cost_update(with_insurance, power)
    if trace is not None:
        no_supply_indirect = update_indirect_cost(
            n_th,
            inp["standardization_0"],
            direct_plus_learning,
            no_supply_final_dur,
            power,
            reactor_type=config["reactor_type"],
        )
        no_supply_tax = tax_update(no_supply_indirect, power)
        no_supply_insurance = insurance_cost_update(no_supply_tax, power)
        no_supply_decomm = decomission_cost_update(no_supply_insurance, power)
        trace["Supplychain efficiency"] = _occ_per_kwe(with_decomm, power) - _occ_per_kwe(no_supply_decomm, power)
        trace["indirect_cost_delta"] = _occ_per_kwe(with_indirect, power) - _occ_per_kwe(direct_plus_learning, power)
        trace["supplementary_cost_delta"] = _occ_per_kwe(with_decomm, power) - _occ_per_kwe(with_indirect, power)

    # Finance costs: interest during construction and ITC
    with_interest, tot_occ, tot_cap = update_interest_cost(
        store=store,
        df=with_decomm,
        final_construction_duration=final_dur,
        interest_rate=inp["interest_rate_0"],
        startup_0=config["startup_0"],
        n_th=n_th,
        power=power,
        reactor_type=config["reactor_type"],
    )

    org_occ = float(tot_occ/power)
    org_tci = float(tot_cap/power)  
    final_df, net_occ, nci = update_itc(with_interest, tot_occ, tot_cap, n_th, inp["ITC_0"], inp["n_ITC"], power)
    if trace is not None:
        trace["final_occ"] = org_occ
        trace["final_tci"] = org_tci

    # print(f"Final OCC for plant {n_th}: {net_occ}")
    # print(final_df)
    return final_df, org_occ, net_occ, org_tci, nci, float(final_dur)


def _occ_per_kwe(df, power):
    return float(
        df.loc[
            df["Title"].eq("Total Overnight Cost (Accounts 10 to 50)"),
            "Total Cost (USD)",
        ].iloc[0]
        / power
    )
