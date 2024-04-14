#!/usr/bin/env python
# coding: utf-8

# <center><table>
#     <tr>
#         <th><img src="./INL1.png",align="middle",height="10000"/></th>
#         <th><img src="./MIT1.png",align="middle",height="10"\></th>
#         <th><img src="./ANL.png",align="middle",height="10"/></th>
#     </tr>
# </table>
# </center>

# # <center>Cost Reduction Framework for Nuclear Reactor Power Plants</center>
# 

# ## Section 0 : Essentials to Run the code

# ### Section 0 - 1 : Importing the libraries

# In[1]:


# Importing libararies
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
# sns.set_theme(style="darkgrid")
sns.set_style("whitegrid")


import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

pd.set_option('display.max_rows', None)

# Things to do
# indirect cost scales with ... ? only standaridzation affect one account which is 25. 



# ### Section 0 - 2 : Control the table style

# In[2]:


def prettify(database1, caption, category):
    database1['Total Cost (USD)'] = database1['Total Cost (USD)'].apply(lambda x: '$ {:,.0f}'.format(x))
    database1['Factory Equipment Cost'] = database1['Factory Equipment Cost'].apply(lambda x: '$ {:,.0f}'.format(x))
    database1['Site Labor Cost'] = database1['Site Labor Cost'].apply(lambda x: '$ {:,.0f}'.format(x))
    database1['Site Material Cost'] = database1['Site Material Cost'].apply(lambda x: '$ {:,.0f}'.format(x))
    database1['Site Labor Hours'] =database1['Site Labor Hours'].apply(lambda x: '{:,.0f} hrs'.format(x))
    
    database1 = database1.fillna('') # remove nan
    database1= database1.replace({'$ nan':'', 'nan hrs':''}) # remove nan


    df_ = database1.loc[database1.Account.isin([10, 20, 30, 40, 50, 60])] # highlight high level accounts

    df_2 = database1.iloc[-15:] # final results  # df_2 = database1.iloc[-10:]
    
    df3 = pd.concat([df_, df_2])
    df4 = df_2 = database1.iloc[-2:]
    slice_ = pd.IndexSlice[df3.index, df3.columns]
    slice_2 = pd.IndexSlice[df4.index, df4.columns]


    
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

def highlight_changes(row, baseline):
    return ['background-color: yellow' if val != baseline\
            and len(str(val))>0 and not (str(val)).startswith("Range")  else '' for val in row]


# ## Section 1 : Reading the Baseline reactor Cost Summary Table 

# In[3]:


plt.figure(figsize=(13, 9))

for reactor_type in ["SFR", "HTGR"]: # This can be SFR or HTGR

    if reactor_type == "SFR":
        # Reading excel or csv files
        Reactor_data_0 = pd.read_excel('SFR_HTGR_data.xlsx', sheet_name = "SFR_SA_Plus_MIT_Combined", nrows= 66)
        reactor_power = 310.8 * 1000 # kw

    elif reactor_type == "HTGR":
        # Reading excel or csv files
        Reactor_data_0 = pd.read_excel('SFR_HTGR_data.xlsx', sheet_name = "HTGR", nrows= 66)
        reactor_power = 1056 * 1000 # kw
        
    db = pd.DataFrame()
    db = Reactor_data_0[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                    'Site Material Cost']].copy()
    Reactor_data = db
    Reactor_data_pretty = prettify(Reactor_data, f"{reactor_type} Reactor-FOAK Capital Cost Summary - Baseline hypothetical well-executeed project  ", "no_subsidies")
    Reactor_data_pretty


# ## Section 2 : A function to update the cost summary table each time a change is made

# In[4]:


# Update the high level costs in the database when changing the low level costs

    def update_high_level_costs(db):


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


# ## Section - 2 : User Inputs

# ### Section - 2 - 1 : User-defined Independent Variables (Global Levers)

# In[5]:

    num_orders = 10
