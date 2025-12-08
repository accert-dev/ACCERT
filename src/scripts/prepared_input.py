# if os.path.isfile('user_defined_func.py') copy it to the src/Algorithms folder
# if user_defined_account.csv and user_defined_variable.csv and user_defined_algorithm.csv 
# are present then collect the names of all accounts, variables and algorithms
# make them into a list and write them to src/etc/accert.sch 

import os
import shutil
import pandas as pd

def copy_user_defined_func(source_path, destination_dir):
    """
    Copies 'user_defined_func.py' to the specified destination directory if it exists.

    Parameters:
    - source_path (str): Path to 'user_defined_func.py'.
    - destination_dir (str): Directory where the file should be copied.
    """
    if os.path.isfile(source_path):
        # Ensure the destination directory exists
        os.makedirs(destination_dir, exist_ok=True)
        # Define the destination path
        destination_path = os.path.join(destination_dir, 'user_defined_func.py')
        # Copy the file
        shutil.copy2(source_path, destination_path)
        print(f"Copied '{source_path}' to '{destination_path}'.")
    else:
        print(f"File '{source_path}' does not exist. Skipping copy.")

def collect_names(account_csv, algorithm_csv, variable_csv):
    """
    Collects names from account, algorithm, and variable CSV files.

    Parameters:
    - account_csv (str): Path to 'user_defined_account.csv'.
    - algorithm_csv (str): Path to 'user_defined_algorithm.csv'.
    - variable_csv (str): Path to 'user_defined_variable.csv'.

    Returns:
    - List[str]: Combined list of names.
    """
    names = ['user_defined']  # Default entry

    # Read user_defined_account.csv
    try:
        account_df = pd.read_csv(account_csv, dtype=str)
        account_codes = account_df['code_of_account'].dropna().unique().tolist()
        names.extend(account_codes)
        print(f"Collected {len(account_codes)} account codes.")
    except Exception as e:
        print(f"Error reading '{account_csv}': {e}")
        return names

    # Read user_defined_algorithm.csv
    try:
        algorithm_df = pd.read_csv(algorithm_csv, dtype=str)
        alg_names = algorithm_df['alg_name'].dropna().unique().tolist()
        names.extend(alg_names)
        print(f"Collected {len(alg_names)} algorithm names.")
    except Exception as e:
        print(f"Error reading '{algorithm_csv}': {e}")
        return names

    # Read user_defined_variable.csv
    try:
        variable_df = pd.read_csv(variable_csv, dtype=str)
        var_names = variable_df['var_name'].dropna().unique().tolist()
        names.extend(var_names)
        print(f"Collected {len(var_names)} variable names.")
    except Exception as e:
        print(f"Error reading '{variable_csv}': {e}")
        return names

    return names

def update_accert_sch(accert_sch_path, user_defined_names):
    """
    Updates the 'user_defined_names' list in 'accert.sch'.

    Parameters:
    - accert_sch_path (str): Path to 'accert.sch'.
    - user_defined_names (List[str]): List of names to insert.
    """
    if not os.path.isfile(accert_sch_path):
        print(f"File '{accert_sch_path}' does not exist. Cannot update 'user_defined_names'.")
        return

    try:
        with open(accert_sch_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        with open(accert_sch_path, 'w', encoding='utf-8') as file:
            for line in lines:
                if line.strip().startswith('user_defined_names ='):
                    # Create the new line with the updated list
                    formatted_names = "', '".join(user_defined_names)
                    new_line = f"user_defined_names = ['{formatted_names}']\n"
                    file.write(new_line)
                    print("Updated 'user_defined_names' in 'accert.sch'.")
                else:
                    file.write(line)
    except Exception as e:
        print(f"Error updating '{accert_sch_path}': {e}")

def main():
    # Define paths
    current_folder = os.path.dirname(os.path.abspath(__file__))
    code_src_folder = os.path.dirname(current_folder)

    algorithms_dir = os.path.join(code_src_folder, 'Algorithm')
    etc_dir = os.path.join(code_src_folder, 'etc')
    accert_sch_path = os.path.join(etc_dir, 'accert.sch')

    account_csv = os.path.join(os.getcwd(), 'user_defined_account.csv')
    algorithm_csv = os.path.join(os.getcwd(), 'user_defined_algorithm.csv')
    variable_csv = os.path.join(os.getcwd(),'user_defined_variable.csv')
    func_source = os.path.join(os.getcwd(), 'user_defined_func.py')

    # Step 1: Copy 'user_defined_func.py' if it exists
    copy_user_defined_func(func_source, algorithms_dir)

    # Step 2: Check for presence of all three CSV files
    if all([os.path.isfile(csv) for csv in [account_csv, algorithm_csv, variable_csv]]):
        print("All required CSV files are present. Proceeding to collect names.")
        # Step 3: Collect names from CSVs
        user_defined_names = collect_names(account_csv, algorithm_csv, variable_csv)
        print(f"Combined list of names ({len(user_defined_names)}): {user_defined_names}")
        # Step 4: Update 'accert.sch' with the new list
        update_accert_sch(accert_sch_path, user_defined_names)
    else:
        missing_files = [csv for csv in [account_csv, algorithm_csv, variable_csv] if not os.path.isfile(csv)]
        print(f"Missing CSV files: {', '.join(missing_files)}. Skipping name collection and 'accert.sch' update.")

if __name__ == "__main__":
    main()
