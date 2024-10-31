import sys, os

src_path = os.path.abspath(os.path.join(os.pardir, 'src'))
sys.path.insert(0, src_path)

import pandas as pd

from necost import NECost, generate_monte_carlo_samples

import seaborn as sns
import matplotlib.pyplot as plt
input_params_file_path = f"{src_path}/../test/eg23"
input_params_data = pd.read_csv(f"{input_params_file_path}.csv").set_index("var_name").transpose()

# monte_carlo_data_r3 = generate_monte_carlo_samples(
#     params_data=input_params_data,
#     sampling_amount=50_000,
#     discount_rate=3
# )

monte_carlo_data_r5 = generate_monte_carlo_samples(
    params_data=input_params_data,
    sampling_amount=1,
    discount_rate=5
)

# monte_carlo_data_r10 = generate_monte_carlo_samples(
#     params_data=input_params_data,
#     sampling_amount=50_000,
#     discount_rate=10
# )
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
# necost_r3 = NECost(data=monte_carlo_data_r3, **default_params)
necost_r5 = NECost(data=monte_carlo_data_r5, **default_params)
# necost_r10 = NECost(data=monte_carlo_data_r10, **default_params)

# result_r3 = necost_r3.run()
result_r5 = necost_r5.run()
# result_r10 = necost_r10.run()
print(result_r5)



# levelized_hydride_costs = pd.DataFrame({
#     "Discount Rate at 3%": result_r3["Levelized Hydride Cost"],
#     "Discount Rate at 5%": result_r5["Levelized Hydride Cost"],
#     "Discount Rate at 10%": result_r10["Levelized Hydride Cost"],
# })
# sns.set_theme()

# sns.set(font_scale=3,)
# fig, ax = plt.subplots(figsize=(15.32, 11.944))
# ax_sns = sns.kdeplot(data=levelized_hydride_costs, fill=True, ax=ax)

# ax_sns.set(title="PDF for Levelized Hydride Costs")
# plt.ylabel('Relative Probability')
# plt.xlabel('$mills/kWh')
# plt.show()