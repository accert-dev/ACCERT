import numpy as np
import pickle

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from src import sampler, sheet_info
import multiprocessing as mp
import time
from CostReduction_exploration_mode import calculate_final_result 
import csv

# cpu_count = os.cpu_count()


# meta data
n_samples =  1000000
num_cpus = 100
batch_size = 5000 # the number of samples that you store per time

filename = f"{n_samples}_samples_resultss.csv"
pickle_filename= f"{n_samples}_samples_resultss.pkl"


# Declaring Excel File Path
path_data_file = 'levers_info.xlsx'

# Declaring Subsheets within Excel File
subsheet_names_dict = {}
# subsheet_names_dict['n_Samples'] = 'n_Samples';  
subsheet_names_dict['Levers'] = 'Levers'; 

# Extracting Declared Sheets as a Dictionary
df_dict = sheet_info(path_data_file, subsheet_names_dict)


Lever_samples = sampler(n_samples, df_dict['Levers'])

# hard coding for the ITC amount
possible_values = [6, 30, 40, 50]

# Function to find the closest value
def find_closest(value, possible_values):
    return min(possible_values, key=lambda x: abs(x - value))

# Update the second row
Lever_samples[1] = [find_closest(value, possible_values) for value in Lever_samples[1]]








# A function for the average results (averaged over all the reactors built)

def calculate_final_result_avg_all(reactor_type, f_22, f_2321, land_cost_per_acre_0, RB_grade_0, BOP_grade_0,\
    num_orders, design_completion_0, ae_exp_0, N_AE, ce_exp_0, N_cons, mod_0, Design_Maturity_0, proc_exp_0,\
        N_proc, standardization_0, interest_rate_0,\
        startup_0, ITC_0, n_ITC, staggering_ratio):
    
 
    OCC_list = []
    TCI_list = [] 
    durations_list = []

    for n_th in range(1, num_orders+1):

        # the following results are: # The ITC_reduced OCC (levelized),The ITC_reduced TCI(levelized), cons duration 
        _, OCC_result, TCI_result, duration_result  = calculate_final_result(reactor_type, n_th, f_22, f_2321,\
            land_cost_per_acre_0, RB_grade_0, BOP_grade_0,\
        num_orders, design_completion_0, ae_exp_0, N_AE, ce_exp_0, N_cons,\
            mod_0, Design_Maturity_0, proc_exp_0, N_proc,\
            standardization_0, interest_rate_0, startup_0, ITC_0, n_ITC) 


        OCC_list.append(OCC_result)
        TCI_list.append(TCI_result )
        durations_list.append( duration_result  )
        
    # Convert lists to numpy arrays for efficient computation
    OCC_array = np.array(OCC_list)
    TCI_array = np.array(TCI_list)
    durations_array = np.array(durations_list)
    occLastUnit =  OCC_array[-1]
    TCILastUnit =  TCI_array[-1] 
    durationsLastUnit = durations_array[-1] 
    avg_OCC = np.mean(OCC_array )
    avg_TCI = np.mean(TCI_array)
    avg_duration = np.mean(durations_array)
                            
    # Calculate final startup duration
    final_startup_duration = max(7, startup_0 * (1 - 0.3) ** np.log2(num_orders))
    
    # Calculate cumulative construction duration with startup
    cons_duration_cumulative_wz_startup = (1 - staggering_ratio) * np.sum(durations_array[:-1]) + durations_array[-1] + final_startup_duration
    
    
    # note that all the OCC and TCI here are TCI-reduced
    return OCC_array, TCI_array, durations_array,\
        cons_duration_cumulative_wz_startup, occLastUnit, TCILastUnit,\
            durationsLastUnit, avg_OCC, avg_TCI, avg_duration             
              
              
# 6 parameters that are not sampled
reactor_type = "Concept A"
# factory building cost (associated with accounts 22 and 232.1)
f_22   = 250000000
f_2321 = 150000000
land_cost_per_acre_0 =  22000 # dollars/acre
startup_0 = 16
staggering_ratio = 0.75


