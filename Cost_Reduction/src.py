# Importing libararies
import pandas as pd
import numpy as np


import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# A function to prettify the output (make the results table look nice)

def prettify(database1, caption, category):
    database1['Total Cost (USD)'] = database1['Total Cost (USD)'].apply(lambda x: '$ {:,.0f}'.format(x))
    database1['Factory Equipment Cost'] = database1['Factory Equipment Cost'].apply(lambda x: '$ {:,.0f}'.format(x))
    database1['Site Labor Cost'] = database1['Site Labor Cost'].apply(lambda x: '$ {:,.0f}'.format(x))
    database1['Site Material Cost'] = database1['Site Material Cost'].apply(lambda x: '$ {:,.0f}'.format(x))
    database1['Site Labor Hours'] =database1['Site Labor Hours'].apply(lambda x: '{:,.0f} hrs'.format(x))
    
    database1 = database1.fillna('') # remove nan
    database1= database1.replace({'$ nan':'', 'nan hrs':''}) # remove nan


    df_ = database1.loc[database1.Account.isin([10, 20, 30, 40, 50, 60])] # highlight high level accounts

    df_2 = database1.iloc[-15:] 
    
    df3 = pd.concat([df_, df_2])
    df4 =  database1.iloc[-5:]
    slice_ = pd.IndexSlice[df3.index, df3.columns]
    slice_2 = pd.IndexSlice[df4.index, df4.columns]

 
    if category == "no_subsidies":
        database_styled = (database1.style.set_properties(**{'font-weight': 'bold'}, subset=slice_).\
                           set_properties(**{'color': 'white','background-color': 'white' }, subset=slice_2).\
                           set_caption(caption).set_table_styles([{'selector': 'caption','props': [('color', 'red'),('font-size', '20px')]}]))
            
    elif category == "subsidies":
        database_styled = (database1.style.set_properties(**{'font-weight': 'bold'}, subset=slice_).set_caption(caption).\
                           set_table_styles([{'selector': 'caption','props': [('color', 'red'),('font-size', '20px')]}]))
    
    return database_styled.hide()



# A function to update the high level costs in the database when changing the low level costs

