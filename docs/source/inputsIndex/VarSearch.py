### This python file is used to find any added data from an .csv file, and prints it in a format so that sphinx can
### Automatically generate it.

import pandas as pd

### Insert the .csv file path here
CSVPath = '../tutorial/ref_tables/ABR1000_account.csv'
CSVRead = pd.read_csv(CSVPath)

### Insert the columns you want it to read.
CSVColumns = CSVRead[['ind', 'code_of_account', 'account_description', 'level','supaccount', 'cost_elements']]

### insert the columns in each row[], and if the text is a mix of letters and numbers OR has spaces in it, include quotes.
for idx, row in CSVColumns.iloc[0:102].iterrows():
    print(f"{row['ind']}, {row['code_of_account']}, \"{row['account_description']}\", {row['level']}, {row['supaccount']}, \"{row['cost_elements']}\"")