def results_sampling(sample):
    vars_sampled = Lever_samples[:, sample]
  
    # Unpack only the necessary variables
    n_orders, itc_0, n_ITC, interest_r, design_comp, Design_Maturity_0, proc_exp_0, N_proc, ce_exp_0, N_cons, ae_exp_0, N_AE, standard, mod_0,\
        BOP_grade_0, RB_grade_0 = vars_sampled
    # Directly access values from arrays without intermediate variables
    num_orders = int(n_orders)
    ITC_0 = itc_0/100
    interest_rate_0 = interest_r/100
    design_completion_0 = design_comp/100
    standardization_0 = standard/100
    
    #modularity : "stick_built"  or "modularized"
    if mod_0 == 0:
        Mod_0 = "stick_built"
    elif mod_0 == 1:
        Mod_0 = "modularized"
        
    if RB_grade_0 == 0:  
        RB_Grade_0  = "nuclear"
    elif RB_grade_0 == 1:    
        RB_Grade_0  = "non_nuclear"
        
    if BOP_grade_0 == 0:  
        BOP_Grade_0  = "nuclear"
    elif BOP_grade_0 == 1:    
        BOP_Grade_0  = "non_nuclear"    
        
        
    # Call the function with the necessary parameters
    OCC_array, TCI_array, durations_array,\
        cons_duration_cumulative_wz_startup, occLastUnit, TCILastUnit,\
            durationsLastUnit, avg_OCC, avg_TCI, avg_duration  = \
        calculate_final_result_avg_all(reactor_type, f_22, f_2321, land_cost_per_acre_0, RB_Grade_0, BOP_Grade_0, num_orders, 
                                       design_completion_0, ae_exp_0, N_AE, ce_exp_0, N_cons, Mod_0, Design_Maturity_0, 
                                       proc_exp_0, N_proc, standardization_0, interest_rate_0, startup_0, ITC_0, n_ITC, 
                                       staggering_ratio)
    
    keys = [
        'Num_orders', 'ITC', 'n_ITC', 'interest rate', 'Design completion', 'Design_Maturity_0', 
        'supply chain exp_0', 'N supply chain', 'Const Proficiency', 'N const prof', 'AE', 
        'N AE prof', 'standardization', 'modularity', 'BOP commercial', 'RB Safety Related'
    ]
    
    results_data = {key: vars_sampled[i] for i, key in enumerate(keys)}
    
    
    # Update results_data with each element of the arrays
    for i, occ in enumerate(OCC_array):
        results_data[f'OCC_{i}'] = occ
        
    for i, tci in enumerate(TCI_array):
        results_data[f'TCI_{i}'] = tci
        
    for i, duration in enumerate(durations_array):
        results_data[f'duration_{i}'] = duration
      
    results_data['cons_duration_cumulative_wz_startup'] = cons_duration_cumulative_wz_startup
    results_data['occLastUnit'] = occLastUnit
    results_data['TCILastUnit'] = TCILastUnit
    results_data['durationsLastUnit'] = durationsLastUnit
    results_data['avg_OCC'] = avg_OCC
    results_data['avg_TCI'] = avg_TCI
    results_data['avg_duration'] = avg_duration
    
    return results_data



# # File to store results

# start_time = time.time()
# results = []
# all_keys = set()

# with mp.Pool(num_cpus) as pool:
#     for start in range(0, n_samples, batch_size):
#         end = min(start + batch_size, n_samples)
#         batch_results = pool.map(results_sampling, range(start, end))
        
#         # Accumulate results and collect all keys
#         for result in batch_results:
#             results.append(result)
#             all_keys.update(result.keys())
        
#         print(f"{end} samples", flush=True)
#         print(f"{(time.time() - start_time)/end} sec/sample", flush=True)