def update_high_level_costs(db, reactor_power):


    # update account 21 : material, labor, factory
    db.loc[db.Account == 21, 'Factory Equipment Cost'] = (db.loc[db.Account == 212, 'Factory Equipment Cost']).values+\
    (db.loc[db.Account == 213, 'Factory Equipment Cost']).values +(db.loc[db.Account == '211 plus 214 to 219', 'Factory Equipment Cost']).values
   
    db.loc[db.Account == 21, 'Site Material Cost'] = (db.loc[db.Account == 212, 'Site Material Cost'].values)+\
    (db.loc[db.Account == 213, 'Site Material Cost']).values+(db.loc[db.Account == '211 plus 214 to 219', 'Site Material Cost']).values
    
    db.loc[db.Account == 21, 'Site Labor Cost'] = (db.loc[db.Account == 212, 'Site Labor Cost']).values+\
    (db.loc[db.Account == 213, 'Site Labor Cost']).values+(db.loc[db.Account == '211 plus 214 to 219', 'Site Labor Cost']).values
    
    db.loc[db.Account == 21, 'Site Labor Hours'] = (db.loc[db.Account == 212, 'Site Labor Hours']).values+\
    (db.loc[db.Account == 213, 'Site Labor Hours']).values+(db.loc[db.Account =='211 plus 214 to 219', 'Site Labor Hours']).values


    #     # update account 23 : material, labor, factory
    db.loc[db.Account == 23, 'Factory Equipment Cost'] = (db.loc[db.Account == '232.1', 'Factory Equipment Cost']).values+\
    (db.loc[db.Account == 233, 'Factory Equipment Cost']).values
    
    (db.loc[db['Account'] == 23, 'Site Material Cost']) = (db.loc[db['Account'] == '232.1', 'Site Material Cost']).values+\
    (db.loc[db['Account'] == 233, 'Site Material Cost']).values
    
    (db.loc[db['Account'] == 23, 'Site Labor Cost']) = (db.loc[db['Account'] == '232.1', 'Site Labor Cost']).values+\
    (db.loc[db['Account'] == 233, 'Site Labor Cost']).values
    
    (db.loc[db['Account'] == 23, 'Site Labor Hours']) = (db.loc[db['Account'] == '232.1', 'Site Labor Hours']).values+\
    (db.loc[db['Account'] == 233, 'Site Labor Hours']).values




    
    # update total costs for accounts 21 : 26
    
    # total = labor + factory + material
    for x in [21, 212, 213, '211 plus 214 to 219', 22, 23, '232.1', 233, 24, 26]: 
        (db.loc[db['Account'] == x, 'Total Cost (USD)']) = (db.loc[db['Account'] == x, 'Factory Equipment Cost'])+\
            (db.loc[db['Account'] == x, 'Site Labor Cost'])+ (db.loc[db['Account'] == x, 'Site Material Cost'])

    #update total costs for accounts 10
    (db.loc[db['Title'] == '10s - Subtotal', 'Total Cost (USD)']) =\
        db.loc[db['Account'].isin([11, 12, 13, 14, 15, 16, 18]), 'Total Cost (USD)'].sum()
     
    # update total costs for accounts 20
    (db.loc[db['Title'] == '20s - Subtotal', 'Total Cost (USD)']) =\
        db.loc[db['Account'].isin([21, 22, 23, 24, 25, 26, 28]), 'Total Cost (USD)'].sum()

    # update total costs for accounts 30
    (db.loc[db['Title'] == '30s - Subtotal', 'Total Cost (USD)']) =\
        db.loc[db['Account'].isin([31, 32, 33, 34, 35]), 'Total Cost (USD)'].sum()


    # update total costs for accounts 50
    (db.loc[db['Title'] == '50s - Subtotal', 'Total Cost (USD)']) =\
        db.loc[db['Account'].isin([51, 52, 54]), 'Total Cost (USD)'].sum()

    # update total costs for accounts 60
    (db.loc[db['Title'] == '60s - Subtotal', 'Total Cost (USD)']) =\
        db.loc[db['Account'].isin([ 62]), 'Total Cost (USD)'].sum()
    
    # uodate costs per kw
    
    
    (db.loc[db['Title'] == '10s - $/kWe', 'Total Cost (USD)']) = (db.loc[db['Title'] == '10s - Subtotal', 'Total Cost (USD)']).values/reactor_power 
    (db.loc[db['Title'] == '20s - $/kWe', 'Total Cost (USD)']) = (db.loc[db['Title'] == '20s - Subtotal', 'Total Cost (USD)']).values/reactor_power 
    (db.loc[db['Title'] == '30s - $/kWe', 'Total Cost (USD)']) = (db.loc[db['Title'] == '30s - Subtotal', 'Total Cost (USD)']).values/reactor_power 
    (db.loc[db['Title'] == '40s - $/kWe', 'Total Cost (USD)']) = (db.loc[db['Title'] == '40s - Subtotal', 'Total Cost (USD)']).values/reactor_power 
    (db.loc[db['Title'] == '50s - $/kWe', 'Total Cost (USD)']) = (db.loc[db['Title'] == '50s - Subtotal', 'Total Cost (USD)']).values/reactor_power 
    (db.loc[db['Title'] == '60s - $/kWe', 'Total Cost (USD)']) = (db.loc[db['Title'] == '60s - Subtotal', 'Total Cost (USD)']).values/reactor_power 
    
    
    
    # update final results
    (db.loc[db['Title'] == 'Total Direct Capital Cost (Accounts 10 to 20)', 'Total Cost (USD)']) =\
        (db.loc[db['Title'] == '10s - Subtotal', 'Total Cost (USD)']).values + (db.loc[db['Title'] == '20s - Subtotal', 'Total Cost (USD)']).values
    
    (db.loc[db['Title'] == 'Base Construction Cost (Accounts 10 to 30)', 'Total Cost (USD)']) =\
       (db.loc[db['Title'] == 'Total Direct Capital Cost (Accounts 10 to 20)', 'Total Cost (USD)']).values +\
        (db.loc[db['Title'] == '30s - Subtotal', 'Total Cost (USD)']).values

    (db.loc[db['Title'] == 'Total Overnight Cost (Accounts 10 to 50)', 'Total Cost (USD)']) =\
        (db.loc[db['Title'] == 'Base Construction Cost (Accounts 10 to 30)', 'Total Cost (USD)']).values +\
    (db.loc[db['Title'] == '50s - Subtotal', 'Total Cost (USD)']).values

    (db.loc[db['Title'] == 'Total Capital Investment Cost (All Accounts)', 'Total Cost (USD)']) =\
       (db.loc[db['Title'] == 'Total Overnight Cost (Accounts 10 to 50)', 'Total Cost (USD)']).values +\
        (db.loc[db['Title'] == '60s - Subtotal', 'Total Cost (USD)']).values

   
    # update final results per kw
    (db.loc[db['Title'] == '(Accounts 10 to 20) US$/kWe', 'Total Cost (USD)']) =\
        (db.loc[db['Title'] == 'Total Direct Capital Cost (Accounts 10 to 20)', 'Total Cost (USD)']).values/reactor_power 

    (db.loc[db['Title'] == '(Accounts 10 to 30) US$/kWe', 'Total Cost (USD)']) =\
        (db.loc[db['Title'] == 'Base Construction Cost (Accounts 10 to 30)', 'Total Cost (USD)']).values/reactor_power 
   
    (db.loc[db['Title'] == '(Accounts 10 to 50) US$/kWe', 'Total Cost (USD)']) =\
        (db.loc[db['Title'] == 'Total Overnight Cost (Accounts 10 to 50)', 'Total Cost (USD)']).values/reactor_power 
    
    (db.loc[db['Title'] == '(Accounts 10 to 60) US$/kWe', 'Total Cost (USD)']) =\
        (db.loc[db['Title'] == 'Total Capital Investment Cost (All Accounts)', 'Total Cost (USD)']).values/reactor_power
    	
    return db


