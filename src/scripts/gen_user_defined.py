import pandas as pd
import sys
import os
import warnings




def detect_delimiter(file_path):
    """
    Detects the delimiter used in a CSV file by reading the first line.
    """
    try:
        with open(file_path
                    , 'r', encoding='utf-8-sig') as f:
                first_line = f.readline()
                if ',' in first_line:
                    return ','
                elif '\t' in first_line:
                    return '\t'
                else:
                    return ','
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1)

def get_total_direct_cost():
    """
    Prompts the user to input the total direct cost.
    If no input is provided, returns the default value of 1,000,000,000.
    """
    try:
        user_input = input("Enter the total direct cost (press Enter to use default 1,000,000,000): ").strip()
        if user_input == "":
            return 1000000000
        else:
            # Remove commas and convert to integer
            return int(user_input.replace(",", ""))
    except ValueError:
        print("Invalid input. Please enter a numerical value.")
        sys.exit(1)

# generate from raw_account.csv to user_defined_account.csv and raw_variable.csv
def process_account_csv(raw_csv_path, 
                        user_defined_csv_path, 
                        total_direct_cost, delimiter=','):
    """
    Reads the raw CSV, processes it, and writes to the user-defined CSV using Pandas.
    """
    try:
        # Attempt to read the raw CSV with the specified delimiter and UTF-8 encoding with BOM handling
        df = pd.read_csv(raw_csv_path, delimiter=delimiter, dtype=str, encoding='utf-8-sig', engine='python')
        print(f"Successfully read the raw CSV with delimiter '{delimiter}'.")
    except FileNotFoundError:
        print(f"Error: The file '{raw_csv_path}' was not found.")
        sys.exit(1)
    except pd.errors.ParserError as e:
        print(f"Error parsing '{raw_csv_path}' with delimiter '{delimiter}': {e}")
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"Encoding error while reading '{raw_csv_path}': {e}")
        sys.exit(1)

    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.lower()
 
    # Check if 'ind' column exists
    if 'ind' not in df.columns:
        print("Error: The 'ind' column is missing from the CSV. Please check the column names.")
        sys.exit(1)

    # Convert numerical columns to appropriate types
    numerical_columns = ['ind', 'total_cost', 'level']
    for col in numerical_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            print(f"Converted column '{col}' to numeric.")

    # Calculate prn
    df['prn'] = df['total_cost'] / total_direct_cost
    # Round prn to two decimal places
    df['prn'] = df['prn'].round(2)
    # Add review_status column
    df['review_status'] = "Unchanged"

    # Reorder and select the necessary columns
    # Define the desired column order
    desired_columns = [
        'ind',
        'code_of_account',
        'account_description',
        'total_cost',
        'level',
        'supaccount',
        'review_status',
        'prn',
        'alg_name',
        'fun_unit',
        'variables'
    ]

    # Ensure all desired columns are present
    for col in desired_columns:
        if col not in df.columns:
            df[col] = ""
            print(f"Added missing column '{col}' with empty values.")

    # Select and reorder the columns
    df_final = df[desired_columns]
    print("Selected and reordered the columns.")
    # Handle NaN values by replacing them with empty strings
    df_final = df_final.fillna('')
    print("Replaced NaN values with empty strings.")
    # Save to user_defined.csv with comma delimiter
    df_final.to_csv(user_defined_csv_path, index=False)
    print(f"Successfully generated '{user_defined_csv_path}' with a total direct cost of {total_direct_cost}.")