## ## User-defined Independent Variables (Global Levers)

    OCC_EPC_list = []
    TCI_EPC_list = []
    EPC_list = []
    # number of firm orders
    for epc_exp in ['very low', 'low', 'medium', 'high', 'very high']:

        OCC_list = []
        TCI_list = []
        if epc_exp == "very low":
            proc_exp_0 = 0
            ae_exp_0 = 0
            ce_exp_0 = 0

        elif epc_exp == "low":
            proc_exp_0 = 0
            ae_exp_0 = 0
            ce_exp_0 = 1 

        elif epc_exp == "medium":
            proc_exp_0 = 1
            ae_exp_0 = 1
            ce_exp_0 = 1  

        elif epc_exp == "high":
            proc_exp_0 = 1
            ae_exp_0 = 1
            ce_exp_0 = 2   

        elif epc_exp == "very high":
            proc_exp_0 = 2
            ae_exp_0 = 2
            ce_exp_0 = 2            
            
        

        for n_th in range(1, num_orders+1):

            # land cost
            # From the SA report: the cost $22,000 per acre. The land area is 500 acres including recommended buffer
            land_cost_per_acre_0 =  22000 # dollars/acre
            
            startup_0 = 16 # start up duration (months)

            # interest rate :
            interest_rate_0 = 0.06

            design_completion_0 = 0.8 # 1 means 100%

            Design_Maturity_0 = 1

            # # #procurement service experience (supply chain experience)
            # proc_exp_0= 1 # 2 means procurement experts. This is ideal. 
            
            # # #  architecture and engineeringexperience
            # ae_exp_0 = 0
                
            # # #  Construction service experience
            # ce_exp_0 = 1

            # modularity (applied on civil construction only) "stick_built"  or "modularized"
            mod_0 = "stick_built" 

            # cross_site_standardization :
            standardization_0 = 0.8 # 0.7 corresponds to 70% standardization for PWRs

            # # Determining if the BOP and reactor building (containtment) are non-nuclear or nuclear grade equipment (safety related)
            BOP_grade_0 = "non_nuclear"
            RB_grade_0 = "nuclear"

            # #investment tax credits subsidies
            ITC_0 =  0#
            #number of reactors claiming ITC
            n_ITC = 3 

            if n_th <= n_ITC:
                ITC = ITC_0
            else:
                ITC =0

            # This is a hypothetical well-executed project taking 64 months (TIMCAT simulation)
            if reactor_type == "SFR": 
                baseline_construction_duration = 64 # months
            elif reactor_type == "HTGR":  
                baseline_construction_duration = 100 # months
                

            # numb er of projects for full efficiency
            N_proc = 3
            N_AE  = 4
            N_cons =5



            if n_th == 1:
                land_cost_per_acre = land_cost_per_acre_0 
                
                startup = startup_0
                
                interest_rate =interest_rate_0
                
                design_completion = design_completion_0 
                
                Design_Maturity = Design_Maturity_0
                
                proc_exp = proc_exp_0
                
                # #  architecture and engineeringexperience
                ae_exp =ae_exp_0
                    
                # #  Construction service experience
                ce_exp = ce_exp_0
                
                # modularity (applied on civil construction only) "stick_built"  or "modularized"
                mod = mod_0
                
                # cross_site_standardization :
                standardization = standardization_0 
                
                # # Determining if the BOP and reactor building (containtment) are non-nuclear or nuclear grade equipment (safety related)
                BOP_grade = BOP_grade_0
                RB_grade = RB_grade_0
            



                


            # Change the levers if n >1
            if n_th >1:
                land_cost_per_acre = land_cost_per_acre_0
                
                startup = max( 7 , startup_0*(1-0.3)**np.log2(n_th)  )

                interest_rate =interest_rate_0

                design_completion  = 1

                Design_Maturity = 2
                proc_exp = min( (proc_exp_0 + (2/N_proc)*(n_th-1) ), 2)

                ae_exp = min( (ae_exp_0 + (2/N_AE)*(n_th-1) ), 2)

                ce_exp = min( (ce_exp_0 + (2/N_cons)*(n_th-1) ), 2)

                standardization = 0.8
                mod = "modularized"

                BOP_grade = "non_nuclear"
                RB_grade = "non_nuclear"


            # labor productivity factor = f(construction experience level)
            productivity = 0.145*ce_exp + 0.71

            global_levers = pd.DataFrame()
            global_levers.loc[:, 'Lever'] = ['Baseline Construction Duration (months)', 'Design Completion',\
                                            'Procurement (supply chain) experience ','Architecture & Engineering Experience',\
                                            'Construction service experience',' Land Cost Per Acre (2023 USD)',\
                                            'ITC ', ' Interest Rate', 'BOP grade ', 'Reactor Building grade', 'modulariziation',\
                                            'standardization' , 'productivity',"#th of a kind", "Startup duration (months)"]

            global_levers.loc[:, 'User-Input Value'] = [baseline_construction_duration, design_completion, proc_exp, ae_exp, ce_exp, 
                                                        land_cost_per_acre, ITC, interest_rate, BOP_grade  , RB_grade , mod,\
                                                        standardization, productivity ,n_th, startup] 

            global_levers.loc[:, 'Lever baseline value (for a hopothetical well-executed project)'] = [baseline_construction_duration, 1, 2, 2, 2, 22000, 0, 0.06 ,\
                                                                                                    'nuclear', 'nuclear', "stick_built", 0.7 , 1 , 1, 16 ]

            global_levers.loc[:, 'Range'] = ['30 - 130', '0 - 1', '0 - 2', '0 - 2','0 - 2' , '1000 - 100000', '0 - 0.5', '0 - 0.3',\
                                            "nuclear or non-nuclear", "nuclear or non-nuclear",  'stick_built or modularized', '0 : 1','0 : 1',
                                            '1 - 1000', '3 : 24']



            global_levers_changes = global_levers[global_levers['User-Input Value'] != global_levers['Lever baseline value (for a hopothetical well-executed project)']]

            slice_ = pd.IndexSlice[global_levers_changes .index, global_levers_changes .columns]
            global_levers_styled = (global_levers.style.set_properties(**{'background-color': 'yellow'}, subset=slice_ )\
                                        .set_caption("User-Input Global levers <br> (highlighted in yellow if different from the baseline) <br>")\
                                    .set_table_styles([{
                'selector': 'caption',
                'props': [
                    ('color', 'blue'),
                    ('font-size', '20px')
                ]
            }]))


            global_levers_styled.hide()


            # ### Section - 2 - 2 : User-defined Account-Based Variables

            # In[6]:


            # Creating the table for the account based variables
            accounts_vars = pd.DataFrame()
            accounts_vars.loc[:, 'Account'] = Reactor_data.loc[:, 'Account']
            accounts_vars.loc[:, 'Title'] = Reactor_data.loc[:, 'Title']

            accounts_vars["Design Maturity"] = None
            accounts_vars["Supply Chain Delay (monthhs)"] = None

            accounts_vars = accounts_vars.loc[accounts_vars['Account'].isin([21, 22, 23, 24, 25, 26])]


            # Assigning independent account-based variables
            # design_maturity = 2 # 0 if immature (never done). 2 if mature and ready. 1: in between



            accounts_vars['Design Maturity'] = [Design_Maturity, Design_Maturity, Design_Maturity, Design_Maturity, Design_Maturity, Design_Maturity] 

                


            # Assigning dependent account-based variables

            # Supply chain delay(months)= supply chain delay due to design immaturity (months) * delayfactor due to procurement inexperience
            # supply chain delay due to design immaturity (months)= -6*design immaturity+12
            # delayfactor due to procurement inexperience leads to extra 12 months


            accounts_vars["Supply Chain Delay (monthhs)"] = - 6 *(accounts_vars['Design Maturity']) - 3*proc_exp + 18


            accounts_vars.loc[len(accounts_vars)] = pd.Series(dtype='float64')
            accounts_vars = accounts_vars.fillna('') # remove nan

            accounts_vars.loc[len(accounts_vars.index)] = \
                ['', 'Baseline Value = ', 2, 0] 

            accounts_vars.loc[len(accounts_vars.index)] = \
                ['', ' ', "Range = 0 : 1", "Range = 0 : 18"]  


            accounts_vars

            accounts_vars_styled = accounts_vars.style.apply(highlight_changes, axis=1, subset=pd.IndexSlice[:, ['Design Maturity']], baseline = 2)\
                .apply(highlight_changes, axis=1, subset=pd.IndexSlice[:, ['Supply Chain Delay (monthhs)']], baseline =0)\
                .set_caption("User-Input Account-Based levers <br> (highlighted in yellow if different from the baseline)").set_table_styles([{
                'selector': 'caption',
                'props': [
                    ('color', 'red'),
                    ('font-size', '20px')
                ]}])
            accounts_vars_styled.hide()


            # ### Section - 2 - 3 : Cost reduction framework
            # 
            # <center><table>
            #     <tr>
            #         <th><img src="./framework_diagram.png",align="middle",height="10000"/></th>
            #     </tr>
            # </table>
            # </center>

            # ## Section - 3 : Updating the Cost Summary based on user inputs

            # ### Section - 3-0 : Adding the factory cost to accounts 22 and 232.1

            # In[7]:


            db = pd.DataFrame()
            db = Reactor_data_0[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                            'Site Material Cost']].copy()

            db.loc[db.Account == 22, 'Factory Equipment Cost'] = None # clear old values
            db.loc[db.Account == '232.1', 'Factory Equipment Cost'] = None # clear old values

            # factory building cost
            f_22   = 250000000
            f_2321 = 150000000
            db.loc[db.Account == 22, 'Factory Equipment Cost'] = ((Reactor_data_0.loc[Reactor_data_0.Account == 22, 'Factory Equipment Cost']) + f_22/num_orders )
            db.loc[db.Account == '232.1', 'Factory Equipment Cost'] = ((Reactor_data_0.loc[Reactor_data_0.Account == '232.1', 'Factory Equipment Cost']) + f_2321/num_orders)


            Reactor_data_fac = update_high_level_costs(db)


            Reactor_data_fac_ = pd.DataFrame()
            Reactor_data_fac_ = Reactor_data_fac[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                            'Site Material Cost']].copy()

            Reactor_data_fac_pretty = prettify(Reactor_data_fac_, "Reactor-FOAK Capital Cost Summary - Updated ", 'no_subsidies')

            Reactor_data_fac_pretty


            # ### Section 3-1 : The land cost & Taxes

            # In[8]:


            # The cost of the land is 22000$ per acre (500 acres
            # The cost is multiplied by the new $/acre divided by the old one
            # Accounts 11 and 12 are changed


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
            Reactor_data_updated_1 = update_high_level_costs(db)


            Reactor_data_updated_1_ = pd.DataFrame()
            Reactor_data_updated_1_ = Reactor_data_updated_1[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                            'Site Material Cost']].copy()

            Reactor_data_updated_1_pretty = prettify(Reactor_data_updated_1_, "Reactor-FOAK Capital Cost Summary - Updated ", 'no_subsidies')

            Reactor_data_updated_1_pretty


            # ### Section 3-2 : Whether the Reactor Building and BOP are nuclear grade equipment

            # In[9]:


            # if the BOP is non-nuclear, the cost reduction factor for account 213 is 0.6
            # Also, the cost reduction factor for account 232.1 is 0.6 (for factory and labor but not material)

            # If the reactor building is non nuclear, the cost reduction factor for acount 212 is 0.6
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
                db.loc[db.Account == 212,'Factory Equipment Cost'] = ((Reactor_data_updated_1.loc[Reactor_data_updated_1.Account == 212, 'Site Labor Hours']).values)

                
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


            Reactor_data_updated_2 = update_high_level_costs(db)

            Reactor_data_updated_2_ = pd.DataFrame()
            Reactor_data_updated_2_ = Reactor_data_updated_2[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                            'Site Material Cost']].copy()

            Reactor_data_updated_2_pretty = prettify(Reactor_data_updated_2_, "Reactor-FOAK Capital Cost Summary - Updated ", 'no_subsidies')
            Reactor_data_updated_2_pretty


            # ### Section 3-3  : Modularity

            # In[10]:


            # If TRUE, increase factory cost by <factor>, reduce site material hours by <factor>, and reduce site labor hours & cost by <factor>.
            # This applies only on accuount 21
            # we apply the modularity on acoounts 212, 213, 211 plus 214 to 219	 and account 21 updates automatically
            # The multipliers are 1.3, 0.3. 0.3

            db = pd.DataFrame()

            db = Reactor_data_updated_2[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                            'Site Material Cost']].copy()



            # remove old stuff

            for x in [212, 213,  '211 plus 214 to 219']:  
                db.loc[db.Account == x, 'Factory Equipment Cost'] = None # clear old values
                db.loc[db.Account == x, 'Site Labor Hours'] = None
                db.loc[db.Account == x, 'Site Labor Cost'] = None
                db.loc[db.Account == x, 'Site Material Cost'] = None



            for x in [212, 213,'211 plus 214 to 219']: 
                if mod == 'modularized':
                    db.loc[db.Account == x, 'Factory Equipment Cost'] =\
                    ((Reactor_data_updated_2.loc[Reactor_data_updated_2.Account == x, 'Factory Equipment Cost']).values)*1.3
                    
                    db.loc[db.Account == x, 'Site Labor Hours'] =\
                    ((Reactor_data_updated_2.loc[Reactor_data_updated_2.Account == x, 'Site Labor Hours']).values)*0.7
                    
                    db.loc[db.Account == x, 'Site Labor Cost'] =\
                    ((Reactor_data_updated_2.loc[Reactor_data_updated_2.Account == x, 'Site Labor Cost']).values)*0.7
                
                    db.loc[db.Account == x, 'Site Material Cost'] =\
                    ((Reactor_data_updated_2.loc[Reactor_data_updated_2.Account == x, 'Site Material Cost']).values)*0.7

                else:
                    db.loc[db.Account == x, 'Factory Equipment Cost'] =\
                    ((Reactor_data_updated_2.loc[Reactor_data_updated_2.Account == x, 'Factory Equipment Cost']).values)*1
                    
                    db.loc[db.Account == x, 'Site Labor Hours'] =\
                    ((Reactor_data_updated_2.loc[Reactor_data_updated_2.Account == x, 'Site Labor Hours']).values)*1
                    
                    db.loc[db.Account == x, 'Site Labor Cost'] =\
                    ((Reactor_data_updated_2.loc[Reactor_data_updated_2.Account == x, 'Site Labor Cost']).values)*1
                
                    db.loc[db.Account == x, 'Site Material Cost'] =\
                    ((Reactor_data_updated_2.loc[Reactor_data_updated_2.Account == x, 'Site Material Cost']).values)*1

            Reactor_data_updated_3 = update_high_level_costs(db)
            Reactor_data_updated_3_ = pd.DataFrame()
            Reactor_data_updated_3_ = Reactor_data_updated_3[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                            'Site Material Cost']].copy()

            Reactor_data_updated_3_pretty = prettify(Reactor_data_updated_3_, "Reactor-FOAK Capital Cost Summary - Updated ", 'no_subsidies')
            Reactor_data_updated_3_pretty


            # ### Section 3-4 : Bulk Ordering

            # In[11]:


            #The factory equipment cost of  accounts 22 and 232.1 has to be divided by the number of orders
            # The factory equipment cost of account 22 is multiplied by a reuction factor
            # The factory equipment cost of account 232.1 is multiplied by a reduction factor

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


            db.loc[db.Account == 22, 'Factory Equipment Cost']       = reduction_factor_22   *  (( Reactor_data_updated_3.loc[ Reactor_data_updated_3.Account == 22, 'Factory Equipment Cost']))  
            db.loc[db.Account == '232.1', 'Factory Equipment Cost']  = reduction_factor_2321 *  (( Reactor_data_updated_3.loc[ Reactor_data_updated_3.Account == '232.1', 'Factory Equipment Cost']))  

            

            Reactor_data_updated_4 = update_high_level_costs(db)
            Reactor_data_updated_4_ = pd.DataFrame()
            Reactor_data_updated_4_ = Reactor_data_updated_4[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                            'Site Material Cost']].copy()

            Reactor_data_updated_4_pretty = prettify(Reactor_data_updated_4_, "Reactor-FOAK Capital Cost Summary - Updated ", 'no_subsidies')
            Reactor_data_updated_4_pretty


            # ### Section 3-5 : Reworking and labor productivity

            # In[12]:


            #Reworking = f(AE, CE, design completion)

            if reactor_type == "SFR":
                reworking_factor =  (-0.75*design_completion+ 1.75) * (-0.15*ae_exp+1.3) * (-0.15*ce_exp+1.3) 

            if reactor_type == "HTGR":
                reworking_factor =  (-0.56*design_completion+ 1.56) * (-0.125*ae_exp+1.25) * (-0.125*ce_exp+1.25) 

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


            # update the construction duration

            Reactor_data_updated_5 = update_high_level_costs(db)
            Reactor_data_updated_5_ = pd.DataFrame()
            Reactor_data_updated_5_ = Reactor_data_updated_5[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                            'Site Material Cost']].copy()

            Reactor_data_updated_5_pretty = prettify(Reactor_data_updated_5_, "Reactor-FOAK Capital Cost Summary - Updated ", 'no_subsidies')
            Reactor_data_updated_5_pretty


            # ### Section 3-6 :Update construction duration from labor hours

            # In[13]:


            #sum of labor hours for Account 20 in the initial estimation (well exectued scenario)
            sum_old_lab_hrs = (Reactor_data_0.loc[Reactor_data_0.Account == 21, 'Site Labor Hours']).values +\
            (Reactor_data_0.loc[Reactor_data_0.Account == 22, 'Site Labor Hours']).values +\
            (Reactor_data_0.loc[Reactor_data_0.Account == 23, 'Site Labor Hours']).values+\
            (Reactor_data_0.loc[Reactor_data_0.Account == 24, 'Site Labor Hours']).values+\
            (Reactor_data_0.loc[Reactor_data_0.Account == 26, 'Site Labor Hours']).values



            # #sum of labor hours for Account 20 in the new estimation 
            sum_new_lab_hrs = (db.loc[db.Account == 21, 'Site Labor Hours']).values +\
            (db.loc[db.Account == 22, 'Site Labor Hours']).values +\
            (db.loc[db.Account == 23, 'Site Labor Hours']).values+\
            (db.loc[db.Account == 24, 'Site Labor Hours']).values+\
            (db.loc[db.Account == 26, 'Site Labor Hours']).values



            # # # change in labor hours for account 20
            labor_hour_ratio = (sum_new_lab_hrs)/sum_old_lab_hrs   # note that this number can be positive or negative
            labor_hour_ratio 

            # 	From the literature   we know that if labor hours changed from 3.8M hours to 20.5M hours (5.4 times), the construction duration changes from 33.2 months to 74.3 months (2.2 times).
            # 	We also know that if the labor hours multiplier =1, the cons duration multiplier should be 1.
            # 	Using these two points: 

            # construction duration multiplier = 0.3 * the labor hours multiplier+0.7

            actual_construction_duration = baseline_construction_duration*(0.3*labor_hour_ratio+0.7)


            # ### Section 3-7 supply chain delays

            # In[14]:


            # For the accounts 21, 22, 23, 24, 25, 26, 
            # The delays are D_21,D_22,D_23,D_24,D_25,D_26 
            # The tasks lengths (in months) are B_21,B_22,B_23,B_24,B_25,B_26

            # task length ratio between SFR and HTGR is 100/65
            # We use this ratio to convert SFR to HTGT task lengths

            if reactor_type == "SFR":
                task_length_multiplier = 1
            elif reactor_type == "HTGR": 
                task_length_multiplier = 100/64
            B_21 =  42.1 * task_length_multiplier # months 
            B_22 = 60.2 * task_length_multiplier
            B_23 = 14.8 * task_length_multiplier
            B_24 = 3.6* task_length_multiplier
            B_25 = 10.1* task_length_multiplier
            B_26 = 43.9* task_length_multiplier


            # The delays are 
            D_21 =  accounts_vars["Supply Chain Delay (monthhs)"].values[0]
            D_22 =  accounts_vars["Supply Chain Delay (monthhs)"].values[1]
            D_23 =  accounts_vars["Supply Chain Delay (monthhs)"].values[2]
            D_24 =  accounts_vars["Supply Chain Delay (monthhs)"].values[3]
            D_25 =  accounts_vars["Supply Chain Delay (monthhs)"].values[4]
            D_26 =  accounts_vars["Supply Chain Delay (monthhs)"].values[5]


            # The tasks completion times (in months) are T_21,T_22,T_23,T_24,T_25,T_26
            T_21 = B_21 + D_21 
            T_22 = 0.09*(B_21+D_21)  +B_22+D_22
            T_23 = 0.24*(B_21+D_21)  +B_23+D_23
            T_24 = 0.24*(B_21+D_21) + 0.34*(B_23+D_23)  +B_24+D_24
            T_25 = 0.18*(B_21+D_21)  +B_25+D_25
            T_26 = 0.21*(B_21+D_21)   +B_26+D_26
            T_end = max(T_21, T_22, T_23, T_24, T_25, T_26)
            T_end
            supply_chain_delay = max( T_end - baseline_construction_duration, 0)
            final_construction_duration = actual_construction_duration + supply_chain_delay
            # print("\nThe actual construction duration is estimated to be : ", np.round(final_construction_duration[0] ,1), "months\n") 


            # ### Section 3-8 Learning by doing and standardization

            # In[15]:


            # # Creating the table for the learning rates
            # #These rates are from KS-TIMCAT results.
            # # The learning rates are multiplied by the standardization divded by 0.7 (since the standatization of PWRs was 0.7)
            fitted_LR = pd.DataFrame()
            fitted_LR.loc[:, 'Account'] = Reactor_data.loc[:, 'Account']
            fitted_LR.loc[:, 'Title'] = Reactor_data.loc[:, 'Title']
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


                
            

            Reactor_data_updated_6 = update_high_level_costs(db)
            Reactor_data_updated_6_ = pd.DataFrame()
            Reactor_data_updated_6_ = Reactor_data_updated_6[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                            'Site Material Cost']].copy()

            Reactor_data_updated_6_pretty = prettify(Reactor_data_updated_6_, "Reactor-FOAK Capital Cost Summary - Updated ", 'no_subsidies')
            Reactor_data_updated_6_pretty


            # ### Section 3-9 Calculate the Indirect Cost and the standardization impact

            # In[16]:


            #   I use here the indirect cost correlations prepared by Jia

            # When the standardization is  100%, the engineering service accound (Acct 35) is zero, 
            # When the standardization is  70%, the engineering service accound (Acct 35) does not change
            # The account 35 multiplier is


            factor_35 = -3.33 * standardization + 3.331


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

            db.loc[db.Account == 33, 'Total Cost (USD)'] =  0.042 * (db.loc[db.Account == 32, 'Total Cost (USD)'].values[0] )

            db.loc[db.Account == 34, 'Total Cost (USD)'] =  0.0035 * (db.loc[db.Account == 32, 'Total Cost (USD)'].values[0] )

            db.loc[db.Account == 35, 'Total Cost (USD)'] = ( 0.27 * (db.loc[db.Account == 32, 'Total Cost (USD)'].values[0] ))*factor_35 






            Reactor_data_updated_7 = update_high_level_costs(db)
            Reactor_data_updated_7_ = pd.DataFrame()
            Reactor_data_updated_7_ = Reactor_data_updated_7[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                            'Site Material Cost']].copy()

            Reactor_data_updated_7_pretty = prettify(Reactor_data_updated_7_, "Reactor-FOAK Capital Cost Summary - Updated ", 'no_subsidies')
            Reactor_data_updated_7_pretty


            # ### Section 3-7 :  Insurance

            # In[17]:


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

            Reactor_data_updated_8 = update_high_level_costs(db)

            Reactor_data_updated_8_ = pd.DataFrame()
            Reactor_data_updated_8_ = Reactor_data_updated_8[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                            'Site Material Cost']].copy()

            Reactor_data_updated_8_pretty = prettify(Reactor_data_updated_8_, "Reactor-FOAK Capital Cost Summary - Updated ", 'no_subsidies')
            Reactor_data_updated_8_pretty


            # ### Section 3-6 :  Interest

            # In[18]:


            # Read the ref spending curve
            sp = pd.read_excel('SFR_HTGR_data.xlsx', sheet_name = "Ref Spending Curve", nrows= 104, usecols='A : D')
            Months = sp['Month'].tolist()
            CDFs  = sp['CDF'].tolist()

            annual_periods = np.linspace(12, 12*int(final_construction_duration/12),int(final_construction_duration/12))
            if max(annual_periods) < int(final_construction_duration)-1: 
                annual_periods_1= np.append( annual_periods, int(final_construction_duration)-1)
            else:
                annual_periods_1= annual_periods


            annual_cum_spend = []
            for period in annual_periods_1:
                new_period = 103*period/int(final_construction_duration)
                annual_cum_spend.append(np.interp(new_period, Months, CDFs))
                
            annual_cum_spend1 = np.append(annual_cum_spend[0], np.diff(annual_cum_spend ))
            tot_overnight_cost = (Reactor_data_updated_8.loc[Reactor_data_updated_8.Title == 'Total Overnight Cost (Accounts 10 to 50)' , 'Total Cost (USD)']).values[0]


            annual_loan_add =  annual_cum_spend1 *tot_overnight_cost

            interest_exp = ((1+interest_rate)**((final_construction_duration -annual_periods_1)/12)) * annual_loan_add - annual_loan_add

            tot_int_exp_construction = sum(interest_exp )

            int_exp_startup = (tot_int_exp_construction + tot_overnight_cost)*((1+interest_rate)**(startup/12))-(tot_int_exp_construction + tot_overnight_cost)



            db = pd.DataFrame()

            db = Reactor_data_updated_8[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                            'Site Material Cost']].copy()
            db.loc[db.Account == 62, 'Total Cost (USD)'] = None # clear old values

            (db.loc[db.Account == 62, 'Total Cost (USD)']) = int_exp_startup +tot_int_exp_construction 


            Reactor_data_updated_9 = update_high_level_costs(db)

            Reactor_data_updated_9_ = pd.DataFrame()
            Reactor_data_updated_9_ = Reactor_data_updated_9[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                            'Site Material Cost']].copy()

            Reactor_data_updated_9_pretty = prettify(Reactor_data_updated_9_, "Reactor-FOAK Capital Cost Summary - Updated ", 'no_subsidies')
            Reactor_data_updated_9_pretty


            # ### Section 3 - 8 :  ITC Subsidies

            # In[19]:


            db1 = pd.DataFrame()
            db1 = Reactor_data_updated_9[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                            'Site Material Cost']].copy()

            ITC_cost_reduction_factor = 0.9387*ITC- 0.0046

            ITC_reduced_OCC = tot_overnight_cost - tot_overnight_cost*ITC_cost_reduction_factor



            tot_cap_investment = db.loc[db.Title =='Total Capital Investment Cost (All Accounts)', 'Total Cost (USD)'].values



            db1.loc[db1.Title== 'Total Capital Investment Cost - ITC reduced', 'Total Cost (USD)'] = None # clear old values
            db1.loc[db1.Title== 'Total Capital Investment Cost - ITC reduced (US$/kWe)', 'Total Cost (USD)'] = None


            db1.loc[db1.Title== 'Total Capital Investment Cost - ITC reduced', 'Total Cost (USD)'] = tot_cap_investment - tot_overnight_cost*ITC_cost_reduction_factor
            
            db1.loc[db1.Title== 'Total Capital Investment Cost - ITC reduced (US$/kWe)', 'Total Cost (USD)'] = (db1.loc[db1.Title== 'Total Capital Investment Cost - ITC reduced', 'Total Cost (USD)'].values[0])/reactor_power


            Reactor_data_updated_10 = update_high_level_costs(db1)

            Reactor_data_updated_10_ = pd.DataFrame()
            Reactor_data_updated_10_ = Reactor_data_updated_10[['Account', 'Title', 'Total Cost (USD)', 'Factory Equipment Cost', 'Site Labor Hours', 'Site Labor Cost',\
                            'Site Material Cost']].copy()

            Reactor_data_updated_10_pretty = prettify(Reactor_data_updated_10_, "Reactor-FOAK Capital Cost Summary - Updated ", 'subsidies')
            Reactor_data_updated_10_pretty

            
            OCC_list.append(ITC_reduced_OCC/reactor_power)
            TCI_list.append((tot_cap_investment - tot_overnight_cost*ITC_cost_reduction_factor)/reactor_power)
        avg_OCC = np.mean(OCC_list)
        avg_TCI = np.mean(TCI_list)
        OCC_EPC_list.append(avg_OCC)
        TCI_EPC_list.append(avg_TCI)
        EPC_list.append(epc_exp)
        print(epc_exp)
    if reactor_type == "SFR":
        OCC_EPC_list_SFR = OCC_EPC_list
        TCI_EPC_list_SFR = TCI_EPC_list
        #  plt.bar(EPC_list, OCC_EPC_list,0.4)
        # g= sns.barplot(x=EPC_list, y=OCC_EPC_list)# linestyle='-', marker='o', markersize=8, label=reactor_type, color='blue') 
        # g.set_xticks(range(1,22,2))
    else:  
        OCC_EPC_list_HTGR = OCC_EPC_list
        TCI_EPC_list_HTGR = TCI_EPC_list
        # g= sns.barplot(x=EPC_list, y=OCC_EPC_list)# linestyle='-', marker='o', markersize=8, label=reactor_type, color='red') 
        # g.set_xticks(range(1,22,2))

    # if reactor_type == "SFR":
    #     g= sns.lineplot(x=epc_exp, y=TCI_N_list, linestyle='-', marker='o', markersize=8, label=reactor_type, color='blue') 
    #     g.set_xticks(range(1,22,2))
    # else:    
    #     g= sns.lineplot(x=epc_exp, y=TCI_N_list, linestyle='-', marker='o', markersize=8, label=reactor_type, color='red') 
    #     g.set_xticks(range(1,22,2))


# plt.ylabel('Fleet-Averaged OCC (2022$/kWe)', fontsize='25') # x-axis name
# plt.legend(loc='upper right', fontsize='25') # Add a legend
# plt.ylim(0, 8000)




#     # In[ ]:
xx = np.arange(5) 
plt.bar( xx , TCI_EPC_list_SFR ,0.3)
plt.bar(xx + 0.3 , TCI_EPC_list_HTGR,0.3)
plt.xlabel('EPC Experience', fontsize='25') # x-axis name
plt.ylabel('Fleet-Averaged TCI (2022$/kWe)', fontsize='25') # x-axis name

plt.xticks(xx, ['Very Low', 'Low', 'Medium', 'High', 'Very High'])

plt.tick_params(labelsize=25)
plt.legend(["SFR" , "HTGR"], fontsize='25')
plt.savefig('EPC_TCI.png')
plt.show() # Display the graph


