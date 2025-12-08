#!/usr/bin/env python

# This notebook demonstrates the impact of various levers on the cost of a nuclear power plant.
# 
# It begins with a baseline cost sheet, followed by an estimation of how each lever affects the overall cost. Levers that may influence the cost include design completion, modularity, interest rates,.etc
# 
# This notebook is useful for exploring how these levers contribute to cost overruns or savings, step by step. Users who are only interested in the final result can utilize the last section, which includes a Python function that calculates the impact of all the levers in a single step.
# 
# For a detailed understanding of the details behind this framework, please check [this report](https://www.osti.gov/biblio/2361138)

# ###  Importing the libraries

# In[1]:


import pandas as pd
import numpy as np
from src import prettify, update_high_level_costs, ITC_reduction_factor, update_cons_duration, sum_lab_hrs, update_cons_duration_2

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

pd.set_option('display.max_rows', None)


# ## Section 1 : Reading the Baseline reactor Cost Summary Table 


# A function to read the inital reactor data from excel

def reactor_data_read(reactor_type):
    
    if reactor_type == "Concept A":
        # Reading excel or csv files
        Reactor_data_0 = pd.read_excel('Inputs.xlsx', sheet_name = "Concept_A", nrows= 69)
        reactor_power = 1056 * 1000 # kw
        
        
    elif reactor_type == "Concept B":
        # Reading excel or csv files
        Reactor_data_0 = pd.read_excel('Inputs.xlsx', sheet_name = "Concept_B", nrows= 69)
        reactor_power = 310.8 * 1000 # kw    
        
    db = pd.DataFrame()
    db = Reactor_data_0[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()
    Reactor_data = db
    return Reactor_data, reactor_power



# ### The Cost reduction framework: levers and variables impact the costs as shown in the figure (below)


# ## Section - 3 : Updating the Cost Summary based on user inputs

# ### Section - 3-0 : Adding the factory cost to accounts 22 and 232.1


def add_factory_cost(Reactor_data_0, power, f_22, f_2321, num_orders):
    db = pd.DataFrame()
    db = Reactor_data_0[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    db.loc[db.Account == 22, 'Factory Equipment Cost'] = None # clear old values
    db.loc[db.Account == '232.1', 'Factory Equipment Cost'] = None # clear old values

  
    db.loc[db.Account == 22, 'Factory Equipment Cost'] = ((Reactor_data_0.loc[Reactor_data_0.Account == 22, 'Factory Equipment Cost']) + f_22/num_orders )
    db.loc[db.Account == '232.1', 'Factory Equipment Cost'] = ((Reactor_data_0.loc[Reactor_data_0.Account == '232.1', 'Factory Equipment Cost']) + f_2321/num_orders)


    Reactor_data_fac = update_high_level_costs(db, power)
    ref_tot_lab_hrs = sum_lab_hrs (Reactor_data_fac)

    Reactor_data_fac_ = pd.DataFrame()
    Reactor_data_fac_ = Reactor_data_fac[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()
    
    
    return Reactor_data_fac_  , ref_tot_lab_hrs

# ### Section 3-1 : The land cost & Taxes

# In[5]:


# The cost of the land is 22000$ per acre (500 acres
# The cost is multiplied by the new $/acre divided by the old one
# Accounts 11 and 12 are changed

def add_land_cost(Reactor_data_fac, land_cost_per_acre, power):

    db = pd.DataFrame()
    db = Reactor_data_fac[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

   
    db.loc[db.Account == 11, 'Total Cost (USD)'] = None # clear old values
    db.loc[db.Account == 12, 'Total Cost (USD)'] = None # clear old values
    db.loc[db.Account == 51, 'Total Cost (USD)'] = None # clear old values
    

    db.loc[db.Account == 11, 'Total Cost (USD)'] = (land_cost_per_acre /22000)*(Reactor_data_fac.loc[Reactor_data_fac.Account == 11, 'Total Cost (USD)'].values)
    db.loc[db.Account == 12, 'Total Cost (USD)'] = (land_cost_per_acre /22000)*(Reactor_data_fac.loc[Reactor_data_fac.Account == 12, 'Total Cost (USD)'].values)


    # The taxes scale with increasing the land cost 
    db.loc[db.Account == 51, 'Total Cost (USD)'] = (land_cost_per_acre /22000)*(Reactor_data_fac.loc[Reactor_data_fac.Account == 51, 'Total Cost (USD)'].values)

    db.loc[db.Account == 51, 'Total Cost (USD)']
    Reactor_data_updated_1 = update_high_level_costs(db, power)


    Reactor_data_updated_1_ = pd.DataFrame()
    Reactor_data_updated_1_ = Reactor_data_updated_1[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    return Reactor_data_updated_1_
 

# ### Section 3-2 : Whether the Reactor Building and BOP are nuclear grade equipment

# if the BOP is non-nuclear, the cost reduction factor for account 213 is 0.6
# Also, the cost reduction factor for account 232.1 is 0.6 (for factory and labor but not material)

# If the reactor building is non nuclear, the cost reduction factor for acount 212 is 0.6

def add_BOP_RP_grades(Reactor_data_updated_1, RB_grade_0, BOP_grade_0, power, reactor_type, n_th, mod_0):
    
    RB_grade = RB_grade_0     # Does not change when building more units. it is either always nuclear or always non nuclear
    
    
    # If n >=2: BoP commercial = True : non_nuclear
    if n_th == 1:
        BOP_grade = BOP_grade_0
    elif n_th >=2:
        BOP_grade = "non_nuclear"
             
    
    db = pd.DataFrame()

    db = Reactor_data_updated_1[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    db.loc[db.Account == 212, 'Site Material Cost'] = None # clear old values
    db.loc[db.Account == 212, 'Site Labor Cost'] = None # clear old values
    db.loc[db.Account ==  212, 'Site Labor Hours'] = None
    db.loc[db.Account ==  212, 'Factory Equipment Cost'] = None

    db.loc[db.Account ==  213, 'Site Material Cost'] = None
    db.loc[db.Account ==  213, 'Site Labor Cost']  = None
    db.loc[db.Account ==  213, 'Site Labor Hours'] = None
    db.loc[db.Account ==  213, 'Factory Equipment Cost'] = None

    db.loc[db.Account ==  '232.1', 'Factory Equipment Cost'] = None
    db.loc[db.Account ==  '232.1', 'Site Labor Cost'] = None
    db.loc[db.Account ==  '232.1', 'Site Labor Hours'] = None


    if RB_grade == "non_nuclear":
        db.loc[db.Account == 212, 'Site Material Cost'] = 0.6*((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 212, 'Site Material Cost']).values)
        db.loc[db.Account == 212, 'Site Labor Cost'] = 0.6*((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 212, 'Site Labor Cost']).values)
        db.loc[db.Account == 212,'Site Labor Hours'] = 0.6*((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 212, 'Site Labor Hours']).values)
        db.loc[db.Account == 212,'Factory Equipment Cost'] = 0.6*((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 212, 'Factory Equipment Cost']).values)

    else:
        db.loc[db.Account == 212, 'Site Material Cost'] = ((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 212, 'Site Material Cost']).values)
        db.loc[db.Account == 212, 'Site Labor Cost'] = ((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 212, 'Site Labor Cost']).values)
        db.loc[db.Account == 212,'Site Labor Hours'] = ((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 212, 'Site Labor Hours']).values)
        db.loc[db.Account == 212,'Factory Equipment Cost'] = ((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 212, 'Factory Equipment Cost']).values)

    
    if BOP_grade == "non_nuclear":
        db.loc[db.Account == 213, 'Site Material Cost'] = 0.6*((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 213, 'Site Material Cost']).values)
        db.loc[db.Account == 213, 'Site Labor Cost'] = 0.6*((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 213, 'Site Labor Cost']).values)
        db.loc[db.Account == 213, 'Site Labor Hours'] = 0.6*((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 213, 'Site Labor Hours']).values)
        db.loc[db.Account == 213, 'Factory Equipment Cost'] = 0.6*((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 213, 'Factory Equipment Cost']).values)

        db.loc[db.Account == '232.1', 'Factory Equipment Cost'] = 0.6*((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == '232.1', 'Factory Equipment Cost']).values)
        db.loc[db.Account == '232.1', 'Site Labor Hours'] = 0.6*((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == '232.1', 'Site Labor Hours']).values)
        db.loc[db.Account == '232.1', 'Site Labor Cost'] = 0.6*((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == '232.1', 'Site Labor Cost']).values)


    else:
        db.loc[db.Account == 213, 'Site Material Cost'] = ((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 213, 'Site Material Cost']).values)
        db.loc[db.Account == 213, 'Site Labor Cost'] = ((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 213, 'Site Labor Cost']).values)
        db.loc[db.Account == 213, 'Site Labor Hours'] = ((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 213, 'Site Labor Hours']).values)
        db.loc[db.Account == 213, 'Factory Equipment Cost'] = ((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 213, 'Factory Equipment Cost']).values)

        db.loc[db.Account == '232.1', 'Factory Equipment Cost'] = ((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == '232.1', 'Factory Equipment Cost']).values)
        db.loc[db.Account == '232.1', 'Site Labor Hours'] = ((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == '232.1', 'Site Labor Hours']).values)
        db.loc[db.Account == '232.1', 'Site Labor Cost'] = ((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == '232.1', 'Site Labor Cost']).values)


    Reactor_data_updated_2 = update_high_level_costs(db, power)

    Reactor_data_updated_2_ = pd.DataFrame()
    Reactor_data_updated_2_ = Reactor_data_updated_2[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()
    

     
    if reactor_type == "Concept A":
        duration = 125
    elif reactor_type == "Concept B": 
        duration = 80
          
    new_dur = update_cons_duration(Reactor_data_updated_1, Reactor_data_updated_2,  duration)
   
     #apply modularity factor affecting the construction duration 
    if n_th == 1:
        mod = mod_0
    elif n_th >= 2:
        mod =  "modularized"
   
     
    if mod == "modularized" :
        mod_factor = 0.8
    else:   
        mod_factor = 1
    
    new_dur_1 = new_dur * mod_factor 
    return Reactor_data_updated_2_ , new_dur_1


# ### Section 3-3 : Bulk Ordering


#The factory equipment cost of  accounts 22 and 232.1 has to be divided by the number of orders
# The factory equipment cost of account 22 is multiplied by a reuction factor
# The factory equipment cost of account 232.1 is multiplied by a reduction factor


def add_bulk_ordering(Reactor_data_updated_3, num_orders, f_22, f_2321, power):
    db = pd.DataFrame()

    db = Reactor_data_updated_3[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    # esimtated learning rates
    lr22   = 0.1802341659291420
    lr2321 = 0.2607462372040820

    # These reduction factor are calculated as follows
    reduction_factor_22 = 0 # initialization
    reduction_factor_2321 = 0

    for ith_unit in  range(1,num_orders+1):
        reduction_factor_22+=((1 - lr22)**np.log2(ith_unit))/num_orders # for account 22
        reduction_factor_2321+=((1 - lr2321)**np.log2(ith_unit))/num_orders # for account 232.1


        
    for x in [ 22, '232.1']:  
        db.loc[db.Account == x, 'Factory Equipment Cost'] = None # clear old values


    # note that the cost reduction factor impacts the cost of the component not the cost of the factory
    db.loc[db.Account == 22, 'Factory Equipment Cost']       = reduction_factor_22   *  (    ( Reactor_data_updated_3.loc[ Reactor_data_updated_3.Account == 22, 'Factory Equipment Cost']   ) - ( f_22/num_orders) ) + (f_22/num_orders) 
    db.loc[db.Account == '232.1', 'Factory Equipment Cost']  = reduction_factor_2321 *   (  ( Reactor_data_updated_3.loc[ Reactor_data_updated_3.Account == '232.1', 'Factory Equipment Cost']) - ( f_2321/num_orders)) +(f_2321/num_orders) 

    

    Reactor_data_updated_4 = update_high_level_costs(db, power)
    Reactor_data_updated_4_ = pd.DataFrame()
    Reactor_data_updated_4_ = Reactor_data_updated_4[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()
    
    return Reactor_data_updated_4_ 



# ### Section 3-4 : Reworking and labor productivity


def add_reworking_productivity(Reactor_data_updated_4, reactor_type, n_th, design_completion_0, ae_exp_0, N_AE, ce_exp_0, N_cons, power, prev_cons_duration, baseline_lab_hours):
    #Reworking = f(AE, CE, design completion)
    
    if n_th == 1:
        design_completion = design_completion_0
        ae_exp = ae_exp_0
        ce_exp = ce_exp_0
        
    elif n_th > 1:
        design_completion = 1   
        ae_exp = min( (ae_exp_0 + (2/N_AE)*(n_th-1) ), 2)
        ce_exp = min( (ce_exp_0 + (2/N_cons)*(n_th-1) ), 2)
    
    # # labor productivity factor = f(construction experience level)
    productivity = 0.145*ce_exp + 0.71        
            

    if reactor_type == "Concept B":
        reworking_factor =  (-0.9*design_completion+ 1.9) * (-0.15*ae_exp+1.3) * (-0.15*ce_exp+1.3) 

    elif reactor_type == "Concept A":
        reworking_factor =  (-0.69*design_completion+ 1.69) * (-0.125*ae_exp+1.25) * (-0.125*ce_exp+1.25) 

    db = pd.DataFrame()

    db = Reactor_data_updated_4[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    for x in [212, 213, '211 plus 214 to 219',22, '232.1', 233, 24, 26]:  
        db.loc[db.Account == x, 'Factory Equipment Cost'] = None # clear old values
        db.loc[db.Account == x, 'Site Labor Hours'] = None
        db.loc[db.Account == x, 'Site Labor Cost'] = None
        db.loc[db.Account == x, 'Site Material Cost'] = None

    for x in [212, 213, '211 plus 214 to 219',22, '232.1', 233, 24, 26]: 
        db.loc[db.Account == x, 'Factory Equipment Cost'] =\
            ((( Reactor_data_updated_4.loc[ Reactor_data_updated_4.Account == x, 'Factory Equipment Cost']).values)[0])*reworking_factor  
        db.loc[db.Account == x, 'Site Labor Hours'] =\
            ((( Reactor_data_updated_4.loc[ Reactor_data_updated_4.Account == x, 'Site Labor Hours']).values)[0])*reworking_factor/productivity
        db.loc[db.Account == x, 'Site Labor Cost'] =\
            ((( Reactor_data_updated_4.loc[ Reactor_data_updated_4.Account == x, 'Site Labor Cost']).values)[0])*reworking_factor/productivity 
        db.loc[db.Account == x, 'Site Material Cost'] =\
            ((( Reactor_data_updated_4.loc[ Reactor_data_updated_4.Account == x, 'Site Material Cost']).values)[0])*reworking_factor 


    

    Reactor_data_updated_5 = update_high_level_costs(db, power)
    Reactor_data_updated_5_ = pd.DataFrame()
    Reactor_data_updated_5_ = Reactor_data_updated_5[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()
    
    # update the construction duration
    if reactor_type == "Concept A":
        reactor_type_ref_duration = 125
    elif reactor_type == "Concept B": 
        reactor_type_ref_duration = 80
        
    new_dur    = update_cons_duration_2(Reactor_data_updated_4, Reactor_data_updated_5_, reactor_type_ref_duration, prev_cons_duration, baseline_lab_hours)
    return Reactor_data_updated_5_  , new_dur
 



# #### Combine the previous functions in one function


# Combine the previous functions in one function

def update_direct_cost(reactor_type, n_th, f_22, f_2321, land_cost_per_acre_0, RB_grade_0, BOP_grade_0, 
                       num_orders, design_completion_0, ae_exp_0, N_AE, ce_exp_0, N_cons, mod_0):

    reactor_data, reactor_power = reactor_data_read(reactor_type)
    
    reactor_data_factory, baseline_lab_hours = add_factory_cost(
        reactor_data, reactor_power, f_22, f_2321, num_orders
    )
    
    reactor_data_factory = add_land_cost(
        reactor_data_factory, land_cost_per_acre_0, reactor_power
    )
    
    reactor_data_factory, prev_cons_duration = add_BOP_RP_grades(
        reactor_data_factory, RB_grade_0, BOP_grade_0, reactor_power, reactor_type, n_th, mod_0
    )
    
    reactor_data_factory = add_bulk_ordering(
        reactor_data_factory, num_orders, f_22, f_2321, reactor_power
    )
    
    reactor_data_factory, new_dur_2 = add_reworking_productivity(
        reactor_data_factory, reactor_type, n_th, design_completion_0, ae_exp_0, N_AE, ce_exp_0, 
        N_cons, reactor_power, prev_cons_duration, baseline_lab_hours
    )
    
    return reactor_data_factory, new_dur_2



# ### Section 3-5 Learning by doing effect on the cost


def learning_effect(Reactor_data_updated_5, n_th, standardization_0, power):

    if n_th  == 1:
        standardization = min(0.7, standardization_0)
    elif n_th >1:
        standardization = standardization_0    
        
    # # Creating the table for the learning rates
    # #These rates are from KS-TIMCAT results.
    # # The learning rates are multiplied by the standardization divded by 0.7 (since the standatization of PWRs was 0.7)
    fitted_LR = pd.DataFrame()

    fitted_LR.loc[:, 'Account'] = Reactor_data_updated_5.loc[:, 'Account']
    fitted_LR.loc[:, 'Title'] = Reactor_data_updated_5.loc[:, 'Title']
    fitted_LR = fitted_LR.loc[fitted_LR['Account'].isin([212, 213, '211 plus 214 to 219', 22, '232.1', 233, 24, 26])]

    fitted_LR['Mat LR'] = np.array([0.099588665391, 0.099588665391, 0.099588665391, 0.080817992281, 0.0000000, 0.099588665391,\
                                    0.099588665391,0.099588665391])*standardization/0.7

    fitted_LR['Lab LR'] =     np.array([0.180678729399, 0.180678729399, 0.180678729399,0.146555539499, 0.137148574884,\
                                        0.180678729399, 0.180678729399,0.180678729399])*standardization/0.7


    db = pd.DataFrame()

    db = Reactor_data_updated_5[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    for x in [212, 213, '211 plus 214 to 219', 22, '232.1', 233, 24, 26]:  
        db.loc[db.Account == x, 'Site Labor Hours'] = None
        db.loc[db.Account == x, 'Site Labor Cost'] = None
        db.loc[db.Account == x, 'Site Material Cost'] = None


    # # # # Bulk order reduction	
    for x in [212, 213, '211 plus 214 to 219', 22, '232.1', 233, 24, 26]:
        mat_cost_reduction_multiplier = (1 - (fitted_LR.loc[fitted_LR.Account == x, 'Mat LR'].values[0]))**np.log2(n_th)
        lab_cost_reduction_multiplier = (1 - (fitted_LR.loc[fitted_LR.Account == x, 'Lab LR'].values[0]))**np.log2(n_th)
        
        db.loc[db.Account == x, 'Site Material Cost'] =\
            (( Reactor_data_updated_5.loc[ Reactor_data_updated_5.Account == x, 'Site Material Cost']))* mat_cost_reduction_multiplier

        db.loc[db.Account == x, 'Site Labor Hours'] =\
            (( Reactor_data_updated_5.loc[ Reactor_data_updated_5.Account == x, 'Site Labor Hours']))* lab_cost_reduction_multiplier
    
        db.loc[db.Account == x, 'Site Labor Cost'] =\
            (( Reactor_data_updated_5.loc[ Reactor_data_updated_5.Account == x, 'Site Labor Cost']))* lab_cost_reduction_multiplier


    Reactor_data_updated_6 = update_high_level_costs(db, power)
    Reactor_data_updated_6_ = pd.DataFrame()
    Reactor_data_updated_6_ = Reactor_data_updated_6[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                 'Site Material Cost']].copy()
    
    return Reactor_data_updated_6_  



def act_cons_duration_plus_delay(reactor_type, n_th, Design_Maturity_0, proc_exp_0, N_proc, cons_duration_no_delay):
    
    if n_th == 1:
        Design_Maturity = Design_Maturity_0
        proc_exp = proc_exp_0
    
    elif n_th>1:
        Design_Maturity = 2
        proc_exp = min( (proc_exp_0 + (2/N_proc)*(n_th-1) ), 2)
             
    # For the accounts 21, 22, 23, 24, 25, 26, 
    # The delays are D_21,D_22,D_23,D_24,D_25,D_26 
    # The tasks lengths (in months) are B_21,B_22,B_23,B_24,B_25,B_26

    # task length ratio between SFR and HTGR is 100/65
    # We use this ratio to convert SFR to HTGT task lengths

    if reactor_type == "Concept B":
        task_length_multiplier = 1
        ref_construction_duration = 64
    elif reactor_type == "Concept A": 
        task_length_multiplier = 100/64
        ref_construction_duration = 100
        
    B_21 =  42.1 * task_length_multiplier # months 
    B_22 = 60.2 * task_length_multiplier
    B_23 = 14.8 * task_length_multiplier
    B_24 = 3.6* task_length_multiplier
    B_25 = 10.1* task_length_multiplier
    B_26 = 43.9* task_length_multiplier


    # The delays are 
    D_21 =  - 6 * Design_Maturity  - 3*proc_exp + 18
    D_22 =  - 6 * Design_Maturity  - 3*proc_exp + 18
    D_23 =   - 6 * Design_Maturity  - 3*proc_exp + 18
    D_24 =   - 6 * Design_Maturity  - 3*proc_exp + 18
    D_25 =   - 6 * Design_Maturity  - 3*proc_exp + 18
    D_26 =   - 6 * Design_Maturity  - 3*proc_exp + 18


    # The tasks completion times (in months) are T_21,T_22,T_23,T_24,T_25,T_26
    T_21 = B_21 + D_21 
    T_22 = 0.09*(B_21+D_21)  +B_22+D_22
    T_23 = 0.24*(B_21+D_21)  +B_23+D_23
    T_24 = 0.24*(B_21+D_21) + 0.34*(B_23+D_23)  +B_24+D_24
    T_25 = 0.18*(B_21+D_21)  +B_25+D_25
    T_26 = 0.21*(B_21+D_21)   +B_26+D_26
    T_end = max(T_21, T_22, T_23, T_24, T_25, T_26)


    supply_chain_delay = max( T_end - ref_construction_duration, 0)
    actual_construction_duration_plus_delay = cons_duration_no_delay + supply_chain_delay
    return actual_construction_duration_plus_delay


# ### Section 3-7 Learning by doing effect on the construction duration


def duration_learning_effect(n_th, standardization_0, actual_construction_duration_plus_delay):
    
    if n_th  == 1:
        standardization = min(0.7, standardization_0)
    elif n_th >1:
        standardization = standardization_0  
    # now the effect of learning on the consturction duration
    fitted_LR_duration = 0.103719051*standardization/0.7
    duration_multiplier = (1 -fitted_LR_duration)**np.log2(n_th)
    final_construction_duration = duration_multiplier *actual_construction_duration_plus_delay
    return final_construction_duration 

# ### Section 3-8 Calculate the Indirect Cost and the standardization impact

def update_indirect_cost(n_th, standardization_0, Reactor_data_updated_6, final_construction_duration, power ):
    
    if n_th  == 1:
        standardization = min(0.7, standardization_0)
    elif n_th >1:
        standardization = standardization_0     
    #   I use here the indirect cost correlations prepared by Jia

    # When the standardization is  100%, the engineering service accound (Acct 35) is zero, 
    # When the standardization is  70%, the engineering service accound (Acct 35) does not change
    # The account 35 multiplier is

    factor_35 = 10/3* ( 1 - standardization)


    db = pd.DataFrame()

    db = Reactor_data_updated_6[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    for x in [31, 32, 33, 34, 35]:  
        db.loc[db.Account == x, 'Total Cost (USD)'] = None # clear old values


    # # total direct mat cost, labor cost, labor hours
    sum_new_mat_cost  = 0 # initilization
    sum_new_lab_cost  = 0 # initilization
    sum_new_lab_hrs  = 0 # initilization

    for x in [21, 22, 23, 24, 26]:
        sum_new_mat_cost +=     (db.loc[db.Account == x, 'Site Material Cost']).values
        sum_new_lab_cost +=     (db.loc[db.Account == x, 'Site Labor Cost']).values
        sum_new_lab_hrs  +=     (db.loc[db.Account == x, 'Site Labor Hours']).values


    # The new indirect costs   
    db.loc[db.Account == 31, 'Total Cost (USD)'] =  (sum_new_mat_cost*0.785* sum_new_lab_hrs/final_construction_duration/160/1058)\
    + sum_new_lab_cost *0.36

    db.loc[db.Account == 32, 'Total Cost (USD)'] =  sum_new_lab_cost *0.36*3.661* final_construction_duration/72

    db.loc[db.Account == 33, 'Total Cost (USD)'] =  0.04207006 * (db.loc[db.Account == 32, 'Total Cost (USD)'].values[0] )

    db.loc[db.Account == 34, 'Total Cost (USD)'] =  0.00354234616938 * (db.loc[db.Account == 32, 'Total Cost (USD)'].values[0] )

    db.loc[db.Account == 35, 'Total Cost (USD)'] = (0.27017603 * (db.loc[db.Account == 32, 'Total Cost (USD)'].values[0] ))*factor_35 


    Reactor_data_updated_7 = update_high_level_costs(db, power)
    Reactor_data_updated_7_ = pd.DataFrame()
    Reactor_data_updated_7_ = Reactor_data_updated_7[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()
    
    return Reactor_data_updated_7_  





# #### Combine the previous functions in one function



def calculate_base_cost(reactor_type, n_th, f_22, f_2321, land_cost_per_acre_0, RB_grade_0, BOP_grade_0, num_orders, design_completion_0, ae_exp_0, N_AE, ce_exp_0, N_cons, Design_Maturity_0, proc_exp_0, N_proc, standardization_0, mod_0):
    reactor_power = (reactor_data_read(reactor_type ))[1]
    direct_cost_updated , act_con_duration = update_direct_cost(reactor_type, n_th, f_22, f_2321, land_cost_per_acre_0, RB_grade_0, BOP_grade_0, num_orders, design_completion_0, ae_exp_0, N_AE, ce_exp_0, N_cons, mod_0)

    cons_duration_plus_delay = act_cons_duration_plus_delay(reactor_type, n_th, Design_Maturity_0, proc_exp_0, N_proc, act_con_duration)
    final_con_duration = duration_learning_effect(n_th, standardization_0, cons_duration_plus_delay)
    direct_cost_updated_plus_learning = learning_effect(direct_cost_updated , n_th, standardization_0, reactor_power)

    direct_cost_updated_plus_learning_with_indirect_cost = update_indirect_cost(n_th, standardization_0, direct_cost_updated_plus_learning, final_con_duration, reactor_power  )
    return direct_cost_updated_plus_learning_with_indirect_cost, final_con_duration 


# ### Section 3-9 :  Insurance



def insurance_cost_update(Reactor_data_0, Reactor_data_updated_7, power):
    # insurance increases linearly when increaing the sum of the 20s and 30s account
    db = pd.DataFrame()

    db = Reactor_data_updated_7[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()
    db0 = Reactor_data_0
    db.loc[db.Account == 52, 'Total Cost (USD)'] = None # clear old values

    change_in_insuance_cost = (db.loc[db.Title =='20s - Subtotal', 'Total Cost (USD)'].values\
                            + db.loc[db.Title =='30s - Subtotal', 'Total Cost (USD)'].values)/ (db0.loc[db0.Title =='20s - Subtotal', 'Total Cost (USD)'].values\
                            + db0.loc[db0.Title =='30s - Subtotal', 'Total Cost (USD)'].values)

    db.loc[db.Account == 52, 'Total Cost (USD)'] =  (change_in_insuance_cost[0])* (Reactor_data_updated_7.loc[db.Account == 52, 'Total Cost (USD)'])

    Reactor_data_updated_8 = update_high_level_costs(db, power)

    Reactor_data_updated_8_ = pd.DataFrame()
    Reactor_data_updated_8_ = Reactor_data_updated_8[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()
    
    return Reactor_data_updated_8_  

# ### Section 3-10 :  Interest



def update_interest_cost(Reactor_data_updated_8, final_construction_duration, interest_rate, startup_0, n_th, power):
    # Read the ref spending curve
    sp = pd.read_excel('Inputs.xlsx', sheet_name = "Ref Spending Curve", nrows= 104, usecols='A : D')
    Months = sp['Month'].tolist()
    CDFs  = sp['CDF'].tolist()
    
    annual_periods = np.linspace(12, 12*int(final_construction_duration/12),int(final_construction_duration/12))
   
    if max(annual_periods) < int(final_construction_duration)-1:
        annual_periods_1= np.append( annual_periods, (final_construction_duration)-1)
    else:
        annual_periods_1 = annual_periods
    
    annual_cum_spend = []
    for period in annual_periods_1:
        new_period = 103*period/int(final_construction_duration)
        
        annual_cum_spend.append(np.interp(new_period, Months, CDFs))
    annual_spend1 = np.append(annual_cum_spend[0], np.diff(annual_cum_spend ))
    
    tot_overnight_cost =   (Reactor_data_updated_8.loc[Reactor_data_updated_8.Title == 'Total Overnight Cost (Accounts 10 to 50)' , 'Total Cost (USD)']).values[0]

    annual_loan_add =  annual_spend1 *tot_overnight_cost
    
    interest_exp = ((1+interest_rate)**((final_construction_duration -annual_periods_1)/12)) * annual_loan_add - annual_loan_add
    
    tot_int_exp_construction = sum(interest_exp )
    if n_th == 1:
        startup = startup_0
    elif n_th >1:
        startup = max( 7 , startup_0*(1-0.3)**np.log2(n_th))
    
    int_exp_startup = (tot_int_exp_construction + tot_overnight_cost)*((1+interest_rate)**(startup/12))-(tot_int_exp_construction + tot_overnight_cost)
    db = pd.DataFrame()

    db = Reactor_data_updated_8[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()
    db.loc[db.Account == 62, 'Total Cost (USD)'] = None # clear old values

    (db.loc[db.Account == 62, 'Total Cost (USD)']) = int_exp_startup +tot_int_exp_construction 


    Reactor_data_updated_9 = update_high_level_costs(db, power)

    Reactor_data_updated_9_ = pd.DataFrame()
    Reactor_data_updated_9_ = Reactor_data_updated_9[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()
    
    tot_cap_investment = Reactor_data_updated_9.loc[Reactor_data_updated_9.Title =='Total Capital Investment Cost (All Accounts)', 'Total Cost (USD)'].values
    
    return Reactor_data_updated_9_, tot_overnight_cost, tot_cap_investment


# ### Section 3 - 11 :  ITC Subsidies


def update_itc(Reactor_data_updated_9, tot_overnight_cost, tot_cap_investment, n_th, ITC_0, n_ITC, reactor_power):
    
    ITC = ITC_0 if n_th <= n_ITC else 0
    
    db1 = Reactor_data_updated_9[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 
                                  'Site Labor Cost', 'Site Material Cost']].copy()

    ITC_cost_reduction_factor = ITC_reduction_factor(ITC)
    ITC_reduced_OCC = tot_overnight_cost * ITC_cost_reduction_factor
    OCC_cost_reduction_due_to_TCI = tot_overnight_cost - ITC_reduced_OCC

    db1.loc[db1.Title == 'Total Overnight Cost - ITC reduced', 'Total Cost (USD)'] = ITC_reduced_OCC
    db1.loc[db1.Title == 'Total Overnight Cost -ITC reduced (US$/kWe)', 'Total Cost (USD)'] = ITC_reduced_OCC / reactor_power
    db1.loc[db1.Title == 'Total Capital Investment Cost - ITC reduced', 'Total Cost (USD)'] = tot_cap_investment - OCC_cost_reduction_due_to_TCI
    
    levelized_NCI = db1.loc[db1.Title == 'Total Capital Investment Cost - ITC reduced', 'Total Cost (USD)'].values[0] / reactor_power
    db1.loc[db1.Title == 'Total Capital Investment Cost - ITC reduced (US$/kWe)', 'Total Cost (USD)'] = levelized_NCI

    Reactor_data_updated_10 = update_high_level_costs(db1, reactor_power)
    Reactor_data_updated_10_ = Reactor_data_updated_10[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 
                                                        'Site Labor Hours', 'Site Labor Cost', 'Site Material Cost']].copy()
    
    return Reactor_data_updated_10_, ITC_reduced_OCC / reactor_power, levelized_NCI

# ## Section 4 :  The Final Result

# #### A Python function to combine all the previous ones


def calculate_final_result(reactor_type, n_th, f_22, f_2321, land_cost_per_acre_0, RB_grade_0, BOP_grade_0,
                           num_orders, design_completion_0, ae_exp_0, N_AE, ce_exp_0, N_cons, mod_0, 
                           Design_Maturity_0, proc_exp_0, N_proc, standardization_0, interest_rate_0, 
                           startup_0, ITC_0, n_ITC): 

    reactor_data, reactor_power = reactor_data_read(reactor_type)
    
    tot_base_cost, final_construction_duration = calculate_base_cost(
        reactor_type, n_th, f_22, f_2321, land_cost_per_acre_0, RB_grade_0, BOP_grade_0, num_orders, 
        design_completion_0, ae_exp_0, N_AE, ce_exp_0, N_cons, Design_Maturity_0, proc_exp_0, N_proc, 
        standardization_0, mod_0
    )
    
    tot_base_cost = insurance_cost_update(reactor_data, tot_base_cost, reactor_power)
    tot_base_cost, tot_overnight_cost, tot_cap_investment = update_interest_cost(
        tot_base_cost, final_construction_duration, interest_rate_0, startup_0, n_th, reactor_power
    )

    Final_Result_COA, levelized_net_OCC, levelized_NCI = update_itc(
        tot_base_cost, tot_overnight_cost, tot_cap_investment, n_th, ITC_0, n_ITC, reactor_power
    )

    return Final_Result_COA, levelized_net_OCC, levelized_NCI, final_construction_duration[0]






# # factory building cost (associated with accounts 22 and 232.1)
# f_22   = 250000000
# f_2321 = 150000000
# land_cost_per_acre_0 =  22000 # dollars/acre
# startup_0 = 16
# staggering_ratio = 0.75



# # reactor type: Concept A or Concept B
# reactor_type = "Concept A"

# # Which reactor unit: first of a kind : nth of a kind 
# n_th = 1

# # number of firm orders
# num_orders = 7

# # land cost
# # From the SA report: the cost $22,000 per acre. The land area is 500 acres including recommended buffer
# land_cost_per_acre_0 =  22000 # dollars/acre

# # start up duration (months) 
# startup_0 = 16 

# # interest rate :
# interest_rate_0 = 0.074

# # Design completion
# design_completion_0 =  0.463# 1 means 100%

# # Design maturity
# Design_Maturity_0 = 1

# # #procurement service experience (supply chain experience)
# proc_exp_0= 0.196 # 2 means procurement experts. This is ideal. 
   
# # #  architecture and engineeringexperience
# ae_exp_0 = 0.69
    
# # #  Construction service experience
# ce_exp_0 = 0.19


# # numb er of projects for full efficiency of procurement, A/E, Construction
# N_proc = 3
# N_AE  = 4
# N_cons =5

# # modularity : "stick_built"  or "modularized"
# mod_0 = "modularized" 

    

# # cross_site_standardization :
# standardization_0 = 69.6979/100 # 0.7 corresponds to 70% standardization for PWRs

# # # Determining if the BOP and reactor building (containtment) are non-nuclear or nuclear grade equipment (safety related)
# BOP_grade_0 = "non_nuclear"
# RB_grade_0 = "nuclear"

# # #investment tax credits subsidies
# ITC_0 = 0.3298

# #number of reactors claiming ITC
# n_ITC = 2

# aa = (calculate_final_result(reactor_type, n_th, f_22, f_2321, land_cost_per_acre_0, RB_grade_0, BOP_grade_0,
#                            num_orders, design_completion_0, ae_exp_0, N_AE, ce_exp_0, N_cons, mod_0, 
#                            Design_Maturity_0, proc_exp_0, N_proc, standardization_0, interest_rate_0, 
#                            startup_0, ITC_0, n_ITC))

# print(aa[3])