# generate from user_defined_account.csv to raw_variable.csv
def process_user_defined_csv(user_defined_csv_path, 
                             raw_variable_csv_path):
    """
    Reads the user_defined_account.csv file, extracts unique variables, and writes them to raw_variable.csv
    with 'REQUIRED' in var_value and var_unit columns, leaving other columns blank.
    """
    try:
        # Read the user_defined_account.csv file
        df = pd.read_csv(user_defined_csv_path, dtype=str)
        print(f"Successfully read '{user_defined_csv_path}'.")
    except FileNotFoundError:
        print(f"Error: The file '{user_defined_csv_path}' was not found.")
        sys.exit(1)
    except pd.errors.ParserError as e:
        print(f"Error parsing '{user_defined_csv_path}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while reading '{user_defined_csv_path}': {e}")
        sys.exit(1)
    
    # Ensure 'variables' column exists
    if 'variables' not in df.columns:
        print("Error: The 'variables' column is missing from the CSV. Please check the column names.")
        sys.exit(1)
    
    # Extract all variables from the 'variables' column
    variables_series = df['variables'].dropna().astype(str)
    all_variables = variables_series.apply(lambda x: [var.strip() for var in x.split(',') if var.strip() != ''])
    unique_variables = sorted(set(var for sublist in all_variables for var in sublist))
    
    print(f"Extracted {len(unique_variables)} unique variables from '{user_defined_csv_path}'.")
    
    # Create a list of dictionaries for the new DataFrame
    raw_variable_data = []
    for idx, var in enumerate(unique_variables, start=1):
        raw_variable_data.append({
            'ind': idx,
            'var_name': var,
            'var_value': 'REQUIRED',
            'var_unit': 'REQUIRED',
            'var_alg': '',
            'var_need': '',
            'v_linked': ''
        })
    
    # Create the raw_variable DataFrame
    raw_variable_df = pd.DataFrame(raw_variable_data, columns=[
        'ind',
        'var_name',
        'var_value',
        'var_unit',
        'var_alg',
        'var_need',
        'v_linked'
    ])
    
    # Save the DataFrame to raw_variable.csv
    try:
        raw_variable_df.to_csv(raw_variable_csv_path, index=False)
        print(f"Successfully generated '{raw_variable_csv_path}'.")
    except Exception as e:
        print(f"An error occurred while writing to '{raw_variable_csv_path}': {e}")
        sys.exit(1)

# generate from raw_variable.csv to user_defined_variable.csv
def transform_raw_variable(raw_variable_filled_path, 
                           user_defined_variable_path):
    """
    Transforms raw_variable_filled.csv into user_defined_variable.csv by adding
    var_description and user_input columns.

    Parameters:
    - raw_variable_filled_path: Path to the input raw_variable_filled.csv file.
    - user_defined_variable_path: Path where the output user_defined_variable.csv will be saved.
    """
    # Check if the input file exists
    if not os.path.isfile(raw_variable_filled_path):
        print(f"Error: The file '{raw_variable_filled_path}' does not exist.")
        sys.exit(1)
    
    try:
        # Read the raw_variable_filled.csv file
        df = pd.read_csv(raw_variable_filled_path, dtype=str)
        print(f"Successfully read '{raw_variable_filled_path}'.")
    except Exception as e:
        print(f"Error reading '{raw_variable_filled_path}': {e}")
        sys.exit(1)
    
    # Verify that required columns exist
    required_columns = ['ind', 'var_name', 'var_value', 'var_unit', 'var_alg', 'var_need', 'v_linked']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: The following required columns are missing in '{raw_variable_filled_path}': {missing_columns}")
        sys.exit(1)
    
    # Generate var_description
    df['var_description'] = df['var_name'].apply(lambda x: f"description of {x} optional")
    
    # Add user_input column with default value 0
    df['user_input'] = 0
    
    # Rearrange columns to the desired order
    desired_columns = ['ind', 'var_name', 'var_description', 'var_value', 'var_unit',
                       'var_alg', 'var_need', 'v_linked', 'user_input']
    
    # Ensure all desired columns are present
    for col in desired_columns:
        if col not in df.columns:
            df[col] = ''  # Fill missing columns with empty strings
    
    df_final = df[desired_columns]
    
    # Save the transformed DataFrame to user_defined_variable.csv
    try:
        df_final.to_csv(user_defined_variable_path, index=False)
        print(f"Successfully generated '{user_defined_variable_path}'.")
    except Exception as e:
        print(f"Error writing to '{user_defined_variable_path}': {e}")
        sys.exit(1)