# A function to calculate the cost reduction factor due to the ITC subsidies
def ITC_reduction_factor(itc_level):
    itc_values = [0, 0.06, 0.3, 0.4, 0.5]
    ITC_reduction_factor = [1, 0.95,	0.73,	0.63,	0.53 ]
    return np.interp(itc_level, itc_values, ITC_reduction_factor)




# A function to update the construction duration when the labor hours change
def update_cons_duration(db0, db1, ref_duration):
    # sum old hours
    #sum of labor hours for Account 20 in the initial estimation (well exectued scenario)
    sum_old_lab_hrs = (db0.loc[db0.Account == 21, 'Site Labor Hours']).values +\
    (db0.loc[db0.Account == 22, 'Site Labor Hours']).values +\
    (db0.loc[db0.Account == 23, 'Site Labor Hours']).values+\
    (db0.loc[db0.Account == 24, 'Site Labor Hours']).values+\
    (db0.loc[db0.Account == 26, 'Site Labor Hours']).values
    
    
    sum_new_lab_hrs = (db1.loc[db1.Account == 21, 'Site Labor Hours']).values +\
    (db1.loc[db1.Account == 22, 'Site Labor Hours']).values +\
    (db1.loc[db1.Account == 23, 'Site Labor Hours']).values+\
    (db1.loc[db1.Account == 24, 'Site Labor Hours']).values+\
    (db1.loc[db1.Account == 26, 'Site Labor Hours']).values
    
    lab_hrs_delta = (sum_new_lab_hrs - sum_old_lab_hrs) / sum_old_lab_hrs
    new_duration = 0.3 * lab_hrs_delta* ref_duration + ref_duration
    return new_duration


def sum_lab_hrs(db0):
    # sum old hours
    #sum of labor hours for Account 20 in the initial estimation (well exectued scenario)
    sum_lab_hrs = (db0.loc[db0.Account == 21, 'Site Labor Hours']).values +\
    (db0.loc[db0.Account == 22, 'Site Labor Hours']).values +\
    (db0.loc[db0.Account == 23, 'Site Labor Hours']).values+\
    (db0.loc[db0.Account == 24, 'Site Labor Hours']).values+\
    (db0.loc[db0.Account == 26, 'Site Labor Hours']).values
    
    
    return sum_lab_hrs

def update_cons_duration_2(db0, db1, ref_duration, prev_cons_duration, baseline_lab_hours):
    
    # sum old hours
    #sum of labor hours for Account 20 in the initial estimation (well exectued scenario)
    sum_old_lab_hrs = (db0.loc[db0.Account == 21, 'Site Labor Hours']).values +\
    (db0.loc[db0.Account == 22, 'Site Labor Hours']).values +\
    (db0.loc[db0.Account == 23, 'Site Labor Hours']).values+\
    (db0.loc[db0.Account == 24, 'Site Labor Hours']).values+\
    (db0.loc[db0.Account == 26, 'Site Labor Hours']).values
    
    sum_new_lab_hrs = (db1.loc[db1.Account == 21, 'Site Labor Hours']).values +\
    (db1.loc[db1.Account == 22, 'Site Labor Hours']).values +\
    (db1.loc[db1.Account == 23, 'Site Labor Hours']).values+\
    (db1.loc[db1.Account == 24, 'Site Labor Hours']).values+\
    (db1.loc[db1.Account == 26, 'Site Labor Hours']).values
    
    lab_hrs_delta = (sum_new_lab_hrs -sum_old_lab_hrs ) / baseline_lab_hours
    
    return 0.3*lab_hrs_delta *ref_duration + prev_cons_duration
    