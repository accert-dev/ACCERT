# Importing libararies
import pandas as pd
import numpy as np
import seaborn as sn
pd.set_option('mode.chained_assignment', None)
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', None)



def prettify(database1, caption, category):
    database1['Total Cost (USD)'] = database1['Total Cost (USD)'].apply(lambda x: '$ {:,.0f}'.format(x))
    database1['Factory Equipment Cost'] = database1['Factory Equipment Cost'].apply(lambda x: '$ {:,.0f}'.format(x))
    database1['Site Labor Cost'] = database1['Site Labor Cost'].apply(lambda x: '$ {:,.0f}'.format(x))
    database1['Site Material Cost'] = database1['Site Material Cost'].apply(lambda x: '$ {:,.0f}'.format(x))
    database1['Site Labor Hours'] =database1['Site Labor Hours'].apply(lambda x: '{:,.0f} hrs'.format(x))
    
    database1 = database1.fillna('') # remove nan
    database1= database1.replace({'$ nan':'', 'nan hrs':''}) # remove nan


    df_ = database1.loc[database1.Account.isin([10, 20, 30, 40, 50, 60])] # highlight high level accounts

    df_2 = database1.iloc[-10:] # final results
    
    df3 = pd.concat([df_, df_2])
    df4 = df_2 = database1.iloc[-2:]
    slice_ = pd.IndexSlice[df3.index, df3.columns]
    slice_2 = pd.IndexSlice[df4.index, df4.columns]



reactor_power = 310.8 * 1000 # kw
def update_high_level_costs(db):
   
    # update total costs for accounts 21 : 26
    for x in [21, 22, 23, 24, 25, 26]: 
        (db.loc[db['Account'] == x, 'Total Cost (USD)']) = (db.loc[db['Account'] == x, 'Factory Equipment Cost'])+\
            (db.loc[db['Account'] == x, 'Site Labor Cost'])+ (db.loc[db['Account'] == x, 'Site Material Cost'])

    #update total costs for accounts 10
    (db.loc[db['Title'] == '10s - Subtotal', 'Total Cost (USD)']) =\
        db.loc[db['Account'].isin([11, 12, 13, 14, 15, 16, 17, 18]), 'Total Cost (USD)'].sum()
     
    # update total costs for accounts 20
    (db.loc[db['Title'] == '20s - Subtotal', 'Total Cost (USD)']) =\
        db.loc[db['Account'].isin([21, 22, 23, 24, 25, 26, 27, 28]), 'Total Cost (USD)'].sum()

    # update total costs for accounts 30
    (db.loc[db['Title'] == '30s - Subtotal', 'Total Cost (USD)']) =\
        db.loc[db['Account'].isin([31, 32, 33, 34, 35, 36, 37, 38]), 'Total Cost (USD)'].sum()

    # update total costs for accounts 40
    (db.loc[db['Title'] == '40s - Subtotal', 'Total Cost (USD)']) =\
        db.loc[db['Account'].isin([41, 42, 43, 44, 49]), 'Total Cost (USD)'].sum()

    # update total costs for accounts 50
    (db.loc[db['Title'] == '50s - Subtotal', 'Total Cost (USD)']) =\
        db.loc[db['Account'].isin([51, 52, 53, 54, 55, 58, 59]), 'Total Cost (USD)'].sum()

    # update total costs for accounts 60
    (db.loc[db['Title'] == '60s - Subtotal', 'Total Cost (USD)']) =\
        db.loc[db['Account'].isin([61, 62, 63, 69]), 'Total Cost (USD)'].sum()
    
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
        (db.loc[db['Title'] == 'Base Construction Cost (Accounts 10 to 30)', 'Total Cost (USD)']).values + \
        (db.loc[db['Title'] == '40s - Subtotal', 'Total Cost (USD)']).values+\
        (db.loc[db['Title'] == '50s - Subtotal', 'Total Cost (USD)']).values

    (db.loc[db['Title'] == 'Total Capital Investment Cost (Accounts 10 to 60)', 'Total Cost (USD)']) =\
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
        (db.loc[db['Title'] == 'Total Capital Investment Cost (Accounts 10 to 60)', 'Total Cost (USD)']).values/reactor_power

    	
    return db
    
    slice_ = pd.IndexSlice[df3.index, df3.columns]
    slice_2 = pd.IndexSlice[df4.index, df4.columns]
    
    if category == "no_subsidies":
        database_styled = (database1.style.set_properties(**{'font-weight': 'bold'}, subset=slice_).set_properties(**{'color': 'white','background-color': 'white' }, subset=slice_2).set_caption(caption).set_table_styles([{'selector': 'caption','props': [('color', 'red'),('font-size', '20px')]}]))
            
    elif category == "subsidies":
        database_styled = (database1.style.set_properties(**{'font-weight': 'bold'}, subset=slice_).set_caption(caption).\
                           set_table_styles([{'selector': 'caption','props': [('color', 'red'),('font-size', '20px')]}]))
    
    return database_styled.hide()

def highlight_changes(row, baseline):
    return ['background-color: yellow' if val != baseline\
            and len(str(val))>0 and not (str(val)).startswith("Range")  else '' for val in row]






# Reading excel or csv files
SFR_data_0 = pd.read_excel('SFR_allData.xlsx', sheet_name = "SA_Plus_MIT_Combined", nrows= 69)