# generate from user_defined_account.csv and user_defined_variable.csv to user_defined_algorithm.csv
def generate_user_defined_algorithm(user_defined_account_path, 
                                    user_defined_variable_path, 
                                    user_defined_algorithm_path):
    """
    Generates user_defined_algorithm.csv from user_defined_account.csv and user_defined_variable.csv.
    
    Parameters:
    - user_defined_account_path: Path to user_defined_account.csv
    - user_defined_variable_path: Path to user_defined_variable.csv
    - user_defined_algorithm_path: Path to save user_defined_algorithm.csv
    """
    # Check if input files exist
    if not os.path.isfile(user_defined_account_path):
        print(f"Error: The file '{user_defined_account_path}' does not exist.")
        sys.exit(1)
        
    if not os.path.isfile(user_defined_variable_path):
        print(f"Error: The file '{user_defined_variable_path}' does not exist.")
        sys.exit(1)
    
    # Read user_defined_account.csv
    try:
        account_df = pd.read_csv(user_defined_account_path, dtype=str)
        print(f"Successfully read '{user_defined_account_path}'.")
    except Exception as e:
        print(f"Error reading '{user_defined_account_path}': {e}")
        sys.exit(1)
    
    # Read user_defined_variable.csv
    try:
        variable_df = pd.read_csv(user_defined_variable_path, dtype=str)
        print(f"Successfully read '{user_defined_variable_path}'.")
    except Exception as e:
        print(f"Error reading '{user_defined_variable_path}': {e}")
        sys.exit(1)
    
    # Extract alg_name from account_df where alg_name is not empty
    account_alg_df = account_df[['alg_name', 'fun_unit']].dropna(subset=['alg_name'])
    account_alg_df = account_alg_df[account_alg_df['alg_name'].str.strip() != '']
    account_alg_df['alg_name'] = account_alg_df['alg_name'].str.strip()
    account_alg_df['fun_unit'] = account_alg_df['fun_unit'].str.strip()
    
    print(f"Extracted {len(account_alg_df)} algorithms from '{user_defined_account_path}'.")
    
    # Extract var_alg from variable_df where var_alg is not empty
    variable_alg_df = variable_df[['var_alg', 'var_unit']].dropna(subset=['var_alg'])
    variable_alg_df = variable_alg_df[variable_alg_df['var_alg'].str.strip() != '']
    variable_alg_df['var_alg'] = variable_alg_df['var_alg'].str.strip()
    variable_alg_df['var_unit'] = variable_alg_df['var_unit'].str.strip()
    
    print(f"Extracted {len(variable_alg_df)} algorithms from '{user_defined_variable_path}'.")
    
    # Rename columns for consistency
    account_alg_df = account_alg_df.rename(columns={'alg_name': 'alg_name', 'fun_unit': 'alg_units'})
    variable_alg_df = variable_alg_df.rename(columns={'var_alg': 'alg_name', 'var_unit': 'alg_units'})
    
    # Add 'alg_for' column: 'c' for account algorithms, 'v' for variable algorithms
    account_alg_df['alg_for'] = 'c'
    variable_alg_df['alg_for'] = 'v'
    
    # Combine both DataFrames
    combined_alg_df = pd.concat([account_alg_df, variable_alg_df], ignore_index=True)
    
    # Remove duplicates if any
    combined_alg_df = combined_alg_df.drop_duplicates(subset=['alg_name'])
    
    print(f"Total unique algorithms after combining: {len(combined_alg_df)}")
    
    # Sort by alg_name for consistency
    combined_alg_df = combined_alg_df.sort_values(by='alg_name').reset_index(drop=True)
    
    # Assign 'ind' starting from 1
    combined_alg_df.insert(0, 'ind', range(1, len(combined_alg_df) + 1))
    
    # Create 'alg_description', 'alg_python', 'alg_formulation'
    combined_alg_df['alg_description'] = combined_alg_df['alg_name'].apply(lambda x: f"description of {x} optional")
    combined_alg_df['alg_python'] = "user_defined_func"
    combined_alg_df['alg_formulation'] = combined_alg_df['alg_name'].apply(lambda x: f"formulation of {x} optional")
    
    # Reorder columns
    combined_alg_df = combined_alg_df[['ind', 'alg_name', 'alg_for', 'alg_description', 'alg_python', 'alg_formulation', 'alg_units']]
    
    # Save to user_defined_algorithm.csv
    try:
        combined_alg_df.to_csv(user_defined_algorithm_path, index=False)
        print(f"Successfully generated '{user_defined_algorithm_path}'.")
    except Exception as e:
        print(f"Error writing to '{user_defined_algorithm_path}': {e}")
        sys.exit(1)

