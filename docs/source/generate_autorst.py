import os
import re

current_dir = os.path.dirname(os.path.abspath(__file__))

toc_file_path = os.path.join(current_dir, 'reference', 'main.rst')
output_dir = os.path.join(current_dir, 'reference')

def clean_output_directory(directory):
    """
    Removes all .rst files in the specified directory to clean up old documentation.
    """
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith('.rst'):
                file_path = os.path.join(directory, filename)
                os.remove(file_path)
                print(f'Removed old RST file: {file_path}')
    else:
        os.makedirs(directory, exist_ok=True)
        print(f'Created output directory: {directory}')


# remove the old toctree file if it exists
if os.path.exists(toc_file_path):
    os.remove(toc_file_path)
# remove the old rst files in the output directory/main and output directory/utility
clean_output_directory(os.path.join(output_dir, 'main'))
clean_output_directory(os.path.join(output_dir, 'utility'))
# create a new toctree file
with open(toc_file_path, 'w', encoding='utf-8') as toctree_file:
        toctree_file.write(f"""

Accert Code Reference
==========================
This section provides detailed information on the Accert codebase. The Accert codebase is divided into two main sections: the main Accert class and utility functions. The main Accert class contains the main functions and methods for the Accert model, while the utility functions contain helper functions for the Accert model.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

Accert Class 
--------------------

.. autosummary::
   :toctree: main/
   :template: function.rst
                         
                             
""")
# Step 2: Read the Main class file in ../src/Main.py use absoulte path
main_class_file_path = os.path.join(current_dir, '../..', 'src', 'Main.py')
# give absolute path to open the file
main_class_file_path = os.path.abspath(main_class_file_path)
with open(main_class_file_path, 'r') as main_class_file:
    main_class_content = main_class_file.read()
    # Step 3: Parse the Main class file to get all the methods
    # Use regex to find all methods in the class
    method_names = re.findall(r'def (\w+)\(', main_class_content)
    print(f'Found methods in Main class: {method_names}, at folder: {main_class_file_path}')
    # Step 4: Add methods to the Toctree with Main.Accert. at the beginning
    for method_name in method_names:
        with open(toc_file_path, 'a', encoding='utf-8') as toctree_file:
            toctree_file.write(f'   Main.Accert.{method_name}\n')
    # Step 5: Add Utility Functions to the Toctree
    with open(toc_file_path, 'a', encoding='utf-8') as toctree_file:
        toctree_file.write(f"""
                           
Accert Utility Functions
--------------------------
.. autosummary::
   :toctree: utility/
   :template: function.rst
                                
""")
    print('Adding Utility Functions to the Toctree')
# Step 6: Parse the utility functions file in ../src/utility_accert.py    
utility_functions_file_path = os.path.join(current_dir, '../..', 'src', 'utility_accert.py')
with open(utility_functions_file_path, 'r') as utility_functions_file:
    utility_functions_content = utility_functions_file.read()
    # Step 7: Parse the utility functions file to get all the functions
    # Use regex to find all functions in the file
    function_names = re.findall(r'def (\w+)\(', utility_functions_content)
    print(f'Found functions in utility functions file: {function_names}')
    # Step 8: Add functions to the Toctree with Main.Utility_Functions. at the beginning
    for function_name in function_names:
        with open(toc_file_path, 'a', encoding='utf-8') as toctree_file:
            toctree_file.write(f'   utility_accert.Utility_methods.{function_name}\n')

    #end of the script