db = pd.DataFrame()
db = SFR_data_0[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                 'Site Material Cost']].copy()
SFR_data = db
SFR_data_pretty = prettify(SFR_data, "SFR-FOAK Capital Cost Summary - Baseline hypothetical well-executeed project (duration = 64 months) ", "no_subsidies")




## ## User-defined Independent Variables (Global Levers)

# lets start with some basic variables
design_completion = 0.98
proc_exp = 4 # 5 means procurement experts. THis is ideal. In reality, this experience level is less than 5

# Design maturity
design_maturity = 2 # 0 if immature (never done). 2 if mature and ready. 1: in between
ece = 5


ITC  = 0.3 # unchanged for now
#interest rate :

case = "nothing" # initizalition




cases = ['ce_FOAK', 'we_FOAK', 'NOAK']
final_results = []
# This is a hypothetical well-executed project taking 64 months (TIMCAT simulation)
for case in cases: 



    if case == "ce_FOAK":
        
        land_cost_per_acre =  22000 # unchanged for now
    
        # number of firm orders
        num_orders = 2
        # Determining if the turbine and containemnt are non-nuclear or nuclear grade equipment 
        naq_turbine = "nuclear"
        naq_containment = "nuclear"
        # th of a kind
        n_th = 1
        interest_rate = 0.06  # equals 5%. This is the baseline value in the SA report work
        baseline_construction_duration = 100



    if case == "we_FOAK":
        land_cost_per_acre =  0.7*22000 # unchanged for now
        
        # number of firm orders
        num_orders = 10
        # Determining if the turbine and containemnt are non-nuclear or nuclear grade equipment 
        naq_turbine = "non_nuclear"
        naq_containment = "non_nuclear"
        # th of a kind
        n_th = 1
        interest_rate = 0.03  # equals 5%. This is the baseline value in the SA report work
        baseline_construction_duration = 64

        

    if case == "NOAK":
        land_cost_per_acre =  0.7*22000 # unchanged for now
        
        # number of firm orders
        num_orders = 10
        # Determining if the turbine and containemnt are non-nuclear or nuclear grade equipment 
        naq_turbine = "non_nuclear"
        naq_containment = "non_nuclear"
        # th of a kind
        n_th = 100
        interest_rate = 0.03  # equals 5%. This is the baseline value in the SA report work




    # modularization
    mod = "stick_built"


 

    global_levers = pd.DataFrame()
    global_levers.loc[:, 'Lever'] = ['Baseline Construction Duration (months)', 'Design Completion',\
                                    'Procurement service experience ','Engineering & Construction service experience',\
                                    'Number of firm orders',' Land Cost Per Acre (2023 USD)',\
                                    'ITC ', ' Interest Rate', 'NQA-1 Turbine ', 'NQA-1 Containment', 'modulariziation',\
                                    "design maturity" , "#th of a kind"]

    global_levers.loc[:, 'User-Input Value'] = [baseline_construction_duration, design_completion, proc_exp, ece, num_orders, 
                                                land_cost_per_acre, ITC, interest_rate, naq_turbine , naq_containment, mod,\
                                                design_maturity, n_th] 

    global_levers.loc[:, 'Lever baseline value (for a hopothetical well-executed project)'] = [64, 1, 5, 5, 1, 22000, 0, 0.05 ,\
                                                                                            'nuclear', 'nuclear', "stick_built", 2, 1 ]

    global_levers.loc[:, 'Range'] = ['30 - 130', '0 - 1', '1 - 5', '1 - 5', '0 - 10', '1000 - 100000', '0 - 0.5', '0 - 0.3',\
                                    "nuclear or non-nuclear", "nuclear or non-nuclear",  'stick_built or modularized', '0 : 2',
                                    '1 - 1000']



    global_levers_changes = global_levers[global_levers['User-Input Value'] != global_levers['Lever baseline value (for a hopothetical well-executed project)']]

    slice_ = pd.IndexSlice[global_levers_changes .index, global_levers_changes .columns]
    global_levers_styled = (global_levers.style.set_properties(**{'background-color': 'yellow'}, subset=slice_ )\
                                .set_caption("User-Input Global levers <br> (highlighted in yellow if different from the baseline)")\
                            .set_table_styles([{
        'selector': 'caption',
        'props': [
            ('color', 'red'),
            ('font-size', '20px')
        ]
    }]))


    global_levers_styled.hide()





    #creating the table for the account based variables
    accounts_vars = pd.DataFrame()
    accounts_vars.loc[:, 'Account'] = SFR_data.loc[:, 'Account']
    accounts_vars.loc[:, 'Title'] = SFR_data.loc[:, 'Title']


    accounts_vars["Vol Production Learning Rate"] = None
    accounts_vars["FOAK Delays (months)"] = None
    accounts_vars["Task Acceleration factor"] = None
    accounts_vars["Supply Chain Delay factor"] = None
    accounts_vars["Labor Productivity Factor"] = None

    accounts_vars = accounts_vars.loc[accounts_vars['Account'].isin([21, 22, 23, 24, 25, 26])]

    if case == "ce_FOAK":
        # Assigning independent account-based variables
        accounts_vars['Vol Production Learning Rate'] = [0.05, 0.05, 0, 0.05, 0.05, 0.05] 
        accounts_vars['FOAK Delays (months)'] = [1, 2, 3, 0, 0, 0]

        # task acceleration = 1 means no change. Task acceleration = 0.5 means the labor hours decreases by half (optimistic scenario)
        accounts_vars['Task Acceleration factor'] = [1, 1, 1, 1, 1, 1] 


    if case == "we_FOAK":
        # Assigning independent account-based variables
        accounts_vars['Vol Production Learning Rate'] = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2] 
        accounts_vars['FOAK Delays (months)'] = [0, 0, 0, 0, 0, 0]

        # task acceleration = 1 means no change. Task acceleration = 0.5 means the labor hours decreases by half (optimistic scenario)
        accounts_vars['Task Acceleration factor'] = [0.8, 0.9, 0.95, 0.8, 0.9, 0.95]  

    if case == "NOAK":
        # Assigning independent account-based variables
        accounts_vars['Vol Production Learning Rate'] = [0.15, 0.2, 0.15, 0.2, 0.15, 0.2] 
        accounts_vars['FOAK Delays (months)'] = [0, 0, 0, 0, 0, 0]

        # task acceleration = 1 means no change. Task acceleration = 0.5 means the labor hours decreases by half (optimistic scenario)
        accounts_vars['Task Acceleration factor'] = [0.8, 0.8, 0.8, 0.8, 0.8, 0.8]         


    # Assigning dependent account-based variables

    # supply chain delay factor = f(Procurement service experience level)
    # The delay factor = 2 if the experience level = 1  && The delay factor = 1 if the experience level = 5
    # Therefore, we can formulate a simple equation
    # supply chain delay factor  = 0.25*(9 - Procurement service experience level )
    supply_chain_delay_factor_1= 0.25*(9 - proc_exp)

    # supply chain delay is also a function of the design maturity as follows
    # - Supply chain delays - (0 - 2x supplychain delays, 1 - 1.5x supplychain delays, 2 - no effect on supplychain delays) 
    if design_maturity == 0:
        supply_chain_delay_factor_2 = 2 
    elif design_maturity == 1:    
        supply_chain_delay_factor_2 = 1.5 
    elif design_maturity == 2:
        supply_chain_delay_factor_2 = 1 

    supply_chain_delay_factor = min (supply_chain_delay_factor_1*supply_chain_delay_factor_2, 2)
    accounts_vars['Supply Chain Delay factor']  = supply_chain_delay_factor


    # labor productivity factor = f(engineering and construction experience level)
    # labor productivity factor = 0.2 if the experience level = 1  && labor productivity factor =  = 1 if the experience level = 5
    # Therefore, we can formulate a simple equation
    #labor productivity factor  = 0.2* engineering and construction experience leve

    accounts_vars['Labor Productivity Factor'] = 0.2*ece 


    accounts_vars.loc[len(accounts_vars)] = pd.Series(dtype='float64')
    accounts_vars = accounts_vars.fillna('') # remove nan

    accounts_vars.loc[len(accounts_vars.index)] = \
        ['', 'Baseline Value = ', 0, 0, 1, 1, 0] 

    accounts_vars.loc[len(accounts_vars.index)] = \
        ['', ' ', "Range = 0 : 1", "Range = 0 : 100", "Range = 0.5 : 1","Range = 1 : 2", "Range = 0 : 1"]  




    accounts_vars_styled = accounts_vars.style.apply(highlight_changes, axis=1, subset=pd.IndexSlice[:, ['Vol Production Learning Rate']], baseline =0)\
        .apply(highlight_changes, axis=1, subset=pd.IndexSlice[:, ['FOAK Delays (months)']], baseline =0)\
        .apply(highlight_changes, axis=1, subset=pd.IndexSlice[:, ['Task Acceleration factor']], baseline =1)\
        .apply(highlight_changes, axis=1, subset=pd.IndexSlice[:, ['Supply Chain Delay factor']], baseline =1)\
        .apply(highlight_changes, axis=1, subset=pd.IndexSlice[:, ['Labor Productivity Factor']], baseline =0)\
        .set_caption("User-Input Account-Based levers <br> (highlighted in yellow if different from the baseline)").set_table_styles([{
        'selector': 'caption',
        'props': [
            ('color', 'red'),
            ('font-size', '20px')
        ]}])
    accounts_vars_styled.hide()




    # The cost of the land is 22000$ per acre (500 acres
    # The cost is multiplied by the new $/acre divided by the old one
    # Accounts 11 and 12 are changed


    db = pd.DataFrame()
    db = SFR_data_0[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()


    db.loc[db.Account == 11, 'Total Cost (USD)'] = None # clear old values
    db.loc[db.Account == 12, 'Total Cost (USD)'] = None # clear old values

    db.loc[db.Account == 11, 'Total Cost (USD)'] = (land_cost_per_acre /22000)*(SFR_data_0.loc[SFR_data_0.Account == 11, 'Total Cost (USD)'].values)
    db.loc[db.Account == 12, 'Total Cost (USD)'] = (land_cost_per_acre /22000)*(SFR_data_0.loc[SFR_data_0.Account == 12, 'Total Cost (USD)'].values)

    SFR_data_updated_1 = update_high_level_costs(db)


    SFR_data_updated_1_ = pd.DataFrame()
    SFR_data_updated_1_ = SFR_data_updated_1[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    SFR_data_updated_1_pretty = prettify(SFR_data_updated_1_, "SFR-FOAK Capital Cost Summary - Updated ", 'no_subsidies')



    # The change in factory equipment cost due to LR and number of orders
    # cost reduction factor = (1 - Learning rate)^(log2(N))
    db = pd.DataFrame()

    db = SFR_data_updated_1[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    for x in [21, 22, 23, 24, 25, 26]:  
        db.loc[db.Account == x, 'Factory Equipment Cost'] = None # clear old values


    for x in [21, 22, 23, 24, 25, 26]: 
        if num_orders == 0:
            reduction_factor = 1 # no reduction
        else:    
            reduction_factor = (1 - (accounts_vars.loc[accounts_vars['Account'] == x, 'Vol Production Learning Rate']).values)**np.log2(num_orders)

        # cost reduction factor multiplied by factory cost
        db.loc[db.Account == x, 'Factory Equipment Cost'] =\
            ((( SFR_data_updated_1.loc[ SFR_data_updated_1.Account == x, 'Factory Equipment Cost']).values)[0])*reduction_factor

    SFR_data_updated_2 = update_high_level_costs(db)

    SFR_data_updated_2_ = pd.DataFrame()
    SFR_data_updated_2_ = SFR_data_updated_2[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()
    SFR_data_updated_2_pretty = prettify(SFR_data_updated_2_, "SFR-FOAK Capital Cost Summary - Updated", "no_subsidies")






    # If nuclear, the materials cost is 50% higher, the labor cost is 30% higher
    # if non-nuclear, the cost reduction factors for the materials and labor are 0.67 and 0.77 respectively
    db = pd.DataFrame()

    db = SFR_data_updated_2[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    db.loc[db.Account == 21, 'Site Material Cost'] = None # clear old values
    db.loc[db.Account == 21, 'Site Labor Cost'] = None # clear old values
    db.loc[db.Account ==  21, 'Site Labor Hours'] = None
    db.loc[db.Account ==  23, 'Site Material Cost'] = None
    db.loc[db.Account ==  23, 'Site Labor Cost']  = None
    db.loc[db.Account ==  23, 'Site Labor Hours'] = None

    if naq_containment == "non_nuclear":
        db.loc[db.Account == 21, 'Site Material Cost'] = 0.67*((SFR_data_updated_2.loc[SFR_data_updated_2.Account == 21, 'Site Material Cost']).values)
        db.loc[db.Account == 21, 'Site Labor Cost'] = 0.77*((SFR_data_updated_2.loc[SFR_data_updated_2.Account == 21, 'Site Labor Cost']).values)
        db.loc[db.Account == 21,'Site Labor Hours'] = 0.77*((SFR_data_updated_2.loc[SFR_data_updated_2.Account == 21, 'Site Labor Hours']).values)

    else:
        db.loc[db.Account == 21, 'Site Material Cost'] = ((SFR_data_updated_2.loc[SFR_data_updated_2.Account == 21, 'Site Material Cost']).values)
        db.loc[db.Account == 21, 'Site Labor Cost'] = ((SFR_data_updated_2.loc[SFR_data_updated_2.Account == 21, 'Site Labor Cost']).values)
        db.loc[db.Account == 21,'Site Labor Hours'] = ((SFR_data_updated_2.loc[SFR_data_updated_2.Account == 21, 'Site Labor Hours']).values)

    if naq_turbine == "non_nuclear":
        db.loc[db.Account == 23, 'Site Material Cost'] = 0.67*((SFR_data_updated_2.loc[SFR_data_updated_2.Account == 23, 'Site Material Cost']).values)
        db.loc[db.Account == 23, 'Site Labor Cost'] = 0.77*((SFR_data_updated_2.loc[SFR_data_updated_2.Account == 23, 'Site Labor Cost']).values)
        db.loc[db.Account == 23, 'Site Labor Hours'] = 0.77*((SFR_data_updated_2.loc[SFR_data_updated_2.Account == 23, 'Site Labor Hours']).values)

    else:
        db.loc[db.Account == 23, 'Site Material Cost'] = ((SFR_data_updated_2.loc[SFR_data_updated_2.Account == 23, 'Site Material Cost']).values)
        db.loc[db.Account == 23, 'Site Labor Cost'] = ((SFR_data_updated_2.loc[SFR_data_updated_2.Account == 23, 'Site Labor Cost']).values)
        db.loc[db.Account == 23, 'Site Labor Hours'] = ((SFR_data_updated_2.loc[SFR_data_updated_2.Account == 23, 'Site Labor Hours']).values)
    db

    SFR_data_updated_3 = update_high_level_costs(db)

    SFR_data_updated_3_ = pd.DataFrame()
    SFR_data_updated_3_ = SFR_data_updated_3[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    SFR_data_updated_3_pretty = prettify(SFR_data_updated_3_, "SFR-FOAK Capital Cost Summary - Updated ", 'no_subsidies')




    # The change in the labor hours under Account 20 due to 4 factors
    # 1- task acceleration factor #(if <1, the labor hours decrease per account. if 0.5, labor hours are divided by 2
    # 2- supply chain delay factor,  #if 1, no change, if 1.5, labor hours increase by 50%
    # 3- labor producitivy factor,  # if 1, perfect scenario, if <1, labor hours increase
    # 4- FOAK delays (months)

    # The first three factors can be lumped together in one multiplier
    # multiplier = (Task Acceleration factor * supply chain delay factor)/labor producitivy factor



    # change in labor hours due to the FOAK delays (months)
    # The current labor hours are based on a total construction duration of 64 month. 
    #Therefore, the labor hours per each account will be multiplied by (64 + FOAK delay) / 64

    db = pd.DataFrame()
    db = SFR_data_updated_3[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()


    # clear old values
    for x in [21, 22, 23, 24, 25, 26]: 
        db.loc[db.Account == x, 'Site Labor Hours'] = None
        db.loc[db.Account == x, 'Site Labor Cost']  = None
        

    for x in [21, 22, 23, 24, 25, 26]: 
        multiplier = ((accounts_vars.loc[accounts_vars['Account'] == x, 'Task Acceleration factor']).values)*\
            ((accounts_vars.loc[accounts_vars['Account'] == x, 'Supply Chain Delay factor']).values)/\
            ((accounts_vars.loc[accounts_vars['Account'] == x, 'Labor Productivity Factor']).values)
        
        multiplier_FOAK = (((accounts_vars.loc[accounts_vars['Account'] == x, 'FOAK Delays (months)']).values) +\
            baseline_construction_duration)/ baseline_construction_duration


        db.loc[db.Account == x, 'Site Labor Hours'] =  ((SFR_data_updated_3.loc[ SFR_data_updated_3.Account == x, 'Site Labor Hours']).values)\
            *multiplier*multiplier_FOAK

        #  # labor cost will increase due to increaseing labor hours

        db.loc[db.Account == x, 'Site Labor Cost'] =  (( SFR_data_updated_3.loc[ SFR_data_updated_3.Account == x, 'Site Labor Cost']).values)\
            *multiplier*multiplier_FOAK


    SFR_data_updated_4 = update_high_level_costs(db)

    SFR_data_updated_4_ = pd.DataFrame()
    SFR_data_updated_4_ = SFR_data_updated_4[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    SFR_data_updated_4_pretty = prettify(SFR_data_updated_4_, "SFR-FOAK Capital Cost Summary - Updated ", 'no_subsidies')




    # Construction duration: Use Vogtle example - 2x duration for 50% design completion. 1x duration for 100% design completion. 
    # we derive a simple equation: construction duration multiplier = 3 -2 * design completion
    # note that design completion ranges from 0 to 1

    actual_construction_duration = baseline_construction_duration*(3 - 2*design_completion)


    #sum of labor hours for Account 20 in the initial estimation (well exectued scenario)
    sum_old = (SFR_data_0.loc[SFR_data_0.Account == 21, 'Site Labor Hours']).values +\
    (SFR_data_0.loc[SFR_data_0.Account == 22, 'Site Labor Hours']).values +\
    (SFR_data_0.loc[SFR_data_0.Account == 23, 'Site Labor Hours']).values+\
    (SFR_data_0.loc[SFR_data_0.Account == 24, 'Site Labor Hours']).values+\
    (SFR_data_0.loc[SFR_data_0.Account == 25, 'Site Labor Hours']).values+\
    (SFR_data_0.loc[SFR_data_0.Account == 26, 'Site Labor Hours']).values



    #sum of labor hours for Account 20 in the new estimation (well exectued scenario)
    db = SFR_data_updated_4 
    sum_new = (db.loc[db.Account == 21, 'Site Labor Hours']).values +\
    (db.loc[db.Account == 22, 'Site Labor Hours']).values +\
    (db.loc[db.Account == 23, 'Site Labor Hours']).values+\
    (db.loc[db.Account == 24, 'Site Labor Hours']).values+\
    (db.loc[db.Account == 25, 'Site Labor Hours']).values+\
    (db.loc[db.Account == 26, 'Site Labor Hours']).values



    # # change in labor hours for account 20
    change = (sum_new - sum_old)/sum_old   # note that this number can be positive or negative


    # # From EPRI 2019 report, the decrease in total hours to 50$ leads to 24% decrease in construction timeline.
    # # so I assume that the change in the construction timeline equals 50% of the the change in the total labor hours

    construction_duration_change = 0.5*change  *baseline_construction_duration

    final_construction_duration = (actual_construction_duration + construction_duration_change)[0]

    print("\nThe actual construction duration is estimated to be : ", int(final_construction_duration), "months\n") 

    # # From the TIMCAT simulation, the indirect cost changes almost linearly by 28% if the number of construction duration increased from 64 to 100 months
    # # Using this, we can derive a simple equation :
    # # Indirect cost / Indirect cost (well exectued scenario : 64 months)  =  0.0081* construction duration + 0.4627
    # we assume that all the subaccounts under the indriect cost will increae by the same ratio
    # # upadting the indirect cost as follows
    indirect_cost_multiplier = 0.0081*final_construction_duration + 0.4627


    # create new database to add the new costs
    # all the subaccounts under the indirect cost are increased equally
    db = pd.DataFrame()
    db = SFR_data_updated_4[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    for x in [31, 32, 33, 34 ,35, 36, 37, 38]: 
        db.loc[db.Account == x, 'Total Cost (USD)'] = None

    for x in [31, 32, 33, 34 ,35, 36, 37, 38]:
        db.loc[db.Account == x, 'Total Cost (USD)'] =  indirect_cost_multiplier*SFR_data_updated_4.loc[ SFR_data_updated_4.Account == x, 'Total Cost (USD)'] 



    SFR_data_updated_5 = update_high_level_costs(db)

    SFR_data_updated_5_ = pd.DataFrame()
    SFR_data_updated_5_ = SFR_data_updated_5[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    SFR_data_updated_5_pretty = prettify(SFR_data_updated_5_, "SFR-FOAK Capital Cost Summary - Updated ", "no_subsidies")











    # # tot overnight cost = accounts 10 - 50
    # # I cheated this from Levi : SC-HTGR-costreduction_LML.xlsx
    tot_overnight_cost = (SFR_data_updated_5.loc[SFR_data_updated_5.Title == 'Total Overnight Cost (Accounts 10 to 50)' , 'Total Cost (USD)']).values[0]


    # # Interest rate from this equation (from Levi)
    B =(1+ np.exp((np.log(1+ interest_rate)) * final_construction_duration/12))
    C  =((np.log(1+ interest_rate)*(final_construction_duration/12)/3.14)**2+1)
    Interest_expenses = tot_overnight_cost*((0.5*B/C)-1)

    db = pd.DataFrame()

    db = SFR_data_updated_5[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()
    db.loc[db.Account == 63, 'Total Cost (USD)'] = None # clear old values
    Interest_expenses
    (db.loc[db.Account == 63, 'Total Cost (USD)']) = Interest_expenses

    SFR_data_updated_6 = update_high_level_costs(db)

    FR_data_updated_6_ = pd.DataFrame()
    SFR_data_updated_6_ = SFR_data_updated_6[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    SFR_data_updated_6_pretty = prettify(SFR_data_updated_6_, "SFR-FOAK Capital Cost Summary - Updated ", 'no_subsidies')
    SFR_data_updated_6_pretty





    # insurance increases linearly when increaing the sum of the 20s and 30s account
    db = pd.DataFrame()

    db = SFR_data_updated_6[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()
    db0 = SFR_data_0
    db.loc[db.Account == 54, 'Total Cost (USD)'] = None # clear old values

    change_in_insuance_cost = (db.loc[db.Title =='20s - Subtotal', 'Total Cost (USD)'].values\
                            + db.loc[db.Title =='30s - Subtotal', 'Total Cost (USD)'].values)/ (db0.loc[db0.Title =='20s - Subtotal', 'Total Cost (USD)'].values\
                            + db0.loc[db0.Title =='30s - Subtotal', 'Total Cost (USD)'].values)

    db.loc[db.Account == 54, 'Total Cost (USD)'] =  (change_in_insuance_cost[0])* (SFR_data_updated_6.loc[db.Account == 54, 'Total Cost (USD)'])

    SFR_data_updated_7 = update_high_level_costs(db)

    SFR_data_updated_7_ = pd.DataFrame()
    SFR_data_updated_7_ = SFR_data_updated_7[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    SFR_data_updated_7_pretty = prettify(SFR_data_updated_7_, "SFR-FOAK Capital Cost Summary - Updated ", 'no_subsidies')
    SFR_data_updated_7_pretty





    b = SFR_data_updated_7
    tot_cap_investment = db.loc[db.Title =='Total Capital Investment Cost (Accounts 10 to 60)', 'Total Cost (USD)'].values

    # #from levi's equation, the multipliers change with the ITC as follows

    cost_multiplier = min(-0.9387*ITC+ 1.0046, 1)
    ITC_reduced_capital_cost  = cost_multiplier*tot_cap_investment


    db1 = pd.DataFrame()
    db1 = SFR_data_updated_7[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    db1.loc[db1.Title== 'Total Capital Investment Cost (ITC reduced)', 'Total Cost (USD)'] = None
    db1.loc[db1.Title== 'Total Capital Investment Cost (ITC reduced) - US$/kWe', 'Total Cost (USD)'] = None


    db1.loc[db1.Title== 'Total Capital Investment Cost (ITC reduced)', 'Total Cost (USD)'] = ITC_reduced_capital_cost
    db1.loc[db1.Title== 'Total Capital Investment Cost (ITC reduced) - US$/kWe', 'Total Cost (USD)'] = ITC_reduced_capital_cost/reactor_power


    SFR_data_updated_8 = update_high_level_costs(db1)

    SFR_data_updated_8_ = pd.DataFrame()
    SFR_data_updated_8_ = SFR_data_updated_8[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    SFR_data_updated_8_pretty = prettify(SFR_data_updated_8_, "SFR-FOAK Capital Cost Summary - Updated ", 'subsidies')










    #  FOAK to NOAK

    db = pd.DataFrame()
    db = SFR_data_updated_8[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    # remove old values
    for x in [21, 22, 23, 24, 25, 26]:
        db.loc[db.Account== x, 'Total Cost (USD)']       = None
        db.loc[db.Account== x, 'Factory Equipment Cost'] = None
        db.loc[db.Account== x, 'Site Labor Hours']       = None
        db.loc[db.Account== x, 'Site Labor Cost']        = None
        db.loc[db.Account== x, 'Site Material Cost']     = None

    for x in [31, 32, 33, 34 ,35, 36, 37, 38]: 
        db.loc[db.Account == x, 'Total Cost (USD)'] = None


    # # # Equation for accounts 21, 24, 25, 26 factory equipment cost for the nth of a kind reactor
    #  y = x ^ (-0.015)

    for x in [21, 24, 25, 26]: 
        db.loc[db.Account == x, 'Factory Equipment Cost'] =\
            ((SFR_data_updated_8.loc[SFR_data_updated_8.Account == x, 'Factory Equipment Cost']).values) * (n_th ** (-0.015))



    # # Equation for accounts 22, 23 factory equipment
    #  y = x ^ (-0.074)
    for x in [22, 23]: 
        db.loc[db.Account == x, 'Factory Equipment Cost'] =\
            ((SFR_data_updated_8.loc[SFR_data_updated_8.Account == x, 'Factory Equipment Cost']).values) * (n_th ** (-0.074))



    # # Equation for accounts 21, 24, 25, 26
    # # labor cost and labor hours
    #  y = x ^ (-0.2)
    for x in [21, 24, 25, 26]: 
        db.loc[db.Account == x, 'Site Labor Hours'] =\
            ((SFR_data_updated_8.loc[SFR_data_updated_8.Account == x, 'Site Labor Hours']).values) * (n_th ** (-0.2))
        db.loc[db.Account == x, 'Site Labor Cost'] =\
            ((SFR_data_updated_8.loc[SFR_data_updated_8.Account == x, 'Site Labor Cost']).values) * (n_th ** (-0.2))

        
    # # Equation for accounts 22, 23
    # # labor cost and labor hours
    #  y = x ^ (-0.025)

    for x in [22, 23]: 
        db.loc[db.Account == x, 'Site Labor Hours'] =\
            ((SFR_data_updated_8.loc[SFR_data_updated_8.Account == x, 'Site Labor Hours']).values) * (n_th ** (-0.025))
        db.loc[db.Account == x, 'Site Labor Cost'] =\
            ((SFR_data_updated_8.loc[SFR_data_updated_8.Account == x, 'Site Labor Cost']).values) * (n_th ** (-0.025))

    # # Equation for all the accounts
    # # material cost
    #  y = x ^ (-0.105)
    for x in [21, 22, 23, 24, 25, 26]:
        db.loc[db.Account == x, 'Site Material Cost'] =\
            ((SFR_data_updated_8.loc[SFR_data_updated_8.Account == x, 'Site Material Cost']).values) * (n_th ** (-0.105))


    # # Equation for all the accounts (indirect cost)
    #  y = x ^ (-0.101)

    for x in [31, 32, 33, 34 ,35, 36, 37, 38]:
        db.loc[db.Account == x, 'Total Cost (USD)'] =\
        ((SFR_data_updated_8.loc[ SFR_data_updated_8.Account == x, 'Total Cost (USD)'] ).values)* (n_th ** (-0.101))


    # # Equation for the construction durationc
    #  y = x ^ (-0.174)
    nth_reactor_construction_duration = final_construction_duration* (n_th ** (-0.174))

    print("\nThe construction duration of reactor #", n_th, "is estimated to be : ", int(nth_reactor_construction_duration ), "months\n") 


    # Remove the ITC adjusted cost for the NOAK reactor because it is not updated yet
    # db.drop(db.tail(3).index,inplace=True) # drop last n rows

    SFR_data_updated_9 = update_high_level_costs(db)




    FR_data_updated_9_ = pd.DataFrame()
    SFR_data_updated_9_ = SFR_data_updated_9[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    SFR_data_updated_9_pretty = prettify(SFR_data_updated_9_, f"SFR NOAK ({n_th}th) Capital Cost Summary - Updated ", 'no_subsidies')






    # # tot overnight cost = accounts 10 - 50
    tot_overnight_cost_noak = (SFR_data_updated_9.loc[SFR_data_updated_9.Title\
                            == 'Total Overnight Cost (Accounts 10 to 50)' , 'Total Cost (USD)']).values[0]
    
    # # # Interest rate from this equation (from Levi)
    Bn =(1+ np.exp((np.log(1+ interest_rate)) * nth_reactor_construction_duration/12))
    Cn  =((np.log(1+ interest_rate)*(nth_reactor_construction_duration/12)/3.14)**2+1)
    Interest_expenses_noak = tot_overnight_cost_noak*((0.5*Bn/Cn)-1)

    # create the new database and copy columns from the previous database
    db = pd.DataFrame()
    db = SFR_data_updated_9[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()


    # clear old values
    db.loc[db.Account == 63, 'Total Cost (USD)'] = None # clear old values
    db.loc[db.Account == 54, 'Total Cost (USD)'] = None # clear old values


    # Interest_expenses
    (db.loc[db.Account == 63, 'Total Cost (USD)']) = Interest_expenses_noak


    # update insurance account

    db0 = SFR_data_0

    change_in_insuance_cost = (db.loc[db.Title =='20s - Subtotal', 'Total Cost (USD)'].values\
                            + db.loc[db.Title =='30s - Subtotal', 'Total Cost (USD)'].values)/ (db0.loc[db0.Title =='20s - Subtotal', 'Total Cost (USD)'].values\
                            + db0.loc[db0.Title =='30s - Subtotal', 'Total Cost (USD)'].values)

    db.loc[db.Account == 54, 'Total Cost (USD)'] =  (change_in_insuance_cost[0])* (SFR_data_updated_9.loc[db.Account == 54, 'Total Cost (USD)'])


    SFR_data_updated_10 = update_high_level_costs(db)

    SFR_data_updated_10_ = pd.DataFrame()
    SFR_data_updated_10_ = SFR_data_updated_10[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()

    SFR_data_updated_10_pretty = prettify(SFR_data_updated_10_, f"SFR NOAK ({n_th}th) Capital Cost Summary - Updated ", 'no_subsidies')







    db = SFR_data_updated_10
    tot_cap_investment_noak = db.loc[db.Title =='Total Capital Investment Cost (Accounts 10 to 60)', 'Total Cost (USD)'].values

    ITC_reduced_capital_cost_noak  = cost_multiplier*tot_cap_investment_noak 

    # create new database
    db1 = pd.DataFrame()
    db1 = SFR_data_updated_10[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()





    db1.loc[db1.Title== 'Total Capital Investment Cost (ITC reduced)', 'Total Cost (USD)'] = None
    db1.loc[db1.Title== 'Total Capital Investment Cost (ITC reduced) - US$/kWe', 'Total Cost (USD)'] = None


    db1.loc[db1.Title== 'Total Capital Investment Cost (ITC reduced)', 'Total Cost (USD)'] = ITC_reduced_capital_cost_noak
    db1.loc[db1.Title== 'Total Capital Investment Cost (ITC reduced) - US$/kWe', 'Total Cost (USD)'] = ITC_reduced_capital_cost_noak/reactor_power

    SFR_data_updated_11 = update_high_level_costs(db1)

    SFR_data_updated_11_ = pd.DataFrame()
    SFR_data_updated_11_ = SFR_data_updated_11[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()


    SFR_data_updated_11_pretty = prettify(SFR_data_updated_11_, f"SFR NOAK ({n_th}th) Capital Cost Summary - Updated ", 'subsidies')




    results = [ case, nth_reactor_construction_duration, SFR_data_updated_11.loc[SFR_data_updated_11.Title== '(Accounts 10 to 30) US$/kWe', 'Total Cost (USD)'].values[0],\
                                          SFR_data_updated_11.loc[SFR_data_updated_11.Title== '(Accounts 10 to 50) US$/kWe', 'Total Cost (USD)'].values[0],\
                                          SFR_data_updated_11.loc[SFR_data_updated_11.Title== '(Accounts 10 to 60) US$/kWe', 'Total Cost (USD)'].values[0],\
                                          SFR_data_updated_11.loc[SFR_data_updated_11.Title== 'Total Capital Investment Cost (ITC reduced) - US$/kWe', 'Total Cost (USD)'].values[0]]



    final_results.append(results)
 
# print("hiiiiii\n")
final_results_ar = np.vstack(final_results)
cases = (final_results_ar[:, 0])
durations =((final_results_ar[:, 1]))

durations_1 = [float(numeric_string) for numeric_string in durations]

cost_10_30 = (final_results_ar[:, 2])
cost_10_30_1 = [float(numeric_string) for numeric_string in cost_10_30]
cost_10_50 = (final_results_ar[:, 3])
cost_10_50_1 = [float(numeric_string) for numeric_string in cost_10_50]

cost_10_60 = (final_results_ar[:, 4])
cost_10_60_1 = [float(numeric_string) for numeric_string in cost_10_60]

cost_10_60_ITC= (final_results_ar[:, 5])
cost_10_60_ITC_1 = [float(numeric_string) for numeric_string in cost_10_60_ITC]




db_res= pd.DataFrame({'cases': cases , 'durations': durations_1, 'cost_10_30': cost_10_30_1 ,'cost_10_50': cost_10_50_1, 'cost_10_60' :cost_10_60_1, 'cost_10_60_ITC': cost_10_60_ITC_1})


color = ['lightblue', 'blue', 'purple']
fig, ax = plt.subplots()
ax.bar(db_res['cases'], db_res['durations'],
       color=color)
ax.set(ylabel='Estimated Construction Duration (months)')

plt.show()



db_res1= pd.DataFrame({'cases': cases , 'Construction Cost (Accounts 10 to 30)': cost_10_30_1 ,\
                       'Overnight Cost (Accounts 10 to 50)': cost_10_50_1,\
                          'Capital Investment Cost (Accounts 10 to 60)' :cost_10_60_1 ,\
                              'Capital Investment Cost (ITC-adjusted)': cost_10_60_ITC_1})


db_res1.set_index('cases', inplace=True)
db_res1 = db_res1.stack().to_frame('2023 US$/kW').reset_index()
db_res1.rename(columns={'level_1':'Cost'},inplace=True)

db_res1.head()

g1 = sn.barplot(data=db_res1, x='cases', y='2023 US$/kW', hue='Cost')
g1.set(xlabel=None)

plt.show()
# Type   Item    value
# 0   McDonalds   Single  1
# 1   McDonalds   Double  2
# 2   McDonalds   Many    10
# 3   BK  Single  4
# 4   BK  Double  8

# import seaborn as sns

# sns.barplot(data=df, x='Type', y='value', hue='Item')