# generate from user_defined_algorithm.csv, user_defined_account.csv, and user_defined_variable.csv to user_defined_func.py
def generate_user_defined_func(user_defined_algorithm_path, 
                               user_defined_account_path, 
                               user_defined_variable_path, 
                               output_func_path):
    """
    Generates user_defined_func.py based on user_defined_algorithm.csv,
    user_defined_account.csv, and user_defined_variable.csv.

    Parameters:
    - user_defined_algorithm_path: Path to user_defined_algorithm.csv
    - user_defined_account_path: Path to user_defined_account.csv
    - user_defined_variable_path: Path to user_defined_variable.csv
    - output_func_path: Path to save the generated user_defined_func.py
    """
    # Check if input files exist
    for file_path in [user_defined_algorithm_path, user_defined_account_path, user_defined_variable_path]:
        if not os.path.isfile(file_path):
            print(f"Error: The file '{file_path}' does not exist.")
            sys.exit(1)
    
    # Read user_defined_algorithm.csv
    try:
        alg_df = pd.read_csv(user_defined_algorithm_path, dtype=str)
        print(f"Successfully read '{user_defined_algorithm_path}'.")
    except Exception as e:
        print(f"Error reading '{user_defined_algorithm_path}': {e}")
        sys.exit(1)
    
    # Read user_defined_account.csv
    try:
        account_df = pd.read_csv(user_defined_account_path, dtype=str)
        print(f"Successfully read '{user_defined_account_path}'.")
    except Exception as e:
        print(f"Error reading '{user_defined_account_path}': {e}")
        sys.exit(1)
    
    # Read user_defined_variable.csv
    try:
        variable_df = pd.read_csv(user_defined_variable_path, dtype=str)
        print(f"Successfully read '{user_defined_variable_path}'.")
    except Exception as e:
        print(f"Error reading '{user_defined_variable_path}': {e}")
        sys.exit(1)
    
    # Verify that required columns exist in user_defined_algorithm.csv
    required_alg_columns = ['ind', 'alg_name', 'alg_for', 'alg_description', 'alg_python', 'alg_formulation', 'alg_units']
    missing_alg_columns = [col for col in required_alg_columns if col not in alg_df.columns]
    if missing_alg_columns:
        print(f"Error: The following required columns are missing in '{user_defined_algorithm_path}': {missing_alg_columns}")
        sys.exit(1)
    
    # Verify that required columns exist in user_defined_account.csv
    required_acc_columns = ['ind', 'code_of_account', 'account_description', 'total_cost', 'level',
                            'supaccount', 'review_status', 'prn', 'alg_name', 'fun_unit', 'variables']
    missing_acc_columns = [col for col in required_acc_columns if col not in account_df.columns]
    if missing_acc_columns:
        print(f"Error: The following required columns are missing in '{user_defined_account_path}': {missing_acc_columns}")
        sys.exit(1)
    
    # Verify that required columns exist in user_defined_variable.csv
    required_var_columns = ['ind', 'var_name', 'var_description', 'var_value', 'var_unit', 'var_alg', 'var_need', 'v_linked', 'user_input']
    missing_var_columns = [col for col in required_var_columns if col not in variable_df.columns]
    if missing_var_columns:
        print(f"Error: The following required columns are missing in '{user_defined_variable_path}': {missing_var_columns}")
        sys.exit(1)


    account_alg_names = alg_df['alg_name'].dropna().unique()
    # I keep getting the SettingWithCopyWarning from pandas, so just make a copy to avoid it
    # Filter account_df for rows where alg_name is in account_alg_names and make a copy
    account_alg_df = account_df[account_df['alg_name'].isin(account_alg_names)].copy()
    account_alg_df.loc[:, 'alg_name'] = account_alg_df['alg_name'].str.strip()
    account_alg_df.loc[:, 'variables'] = account_alg_df['variables'].fillna('').str.strip()
    
    account_alg_vars_dict = {}
    for _, row in account_alg_df.iterrows():
        alg_name = row['alg_name']
        variables = row['variables']
        if variables:
            vars_list = [var.strip() for var in variables.split(',') if var.strip()]
        else:
            vars_list = []
        account_alg_vars_dict[alg_name] = vars_list
    
    print("Mapping of account algorithms to variables:")
    for alg, vars in account_alg_vars_dict.items():
        print(f"  {alg}: {vars}")
    
    # Create a mapping from var_alg to variables for variable algorithms (alg_for = 'v')
    variable_alg_df = variable_df[variable_df['var_alg'].notna() & (variable_df['var_alg'].str.strip() != '')]
    # same here, make a copy to avoid the SettingWithCopyWarning
    variable_alg_df = variable_alg_df.copy()
    variable_alg_df.loc[:,'var_alg'] = variable_alg_df['var_alg'].str.strip()
    variable_alg_df.loc[:,'var_need'] = variable_alg_df['var_need'].fillna('').str.strip()
    
    variable_alg_vars_dict = {}
    for _, row in variable_alg_df.iterrows():
        alg_name = row['var_alg']
        v_linked = row['var_need']
        if v_linked:
            vars_list = [var.strip() for var in v_linked.split(',') if var.strip()]
        else:
            vars_list = []
        variable_alg_vars_dict[alg_name] = vars_list
    
    print("Mapping of variable algorithms to variables:")
    for alg, vars in variable_alg_vars_dict.items():
        print(f"  {alg}: {vars}")
    
    # Combine both dictionaries
    combined_alg_vars = {}
    # Add account algorithms
    for alg_name, vars_list in account_alg_vars_dict.items():
        combined_alg_vars[alg_name] = vars_list
    # Add variable algorithms
    for alg_name, vars_list in variable_alg_vars_dict.items():
        if alg_name in combined_alg_vars:
            # If alg_name exists in both, combine the variable lists without duplicates
            combined_alg_vars[alg_name].extend(vars_list)
            combined_alg_vars[alg_name] = list(dict.fromkeys(combined_alg_vars[alg_name]))
        else:
            combined_alg_vars[alg_name] = vars_list
    
    print(f"Total unique algorithms after combining: {len(combined_alg_vars)}")
    
    # Start building the content of user_defined_func.py
    func_content = """import numpy as np
from .Algorithm import Algorithm

class user_defined_func(Algorithm):
    def __init__(self, ind, alg_name, alg_for, alg_description, alg_formulation, alg_units, variables, constants):
        super().__init__(ind, alg_name, alg_for, alg_description, alg_formulation, alg_units, variables, constants)
    
    def run(self, inputs: dict) -> float:
        \"\"\"
        Executes the algorithm specified by the name in the instance variables.
        
        Parameters:
        inputs (dict): Dictionary of input variables required for the algorithm.

        Returns:
        float: Result of the algorithm computation.
        \"\"\"
        # run the algorithm using self.name not self.alg_name
        return self._run_algorithm(self.name, [inputs[var.strip()] for var in self.variables.split(",") if var.strip()])
    
    def _run_algorithm(self, alg_name: str, variables: list) -> float:
        \"\"\"
        Runs the specified algorithm with given variables.
        
        Parameters:
        alg_name (str): The name of the algorithm to run.
        variables (list): List of input variables for the algorithm.

        Returns:
        float: Result of the algorithm computation.
        \"\"\"
        try:
            algorithm = getattr(self, alg_name)
            return algorithm(*variables)
        except AttributeError:
            raise ValueError(f"Algorithm {{alg_name}} not found")
"""

    # Iterate over each algorithm and create a static method with appropriate parameters
    for alg_name, vars_list in combined_alg_vars.items():
        alg_row = alg_df[alg_df['alg_name'].str.strip() == alg_name]
        if not alg_row.empty:
            alg_description = alg_row.iloc[0]['alg_description'].strip()
        else:
            alg_description = "No description provided"
        
        params = ', '.join(vars_list)
        
        # Create the function definition with placeholder
        function_def = f"""    
    @staticmethod
    # {alg_name}: {alg_description}
    def {alg_name}({params}):
        # TODO: Implement the logic for {alg_name}
        # The output unit should be {alg_row.iloc[0]['alg_units']}
        pass
"""
        func_content += function_def

    # Write the content to user_defined_func.py
    try:
        with open(output_func_path, 'w') as f:
            f.write(func_content)
        print(f"Successfully generated '{output_func_path}'.")
    except Exception as e:
        print(f"Error writing to '{output_func_path}': {e}")
        sys.exit(1)