# # Static keys in the desired order
# static_keys = [
#     'Num_orders', 'ITC', 'n_ITC', 'interest rate', 'Design completion', 'Design_Maturity_0',
#     'supply chain exp_0', 'N supply chain', 'Const Proficiency', 'N const prof', 'AE',
#     'N AE prof', 'standardization', 'modularity', 'BOP commercial', 'RB Safety Related'
# ]

# # print(all_keys)
# # Extract and sort dynamic keys
# occ_keys = sorted([key for key in all_keys if key.startswith('OCC_')], key=lambda x: int(x.split('_')[1]))
# tci_keys = sorted([key for key in all_keys if key.startswith('TCI_')], key=lambda x: int(x.split('_')[1]))
# duration_keys = sorted([key for key in all_keys if key.startswith('duration_')], key=lambda x: int(x.split('_')[1]))

# # Combine all keys in the desired order
# headers = static_keys + occ_keys + tci_keys + duration_keys +\
#     ['cons_duration_cumulative_wz_startup'] + ['occLastUnit']+\
#         ['TCILastUnit'] + ['durationsLastUnit'] +['avg_OCC'] + ['avg_TCI'] + ['avg_duration']
    
    
# # Save results to a CSV file
# with open(filename, mode='w', newline='') as file:
#     writer = csv.DictWriter(file, fieldnames=headers)
#     writer.writeheader()
    
#     for result in results:
#         # Ensure all dictionaries have the same keys by filling missing keys with None
#         full_result = {key: result.get(key, None) for key in headers}
#         writer.writerow(full_result)

# print(f"Results saved to {filename}")

# # Save results to a pickle file
# with open(pickle_filename, 'wb') as file:
#     pickle.dump(results, file)

# print(f"Results saved to {pickle_filename}")




# Static keys in the desired order
static_keys = [
    'Num_orders', 'ITC', 'n_ITC', 'interest rate', 'Design completion', 'Design_Maturity_0',
    'supply chain exp_0', 'N supply chain', 'Const Proficiency', 'N const prof', 'AE',
    'N AE prof', 'standardization', 'modularity', 'BOP commercial', 'RB Safety Related'
]

# File to store results
start_time = time.time()
results = []
all_keys = set()

with mp.Pool(num_cpus) as pool, open(filename, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=static_keys)
    # writer.writeheader()

    for start in range(0, n_samples, batch_size):
        end = min(start + batch_size, n_samples)
        batch_results = pool.map(results_sampling, range(start, end))

        # Accumulate results and collect all keys
        for result in batch_results:
            results.append(result)
            all_keys.update(result.keys())

        # Extract and sort dynamic keys (only once, after the first batch)
        if start == 0:
            occ_keys = sorted([key for key in all_keys if key.startswith('OCC_')], key=lambda x: int(x.split('_')[1]))
            tci_keys = sorted([key for key in all_keys if key.startswith('TCI_')], key=lambda x: int(x.split('_')[1]))
            duration_keys = sorted([key for key in all_keys if key.startswith('duration_')], key=lambda x: int(x.split('_')[1]))

            # Combine all keys in the desired order
            headers = static_keys + occ_keys + tci_keys + duration_keys +\
                ['cons_duration_cumulative_wz_startup'] + ['occLastUnit']+\
                ['TCILastUnit'] + ['durationsLastUnit'] +['avg_OCC'] + ['avg_TCI'] + ['avg_duration']
            
            # Update the CSV header
            writer.fieldnames = headers
            writer.writeheader()

        for result in batch_results:
            # Ensure all dictionaries have the same keys by filling missing keys with None
            full_result = {key: result.get(key, None) for key in headers}
            writer.writerow(full_result)

        print(f"{end} samples", flush=True)
        print(f"{(time.time() - start_time)/end} sec/sample", flush=True)

print(f"Results saved to {filename}")

# Save results to a pickle file (optional)
with open(pickle_filename, 'wb') as file:
    pickle.dump(results, file)

print(f"Results saved to {pickle_filename}")




 
