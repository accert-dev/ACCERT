import numpy as np
import pandas as pd


def function_1(data: pd.DataFrame, batches_ref, t_plant, efpy, efpy_ref):
    # NOTE: This function is partially vectorized.

    condition = data["L_direct_spec"] <= 0
    # If true, the value of the capacity factor will be calculated [i.e. not an input], else
    # remember that we are calculating L based on forced outages etc...
    l_inp = np.where(condition, False, True)
    t_fl = np.where(condition, np.nan, efpy / data["L_direct_spec"])
    t_cyc = np.where(condition, np.nan, t_fl / data["num_batches"])
    planned_outage = np.where(condition, data["outage_ref"], np.nan)

    # We use a loop here since this part of the code is difficult to vectorize. However, we
    # extract the numpy arrays to minimize the overhead costs of accessing values from Pandas.
    indices = np.where(condition)[0]
    forced_outage_rate = data["forced_outage_rate"][indices]
    num_batches = data["num_batches"][indices]
    outage_ref = data["outage_ref"][indices]
    forced_outage_rate_ref = data["forced_outage_rate_ref"][indices]
    outage_refuel = data["outage_refuel"][indices]
    outage_cooldown_heatup = data["outage_cooldown_heatup"][indices]
    for idx in range(len(indices)):
        # The loop variable `idx` refers to any element of the selected values above. The local
        # variable `data_idx`, however, refers to the index of the filtered elements in the condition.
        data_idx = indices[idx]

        t_av = efpy[data_idx] / (1 - forced_outage_rate[idx])  # total available cycle length over fuel lifetime [years]
        t_fl[data_idx] = t_av + (num_batches[idx] * outage_ref[idx])  # GUESS based on reference outage [years]

        # initial guess for total fuel lifetime assuming reference core planned outage length [years]
        t_cyc_tmp = [
            (efpy_ref[data_idx] / (1 - forced_outage_rate_ref[idx]) + (batches_ref * outage_ref[idx])) / batches_ref,
            t_fl[data_idx] / num_batches[idx]
        ]

        # part of the outage that does not scale with cycle length [yrs] [data in [1]
        planned_outage_non_scale = outage_refuel[idx] + outage_cooldown_heatup[idx]
        planned_outage_scale = outage_ref[idx] - planned_outage_non_scale

        # Iterate between planned_outage_scale and t_cyc
        while abs(t_cyc_tmp[1] - t_cyc_tmp[0]) >= (0.05 / 365.5):
            planned_outage = planned_outage_non_scale + (t_cyc_tmp[1] / t_cyc_tmp[1]) * planned_outage_scale
            planned_outage_scale = planned_outage[data_idx] - planned_outage_non_scale

            t_fl[data_idx] = t_av + num_batches[idx] * planned_outage[data_idx]
            t_cyc_tmp[0] = t_cyc_tmp[1]
            t_cyc_tmp[1] = t_fl[data_idx] / num_batches[idx]

            if abs(t_cyc_tmp[1] - t_cyc_tmp[0]) > abs(t_cyc_tmp[1] - t_cyc_tmp[0]):
                print("Error is growing: Exiting the loop prematurely.")
                print(f"---> Error days: {(t_cyc_tmp[1] - t_cyc_tmp[0]) * 365}")
                break

        t_cyc[data_idx] = t_cyc_tmp[1]

        # capacity factor - it also updates the pv_back_end_fuel_storage includes planned and un-planned outages
        # TODO: Should not modify the dataframe directly.
        # case["L_direct_spec"] = efpy / t_fl

    n_cycl = t_plant // t_cyc  # number of batches throughout the core life
    return l_inp, n_cycl, t_cyc, planned_outage