# generate from user_defined_account.csv user_defined_variable.csv and user_defined_algorithm.csv to user_defined.sql
def escape_sql_string(value):
    """
    Escapes single quotes in SQL string literals by replacing them with two single quotes.
    """
    if isinstance(value, str):
        return value.replace("'", "''")
    return value

def format_sql_value(value, dtype):
    """
    Formats the value based on its data type for SQL insertion.
    - Strings are enclosed in single quotes and escaped.
    - Numbers are left as-is.
    - Empty strings or NaN are converted to NULL.
    """
    if pd.isna(value) or (isinstance(value, str) and value.strip() == ''):
        return 'NULL'
    if dtype in ['int', 'double']:
        return str(value)
    elif dtype.startswith('varchar') or dtype.startswith('text'):
        return f"'{escape_sql_string(str(value))}'"
    else:
        # Default to string if unknown type
        return f"'{escape_sql_string(str(value))}'"

def generate_create_table_statement(table_name, columns, primary_key):
    """
    Generates a CREATE TABLE SQL statement.
    
    Parameters:
    - table_name: Name of the table.
    - columns: List of tuples (column_name, data_type).
    - primary_key: Column name to be set as PRIMARY KEY.
    
    Returns:
    - A string containing the CREATE TABLE SQL statement.
    """
    create_stmt = f"DROP TABLE IF EXISTS `{table_name}`;\n"
    create_stmt += f"CREATE TABLE `{table_name}` (\n"
    column_defs = []
    for col_name, data_type in columns:
        column_def = f"  `{col_name}` {data_type}"
        # Define NOT NULL for primary key
        if col_name == primary_key:
            column_def += " NOT NULL"
        else:
            column_def += " DEFAULT NULL"
        column_defs.append(column_def)
    create_stmt += ",\n".join(column_defs)
    create_stmt += f",\n  PRIMARY KEY (`{primary_key}`)\n"
    create_stmt += ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;\n"
    return create_stmt

def generate_insert_statement(table_name, df, columns, dtypes):
    """
    Generates an INSERT INTO SQL statement for the given DataFrame.
    
    Parameters:
    - table_name: Name of the table.
    - df: Pandas DataFrame containing the data.
    - columns: List of column names in the table.
    - dtypes: Dictionary mapping column names to their data types.
    
    Returns:
    - A string containing the INSERT INTO SQL statement.
    """
    insert_stmt = f"LOCK TABLES `{table_name}` WRITE;\n"
    insert_stmt += f"INSERT INTO `{table_name}` ({', '.join([f'`{col}`' for col in columns])}) VALUES \n"
    values_list = []
    for _, row in df.iterrows():
        formatted_values = []
        for col in columns:
            dtype = dtypes[col]
            value = row[col] if col in row else None
            formatted_value = format_sql_value(value, dtype)
            formatted_values.append(formatted_value)
        values_str = f"({', '.join(formatted_values)})"
        values_list.append(values_str)
    insert_stmt += ",\n".join(values_list)
    insert_stmt += ";\n"
    insert_stmt += f"UNLOCK TABLES;\n\n"
    return insert_stmt

def generate_user_defined_sql(user_defined_algorithm_path, 
                              user_defined_account_path, 
                              user_defined_variable_path, 
                              output_sql_path):
    """
    Generates user_defined.sql based on user_defined_algorithm.csv,
    user_defined_account.csv, and user_defined_variable.csv.

    Parameters:
    - user_defined_algorithm_path: Path to user_defined_algorithm.csv
    - user_defined_account_path: Path to user_defined_account.csv
    - user_defined_variable_path: Path to user_defined_variable.csv
    - output_sql_path: Path to save the generated user_defined.sql
    """
    # Check if input files exist
    for file_path in [user_defined_algorithm_path, user_defined_account_path, user_defined_variable_path]:
        if not os.path.isfile(file_path):
            print(f"Error: The file '{file_path}' does not exist.")
            sys.exit(1)
    
    # Read CSV files
    try:
        alg_df = pd.read_csv(user_defined_algorithm_path, dtype=str)
        print(f"Successfully read '{user_defined_algorithm_path}'.")
    except Exception as e:
        print(f"Error reading '{user_defined_algorithm_path}': {e}")
        sys.exit(1)
    
    try:
        account_df = pd.read_csv(user_defined_account_path, dtype=str)
        print(f"Successfully read '{user_defined_account_path}'.")
    except Exception as e:
        print(f"Error reading '{user_defined_account_path}': {e}")
        sys.exit(1)
    
    try:
        variable_df = pd.read_csv(user_defined_variable_path, dtype=str)
        print(f"Successfully read '{user_defined_variable_path}'.")
    except Exception as e:
        print(f"Error reading '{user_defined_variable_path}': {e}")
        sys.exit(1)
    
    # Define table schemas
    tables = {
        'user_defined_account': {
            'columns': [
                ('ind', 'int'),
                ('code_of_account', 'varchar(20)'),
                ('account_description', 'text'),
                ('total_cost', 'double'),
                ('level', 'int'),
                ('supaccount', 'text'),
                ('review_status', 'text'),
                ('prn', 'double'),
                ('alg_name', 'text'),
                ('fun_unit', 'text'),
                ('variables', 'text')
            ],
            'primary_key': 'code_of_account',
            'data': account_df
        },
        'user_defined_algorithm': {
            'columns': [
                ('ind', 'int'),
                ('alg_name', 'varchar(50)'),
                ('alg_for', 'text'),
                ('alg_description', 'text'),
                ('alg_python', 'text'),
                ('alg_formulation', 'text'),
                ('alg_units', 'text')
            ],
            'primary_key': 'alg_name',
            'data': alg_df
        },
        'user_defined_variable': {
            'columns': [
                ('ind', 'int'),
                ('var_name', 'varchar(20)'),
                ('var_description', 'text'),
                ('var_value', 'double'),
                ('var_unit', 'text'),
                ('var_alg', 'text'),
                ('var_need', 'text'),
                ('v_linked', 'text'),
                ('user_input', 'int')
            ],
            'primary_key': 'var_name',
            'data': variable_df
        }
    }
    
    # Begin constructing the SQL script
    sql_script = ""
    sql_script += "CREATE DATABASE IF NOT EXISTS `accert_db`;\n"
    sql_script += "USE `accert_db`;\n\n"
    
    for table_name, table_info in tables.items():
        columns, primary_key, df = table_info['columns'], table_info['primary_key'], table_info['data']
        
        # Generate CREATE TABLE statement
        create_table_stmt = generate_create_table_statement(table_name, columns, primary_key)
        sql_script += create_table_stmt + "\n"
        
        # Prepare data types dictionary
        dtypes = {col: dtype for col, dtype in columns}
        
        # Generate INSERT INTO statement
        insert_stmt = generate_insert_statement(table_name, df, [col for col, _ in columns], dtypes)
        sql_script += insert_stmt
    
    # Write to the output SQL file
    try:
        with open(output_sql_path, 'w', encoding='utf-8') as f:
            f.write(sql_script)
        print(f"Successfully generated '{output_sql_path}'.")
    except Exception as e:
        print(f"Error writing to '{output_sql_path}': {e}")
        sys.exit(1)

def main():
    '''
    prompt user to choose the process to run
    '''
    # there should be 4 main files needed user_defined_account.csv, user_defined_variable.csv, 
    # user_defined_algorithm.csv, user_defined_func.py
    # if all the files are present, then the next process is to generate user_defined.sql
    # if user_defined_account.csv and user_defined_variable.csv and user_defined_algorithm.csv 
    # are present without user_defined_func.py then the next process is to generate user_defined_func.py
    # if user_defined_account.csv and user_defined_variable.csv are present without user_defined_algorithm.csv
    # then the next process is to generate user_defined_algorithm.csv
    # if user_defined_account.csv is present without user_defined_variable.csv then the next process is to generate
    # raw_variable.csv from user_defined_account.csv and ask the user to fill the raw_variable.csv then generate
    # user_defined_variable.csv

    # check if user_defined_account.csv is present
    if not os.path.isfile('user_defined_account.csv'):
        print("user_defined_account.csv is missing")
        # check if raw_account.csv is present
        if not os.path.isfile('raw_account.csv'):
            print("raw_account.csv is missing")
            sys.exit(1)
        else:
            print("raw_account.csv is present")
            # generate user_defined_account.csv from raw_account.csv
            process_account_csv('raw_account.csv', 'user_defined_account.csv', 1000000000, delimiter=',')
            print("user_defined_account.csv generated")
            raw_variable_csv = 'raw_variable_automated_generated.csv'
            process_user_defined_csv('user_defined_account.csv', raw_variable_csv)
            print("raw_variable.csv generated, please fill the raw_variable.csv")
    else:
        print("user_defined_account.csv is present")
    # check if user_defined_variable.csv is present
    if not os.path.isfile('user_defined_variable.csv'):
        print("user_defined_variable.csv is missing")
        # check if raw_variable.csv is present
        if not os.path.isfile('raw_variable.csv'):
            print("raw_variable.csv is missing")
            sys.exit(1)
        else:
            print("raw_variable.csv is present")
            # generate user_defined_variable.csv from raw_variable.csv
            transform_raw_variable('raw_variable.csv', 'user_defined_variable.csv')
    else:
        print("user_defined_variable.csv is present")
    # check if user_defined_algorithm.csv is present
    if not os.path.isfile('user_defined_algorithm.csv'):
        print("user_defined_algorithm.csv is missing")
        generate_user_defined_algorithm('user_defined_account.csv', 
                                        'user_defined_variable.csv', 
                                        'user_defined_algorithm.csv')
    else:
        print("user_defined_algorithm.csv is present")
    # check if user_defined_func.py is present
    if not os.path.isfile('user_defined_func.py'):
        print("user_defined_func.py is missing")
        generate_user_defined_func('user_defined_algorithm.csv', 
                                   'user_defined_account.csv', 
                                   'user_defined_variable.csv', 
                                   'user_defined_func.py')
    else:
        print("user_defined_func.py is present")
    # check if user_defined.sql is present
    if not os.path.isfile('user_defined.sql'):
        print("user_defined.sql is missing")
        generate_user_defined_sql('user_defined_algorithm.csv', 
                                  'user_defined_account.csv', 
                                  'user_defined_variable.csv', 
                                  'user_defined.sql')
    else:
        print("user_defined.sql is present")


if __name__ == "__main__":
    main()






